from contextlib import contextmanager
from ctypes import Structure, c_uint32
import axi_iic as iic
from mmap import mmap
import os
import signal
import subprocess
import sys
from time import sleep

import codec

IIC_BASE_ADDR: int = 0x4160_0000

RADIO_BASE_ADDR : int = 0x43C0_0000
RADIO_SIZE      : int = 0x0000_0010
DDS_PHASE_WIDTH : int = 27
CLOCK_RATE_HZ   : float = 125e6

IQ_FIFO_BASE_ADDR: int = 0x43C1_0000
IQ_FIFO_SIZE: int = 0x0000_0010
BYTES_PER_SAMPLE: int = 4
SAMPLES_PER_PACKET: int = 256
ENDIAN: str = 'little'

HELP_TEXT = """
-------------------------------------------------------------------------------
-- Welcome to the Radio Peripheral System
--
-- Author: Aaron Lim
--
-- Commands
--   tone   <freq_hz>         : Set the fake ADC to a frequency between 1
--                              Hz and 125_000_000 Hz.
--   u                        : Increase the tone frequency by 100 Hz.
--   U                        : Increase the tone frequency by 1000 Hz.
--   d                        : Decrease the tone frequency by 100 Hz.
--   D                        : Decrease the tone frequency by 1000 Hz.
--   tune   <freq_hz>         : Tune the radio to a frequency between 0 Hz
--                              and 62_500_000 Hz.
--   ip     <ipv4>            : Set the IP address for streaming. Defaults to
--                              127.0.0.1.
--   port   <port>            : Set the port number for streaming. Defaults to
--                              25344.
--   spp    <num>             : Number of samples per packet. Defaults to 256.
--   stream on | off          : Stream IQ data to the given IP and Port.
--                              Defaults to off.
--   volume up | down | [0-9] : Change the DAC volume.
--   reset  true | false      : When true, holds the radio in reset.
--   timer                    : Get the current hardware time
--                              (free running counter).
--   status                   : Show status of radio registers and IQ stream.
--                              Note the FIFO Overflow register clears on read.
--   exit                     : Exit the program.
--
-- Note that if any of the streaming parameters change, the stream does not
-- automatically update. You must turn off the stream and turn it back on
-- for the new settings to take effect.
-------------------------------------------------------------------------------
"""


class SignalHandler:
    """Flags SIGINT and SIGTERM events."""
    def __init__(self):
        self._kill: bool = False
        signal.signal(signal.SIGINT, self.catch)
        signal.signal(signal.SIGTERM, self.catch)

    def catch(self, a, b):
        self._kill = True

    def reset(self):
        self._kill = False

    @property
    def kill(self):
        return self._kill


class RadioRegisters(Structure):
    """Controls for our radio peripheral"""
    _fields_ = [
        ("adc_phase_incr", c_uint32), # Fake ADC DDS phase increment
        ("ddc_phase_incr", c_uint32), # Digital downconverter DDS phase increment
        ("reset",          c_uint32), # DDS reset
        ("timer",          c_uint32), # 32-bit free-running counter
    ]


@contextmanager
def osopen(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


def cmd_tone(arg: str) -> int:
    try:
        freq_hz = float(arg)
        if freq_hz < 0 or freq_hz > 125_000_000:
            print(f'Invalid tone frequency {freq_hz}. Must be between 0 and {CLOCK_RATE_HZ}.')
            return 1
        phase_incr = round((freq_hz / CLOCK_RATE_HZ) * 2**DDS_PHASE_WIDTH)
        print(f'Setting tone to {freq_hz} Hz (phase increment {phase_incr})')
        with osopen('/dev/mem', os.O_RDWR) as fd:
            radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
            radio.adc_phase_incr = phase_incr
    except Exception as e:
        print(e)

    return 0


def cmd_tune(arg: str) -> None:
    try:
        freq_hz = float(arg)
        if freq_hz < 0 or freq_hz > 62.5e6:
            print(f'Invalid tune frequency {freq_hz}. Must be between 0 and {CLOCK_RATE_HZ/2}.')
            return
        freq_hz = CLOCK_RATE_HZ - freq_hz
        phase_incr = round((freq_hz / CLOCK_RATE_HZ) * 2**DDS_PHASE_WIDTH)
        print(f'Tuning to {CLOCK_RATE_HZ-freq_hz} Hz (phase increment {phase_incr})')
        with osopen('/dev/mem', os.O_RDWR) as fd:
            radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
            radio.ddc_phase_incr = phase_incr
    except Exception as e:
        print(e)


def create_stream(ip: str, port: int, spp: int) -> subprocess.Popen:
    print(f'{sys.executable} stream_iq.py -i {ip} -p {port} -s {spp}')
    proc = subprocess.Popen([sys.executable, 'stream_iq.py',
                             '-i', f'{ip}',
                             '-p', f'{port}',
                             '-s', f'{spp}'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    return proc


def cmd_reset(arg: str) -> None:
    if arg not in ("true", "false"):
        print(f"Command reset requires argument true or false. Given {arg}.")
        return
    with osopen('/dev/mem', os.O_RDWR) as fd:
        radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        radio.reset = 1 if arg == "true" else 0
        print(f'Reset Register: {radio.reset}')


def cmd_timer() -> None:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        print(f'Timer: {radio.timer}')


def cmd_status() -> None:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        print(f'ADC Phase Increment: {radio.adc_phase_incr}')
        print(f'DDC Phase Increment: {radio.ddc_phase_incr}')
        print(f'Reset              : {radio.reset}')
        print(f'Timer              : {radio.timer}')

    with osopen('/dev/mem', os.O_RDWR) as fd:
        fifo = mmap(fd, IQ_FIFO_SIZE, offset=IQ_FIFO_BASE_ADDR)
        print(f'IQ FIFO Overflow   : {int.from_bytes(fifo[8:12], "little")}') # 3rd AXI4-L register


def get_tone_freq() -> float:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        return radio.adc_phase_incr * CLOCK_RATE_HZ / 2**DDS_PHASE_WIDTH


def get_tune_freq() -> float:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        return -1*((radio.ddc_phase_incr * CLOCK_RATE_HZ / 2**DDS_PHASE_WIDTH) - CLOCK_RATE_HZ)


def cmd_volume_up() -> None:
    v = codec.get_volume()
    if v < 9:
        codec.set_volume(v+1)


def cmd_volume_down() -> None:
    v = codec.get_volume()
    if v > 0:
        codec.set_volume(v-1)


def ui():
    print(HELP_TEXT)

    sig_handler: SignalHandler = SignalHandler()
    ip:str = '127.0.0.1'
    port: int = 25344
    spp: int = 256
    stream: subprocess.Popen = None
    stream_en: bool = False
    tone_freq: float = get_tone_freq()

    while not sig_handler.kill:
        inp = input('> ').split(' ')
        if len(inp) == 0:
            cmd = ''
            arg = ''
        elif len(inp) == 1:
            cmd = inp[0]
            arg = ''
        else:
            cmd = inp[0]
            arg = inp[1]

        cmdl = cmd.lower()
        argl = arg.lower()

        if cmdl == 'help':
            print(HELP_TEXT)
        elif cmdl == 'tone':
            if not cmd_tone(arg):
                tone_freq = int(arg)
            print(f'Tone Frequency: {get_tone_freq()} Hz')
        elif cmd == 'u':
            if tone_freq + 100 <= 125_000_000:
                tone_freq += 100
                cmd_tone(str(tone_freq))
            print(f'Tone Frequency: {get_tone_freq()} Hz')
        elif cmd == 'U':
            if tone_freq + 1000 <= 125_000_000:
                tone_freq += 1000
                cmd_tone(str(tone_freq))
            print(f'Tone Frequency: {get_tone_freq()} Hz')
        elif cmd == 'd':
            if tone_freq - 100 >= 0:
                tone_freq -= 100
                cmd_tone(str(tone_freq))
            print(f'Tone Frequency: {get_tone_freq()} Hz')
        elif cmd == 'D':
            if tone_freq - 1000 >= 0:
                tone_freq -= 1000
                cmd_tone(str(tone_freq))
            print(f'Tone Frequency: {get_tone_freq()} Hz')
        elif cmdl == 'tune':
            cmd_tune(arg)
            print(f'Tune Frequency: {get_tune_freq()} Hz')
        elif cmdl == 'ip':
            if len(arg) > 0:
                ip = arg
            print(f'IP set to {ip}')
        elif cmdl == 'port':
            try:
                port = int(arg)
                print(f'Port set to {port}')
            except:
                print(f'Unable to converter port {port} to an integer.')
        elif cmdl == 'spp':
            try:
                spp = int(arg)
            except:
                print(f'Unable to convert {arg} to int.')
            print(f'Samples per Packet: {spp}')
        elif cmdl == 'stream':
            if arg in ('off', 'on'):
                if stream_en:
                    stream.terminate()
                    stream_en = False
                if arg == "on":
                    stream = subprocess.Popen([sys.executable, 'stream_iq.py',
                             '-i', f'{ip}',
                             '-p', f'{port}',
                             '-s', f'{spp}'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
                    print(stream.pid)
                    stream_en = True
                if stream_en:
                    print(f'Streaming to {ip}:{port} using process id {stream.pid}')
                else:
                    print('Stream terminated.')
            else:
                print(f'Invalid stream command {arg}. Must be off or on.')
        elif cmdl == 'volume':
            if argl == 'up':
                cmd_volume_up()
            elif argl == 'down':
                cmd_volume_down()
            elif arg in [str(n) for n in range(10)]:
                codec.set_volume(int(arg))
            else:
                print('Invalid volume argument. Must be up, down, or 0-9.')
        elif cmdl == 'reset':
            cmd_reset(argl)
        elif cmdl == 'timer':
            cmd_timer()
        elif cmdl == 'status':
            print('Radio Peripheral Registers:')
            print('---------------------------')
            cmd_status()
            print(' ')
            print('Stream Status:')
            print('--------------')
            print(f'IP                 : {ip}')
            print(f'Port               : {port}')
            print(f'Sampler per Packet : {spp}')
            print(f'Stream             : {"on" if stream_en else "off"}')
            if stream_en:
                print(f'Stream PID         : {stream.pid}')
        elif cmdl == 'exit':
            break
        else:
            print(f'Unknown command {cmd}. Enter "help" for a list of valid commands.')

    if stream_en:
        print('Terminating IQ stream')
        stream.terminate()
    print('Done')


if __name__ == '__main__':
    iic.axi_iic_init(IIC_BASE_ADDR)
    codec.configure_codec()
    ui()
