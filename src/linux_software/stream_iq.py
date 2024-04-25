"""Stream IQ data from our SDR over UDP"""

from argparse import ArgumentParser
from contextlib import contextmanager
from ctypes import Structure, c_uint32
from mmap import mmap
import os
import signal
import socket


IQ_FIFO_BASE_ADDR: int = 0x43C1_0000
IQ_FIFO_SIZE: int = 0x0000_0010
BYTES_PER_SAMPLE: int = 4


class SignalHandler:
    def __init__(self):
        signal.signal(signal.SIGINT, self.catch)
        signal.signal(signal.SIGTERM, self.catch)
        self._kill = False

    def catch(self, a, b):
        self._kill = True

    def reset(self):
        self._kill = False

    @property
    def kill(self):
        return self._kill


@contextmanager
def osopen(*args, **kwargs):
    fd = os.open(*args, **kwargs)
    try:
        yield fd
    finally:
        os.close(fd)


class Axi4sFifo(Structure):
    _fields_ = [
        ("fifo_empty",    c_uint32),
        ("fifo_data",     c_uint32),
        ("fifo_overflow", c_uint32),
        ("reserved1",     c_uint32),
    ]


def main(args):
    signal_handler = SignalHandler()
    print(f'Sending {args.endian} endian IQ stream to {args.ip} at port {args.port}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    pkt_ctr = 0
    msg = bytearray(args.samples_per_packet*BYTES_PER_SAMPLE+2) # +2 for pkt count
    with osopen('/dev/mem', os.O_RDWR) as fd:
        mm = mmap(fd, IQ_FIFO_SIZE, offset=IQ_FIFO_BASE_ADDR)
        reg = Axi4sFifo.from_buffer(mm)
        while not signal_handler.kill:
            msg[0:2] = int.to_bytes(pkt_ctr, 2, args.endian)
            for k in range(args.samples_per_packet):
                while reg.fifo_empty:
                    pass
                msg[k*BYTES_PER_SAMPLE+2 : (k+1)*BYTES_PER_SAMPLE+2] = int.to_bytes(reg.fifo_data, BYTES_PER_SAMPLE, args.endian)
            sock.sendto(msg, (args.ip, args.port))
            pkt_ctr = (pkt_ctr + 1) % 65535 # 16-bit rollover
    print(' ')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-i', '--ip',
        type=str,
        default='127.0.0.1',
        help='IP address to stream to. Defaults to 127.0.0.1'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=25344,
        help='Port to stream to. Defaults to 25344.'
    )
    parser.add_argument(
        '-s', '--samples-per-packet',
        type=int,
        default=256,
        help="Number of complex samples sent per UDP packet. Defaults to 256."
    )
    parser.add_argument(
        '-e', '--endian',
        type=str,
        default='little',
        choices=('big', 'little'),
        help='Endianness of the UDP payload. Defaults to little.'
    )
    args = parser.parse_args()

    main(args)
