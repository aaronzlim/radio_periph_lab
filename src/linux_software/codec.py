"""API to control the audio codec over I2C"""

from argparse import ArgumentParser
import contextlib
import mmap
import os
from time import sleep

import axi_iic as iic

ENDIAN : str = "little"

IIC_BASE_ADDR       : int = 0x4160_0000

CODEC_DEV_ADDR      : int = 0x1A # 0b0001_1010

CODEC_LEFT_ADC_VOLUME_REG    : int = 0x00
CODEC_RIGHT_ADC_VOLUME_REG   : int = 0x01
CODEC_LEFT_DAC_VOLUME_REG    : int = 0x02
CODEC_RIGHT_DAC_VOLUME_REG   : int = 0x03
CODEC_ANALOG_AUDIO_PATH_REG  : int = 0x04
CODEC_DIGITAL_AUDIO_PATH_REG : int = 0x05
CODEC_POWER_MANAGEMENT_REG   : int = 0x06
CODEC_DIGITAL_AUDIO_IF_REG   : int = 0x07
CODEC_SAMPLING_RATE_REG      : int = 0x08
CODEC_ACTIVE_REG             : int = 0x09
CODEC_SOFTWARE_RESET_REG     : int = 0x0F
CODEC_ALC_CONTROL_1_REG      : int = 0x10
CODEC_ALC_CONTROL_2_REG      : int = 0x11
CODEC_NOISE_GATE_REG         : int = 0x12


@contextlib.contextmanager
def osopen(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


def int2hex(d: int, pad: int = 2):
    return '0x' + hex(d)[2:].zfill(pad)


def int2bin(d: int, pad: int = 8):
    return '0b' + bin(d)[2:].zfill(pad)


def write_reg(reg: int, val: int) -> None:
    """Write to a codec register via the AXI_IIC IP."""
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, iic.IIC_SIZE, offset=IIC_BASE_ADDR)
        axi_iic_registers = iic.AxiIicRegister.from_buffer(axi_iic_mm)
        while (not iic.tx_fifo_empty(IIC_BASE_ADDR)) or iic.bus_busy(IIC_BASE_ADDR):
            sleep(0.001)
        axi_iic_registers.tx_fifo = iic.IIC_DYNAMIC_START | (CODEC_DEV_ADDR << 1)
        axi_iic_registers.tx_fifo = (reg << 1) | (val >> 9)
        axi_iic_registers.tx_fifo = iic.IIC_DYNAMIC_STOP | (val & 0xFF)


def read_reg(reg: int, num_bytes: int = 2) -> list:
    """Read from a codec register via the AXI_IIC IP."""
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, iic.IIC_SIZE, offset=IIC_BASE_ADDR)
        axi_iic_registers = iic.AxiIicRegister.from_buffer(axi_iic_mm)
        while not iic.tx_fifo_empty(IIC_BASE_ADDR) or not iic.rx_fifo_empty(IIC_BASE_ADDR) or iic.bus_busy(IIC_BASE_ADDR):
            sleep(0.001)
        axi_iic_registers.tx_fifo = iic.IIC_DYNAMIC_START | (CODEC_DEV_ADDR <<1)
        axi_iic_registers.tx_fifo = (reg << 1)
        axi_iic_registers.tx_fifo = iic.IIC_DYNAMIC_START | (CODEC_DEV_ADDR <<1) | 0x1
        axi_iic_registers.tx_fifo = iic.IIC_DYNAMIC_STOP | num_bytes
        while iic.rx_fifo_empty(IIC_BASE_ADDR):
            sleep(0.001)
        rx_data = []
        while not iic.rx_fifo_empty(IIC_BASE_ADDR):
            rx_data.append(axi_iic_registers.rx_fifo)

    return rx_data


def set_volume(v: int):
    if v not in range(10):
        print('Invalid volumd {v}. Must be in range [0,9]')
        return
    v = v*6 + 47
    write_reg(CODEC_LEFT_DAC_VOLUME_REG, v)
    write_reg(CODEC_RIGHT_DAC_VOLUME_REG, v)


def configure_codec():
    write_reg(CODEC_SOFTWARE_RESET_REG, 0x00)
    sleep(0.001)
    write_reg(CODEC_POWER_MANAGEMENT_REG, 0x37)
    write_reg(CODEC_POWER_MANAGEMENT_REG,0x37)
    write_reg(CODEC_LEFT_ADC_VOLUME_REG,0x80)
    write_reg(CODEC_RIGHT_ADC_VOLUME_REG,0x80)
    write_reg(CODEC_LEFT_DAC_VOLUME_REG,0x47)
    write_reg(CODEC_RIGHT_DAC_VOLUME_REG,0x47)
    write_reg(CODEC_ANALOG_AUDIO_PATH_REG,0x10)
    write_reg(CODEC_DIGITAL_AUDIO_PATH_REG,0x00)
    write_reg(CODEC_DIGITAL_AUDIO_IF_REG,0x02)
    write_reg(CODEC_SAMPLING_RATE_REG,0x00)
    sleep(0.075)
    write_reg(CODEC_POWER_MANAGEMENT_REG,0x27)
    sleep(0.075)
    write_reg(CODEC_ACTIVE_REG,0x01)


def dump():
    raise Exception('Not Implemented')


def main(args):
    iic.axi_iic_init(IIC_BASE_ADDR)

    if args.init:
        configure_codec()

    if args.volume is not None:
        print(f'Setting volume to level {args.volume}/9')
        set_volume(args.volume)

    if args.read_write is None:
        return

    if args.read_write.lower().startswith("r"):
        print(f'Reading register {int2hex(args.register,2)}')
        read_data = read_reg(args.register, args.data) if args.data > 0 else []
        print([int2hex(data) for data in read_data])

    elif args.read_write.lower().startswith("w"):
        print(f'Writing {int2hex(args.data,2)} to register {int2hex(args.register,2)}')
        write_reg(args.register, args.data)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--init',
        action='store_true',
        help="initialize the codec."
    )
    parser.add_argument(
        '--dump',
        action='store_true',
        help="Dump all codec registers."
    )
    parser.add_argument(
        'read_write',
        nargs='?',
        choices=("read", "r", "rd", "write", "w", "wr"),
        help="Specifies a read or write access",
    )
    parser.add_argument(
        'register',
        nargs='?',
        default='0x00',
        help="Register to access.",
    )
    parser.add_argument(
        'data',
        nargs='?',
        default='0x00',
        help="If writing, the data to write. If reading, the number of bytes to read.",
    )
    parser.add_argument(
        '--volume',
        type=int,
        choices=(0,1,2,3,4,5,6,7,8,9),
        help='If provided, sets the DAC volume to this level. Must be between 0 and 9.'
    )
    args = parser.parse_args()

    if isinstance(args.register, str):
        args.register = int(args.register, 16)
    if isinstance(args.data, str):
        args.data = int(args.data,16)

    main(args)
