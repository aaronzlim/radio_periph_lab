import contextlib
from ctypes import Structure, c_uint32
import mmap
import os
from time import sleep


IIC_SIZE          : int = 0x0001_0000
IIC_DYNAMIC_START : int = 0x0000_0100
IIC_DYNAMIC_STOP  : int = 0x0000_0200
IIC_TX_FIFO_EMPTY : int = 0b1000_0000
IIC_RX_FIFO_EMPTY : int = 0b0100_0000
IIC_BUS_BUSY      : int = 0b0000_0100


class AxiIicRegister(Structure):
    """AXI IIC that configures the codec."""
    _fields_ = [
        ("reserved1",    c_uint32*7),  # 0x000 - 0x018
        ("gie",          c_uint32),    # 0x01C global interrupt enable
        ("isr",          c_uint32),    # 0x020 interrupt status
        ("reserved2",    c_uint32),    # 0x024
        ("ier",          c_uint32),    # 0x028 interrupt enable
        ("reserved3",    c_uint32*5),  # 0x02C - 0x03c
        ("softr",        c_uint32),    # 0x040 soft reset
        ("reserved4",    c_uint32*47), # 0x044 - 0x0FC
        ("cr",           c_uint32),    # 0x100 control
        ("sr",           c_uint32),    # 0x104 status
        ("tx_fifo",      c_uint32),    # 0x108 tx fifo
        ("rx_fifo",      c_uint32),    # 0x10C rx fifo
        ("adr",          c_uint32),    # 0x110 slave address register
        ("tx_fifo_ocy",  c_uint32),    # 0x114 transmit fifo occupancy
        ("rx_fifo_ocy",  c_uint32),    # 0x118 receive fifo occupancy
        ("ten_adr",      c_uint32),    # 0x11C slave ten bit address
        ("rx_fifo_pirq", c_uint32),    # 0x120 receive fifo programmable depth interrupt
        ("gpo",          c_uint32),    # 0x124 general purpose output
        ("tsusta",       c_uint32),    # 0x128 timing parameters (from here and below)
        ("tsusto",       c_uint32),
        ("thdsta",       c_uint32),
        ("tsudat",       c_uint32),
        ("tbuf",         c_uint32),
        ("thigh",        c_uint32),
        ("tlow",         c_uint32),
        ("thddat",       c_uint32),    # 0x144
    ]


@contextlib.contextmanager
def osopen(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


def axi_iic_init(base_addr: int = 0) -> None:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, IIC_SIZE, offset=base_addr)
        axi_iic_registers = AxiIicRegister.from_buffer(axi_iic_mm)
        axi_iic_registers.cr = 0x2
        axi_iic_registers.rx_fifo_pirq = 0xF
        sleep(0.001)
        axi_iic_registers.cr = 0x1


def soft_reset(base_addr: int = 0) -> None:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, IIC_SIZE, offset=base_addr)
        axi_iic_registers = AxiIicRegister.from_buffer(axi_iic_mm)
        axi_iic_registers.softr = 0xA


def tx_fifo_empty(base_addr: int = 0) -> bool:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, IIC_SIZE, offset=base_addr)
        axi_iic_registers = AxiIicRegister.from_buffer(axi_iic_mm)
        tx_fifo_empty = (axi_iic_registers.sr & IIC_TX_FIFO_EMPTY) >> 7
    return bool(tx_fifo_empty)


def rx_fifo_empty(base_addr: int = 0) -> bool:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, IIC_SIZE, offset=base_addr)
        axi_iic_registers = AxiIicRegister.from_buffer(axi_iic_mm)
        rx_fifo_empty = (axi_iic_registers.sr & IIC_RX_FIFO_EMPTY) >> 6
    return bool(rx_fifo_empty)


def bus_busy(base_addr: int = 0) -> bool:
    with osopen('/dev/mem', os.O_RDWR) as fd:
        axi_iic_mm = mmap.mmap(fd, IIC_SIZE, offset=base_addr)
        axi_iic_registers = AxiIicRegister.from_buffer(axi_iic_mm)
        bus_busy = (axi_iic_registers.sr & IIC_BUS_BUSY) >> 2
    return bool(bus_busy)