from contextlib import contextmanager
from ctypes import Structure, c_uint32
from mmap import mmap
import os

import codec


RADIO_BASE_ADDR : int = 0x43C0_0000
RADIO_SIZE      : int = 0x0000_0010
DDS_PHASE_WIDTH : int = 27
SAMPLE_RATE_HZ  : float = 125e6

HELP_TEXT = """
---------------------------------------------------------------------------------------------------
-- Welcome to the Radio Peripheral System
--
-- Author: Aaron Lim
--
-- Commands
--   tone  <freq_hz>    : Set the fake ADC to a frequency between 1 Hz and 125_000_000 Hz.
--   tune  <freq_hz>    : Tune the radio to a frequency between.
--   reset <true_false> : When true, holds the radio in reset.
--   timer              : Get the current hardware time (free running counter).
--   benchmark          : Test read speed.
--   status             : Read all registers.
--   exit               : Exit the program.
---------------------------------------------------------------------------------------------------
"""


class RadioRegisters(Structure):
    """Controls for our radio peripheral"""
    _fields_ = [
        ("adc_phase_incr", c_uint32), # Fake ADC DDS phase increment
        ("ddc_phase_incr", c_uint32), # Digital downconverter DDS phase increment
        ("reset",          c_uint32), # DDS reset
        ("timer",          c_uint32), # 32-bit free-running counter
    ]


@contextmanager
def open_radio():
    try:
        fd = os.open('/dev/mem', os.O_RDWR)
        reg = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
        yield reg
    finally:
        os.close(fd)


def benchmark():
    fd = os.open('/dev/mem', os.O_RDWR)
    radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
    start_time = radio.timer
    for _ in range(2048):
        stop_time = radio.timer
    os.close(fd)
    
    elapsed_time = stop_time - start_time
    if elapsed_time < 0:
        elapsed_time += 4294967296 # 2^32
    elapsed_time /= SAMPLE_RATE_HZ # convert ticks to seconds
    bytes_transferred = (2048*32)/8 # 2048 32-bit words with 8 bits per byte
    throughput = float(bytes_transferred) / (elapsed_time*1e6) # convert to MB/s
    print(f'You transferred {bytes_transferred} bytes of data in {elapsed_time} seconds')
    print(f'Measured transfer throughput = {throughput} Mbytes/sec')


def ui():
    print(HELP_TEXT)
    while True:
        inp = input('> ').lower().split(' ')
        if len(inp) == 0:
            cmd = ''
            arg = ''
        elif len(inp) == 1:
            cmd = inp[0]
            arg = ''
        else:
            cmd = inp[0]
            arg = inp[1]

        if cmd == 'help':
            print(HELP_TEXT)

        elif cmd == 'tone':
            try:
                freq_hz = float(arg)
                if freq_hz < 0 or freq_hz > 125_000_000:
                    print(f'Invalid tone frequency {freq_hz}. Must be between 0 and {SAMPLE_RATE_HZ}.')
                    continue
                phase_incr = round((freq_hz / SAMPLE_RATE_HZ) * 2**DDS_PHASE_WIDTH)
                print(f'Setting tone to {freq_hz} Hz (phase increment {phase_incr})')
                fd = os.open('/dev/mem', os.O_RDWR)
                radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
                radio.adc_phase_incr = phase_incr
            except Exception as e:
                print(e)
            finally:
                os.close(fd)

        elif cmd == 'tune':
            try:
                freq_hz = float(arg)
                if freq_hz < 0 or freq_hz > 62.5e6:
                    print(f'Invalid tune frequency {freq_hz}. Must be between 0 and {SAMPLE_RATE_HZ/2}.')
                    continue
                freq_hz = SAMPLE_RATE_HZ - freq_hz
                phase_incr = round((freq_hz / SAMPLE_RATE_HZ) * 2**DDS_PHASE_WIDTH)
                print(f'Tuning to {SAMPLE_RATE_HZ-freq_hz} Hz (phase increment {phase_incr})')
                fd = os.open('/dev/mem', os.O_RDWR)
                radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
                radio.ddc_phase_incr = phase_incr
            except Exception as e:
                print(e)
            finally:
                os.close(fd)

        elif cmd == 'reset':
            if arg not in ("true", "false"):
                print(f"Command reset requires argument true or false. Given {arg}.")
                continue
            fd = os.open('/dev/mem', os.O_RDWR)
            radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
            radio.reset = 1 if arg == "true" else 0
            print(f'Reset Register: {radio.reset}')
            os.close(fd)

        elif cmd == 'timer':
            fd = os.open('/dev/mem', os.O_RDWR)
            radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
            print(f'Timer: {radio.timer}')
            os.close(fd)

        elif cmd == 'benchmark':
            benchmark()

        elif cmd == 'status':
            fd = os.open('/dev/mem', os.O_RDWR)
            radio = RadioRegisters.from_buffer(mmap(fd, RADIO_SIZE, offset=RADIO_BASE_ADDR))
            print(f'ADC Phase Increment: {radio.adc_phase_incr}')
            print(f'DDC Phase Increment: {radio.ddc_phase_incr}')
            print(f'Reset              : {radio.reset}')
            print(f'Timer              : {radio.timer}')
            os.close(fd)

        elif cmd == 'exit':
            break

        else:
            print(f'Unknown command {cmd}. Enter "help" for a list of valid commands.')


if __name__ == '__main__':
    codec_on = codec.read_reg(codec.CODEC_ACTIVE_REG)[0]
    if not codec_on:
        codec.configure_codec()

    ui()
