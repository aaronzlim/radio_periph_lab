"""Stream IQ data from our SDR to a file."""

from argparse import ArgumentParser
from contextlib import contextmanager
from ctypes import Structure, c_uint32
from mmap import mmap
import os
import signal


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
    msg = bytearray(args.samples_per_packet*BYTES_PER_SAMPLE)
    print(f'Writing {args.endian} endian IQ samples to debug.bin in {args.samples_per_packet} sample chunks.')
    samples_collected = 0
    with osopen('/dev/mem', os.O_RDWR) as devmem:
        mm = mmap(devmem, IQ_FIFO_SIZE, offset=IQ_FIFO_BASE_ADDR)
        reg = Axi4sFifo.from_buffer(mm)
        with open('debug.bin', 'wb') as dbg_file:
            while not signal_handler.kill:
                for k in range(args.samples_per_packet):
                    while reg.fifo_empty:
                        pass
                    msg[k*BYTES_PER_SAMPLE : (k+1)*BYTES_PER_SAMPLE] = int.to_bytes(reg.fifo_data, BYTES_PER_SAMPLE, args.endian)
                dbg_file.write(msg)
                if args.length > 0:
                    samples_collected += args.samples_per_packet
                    if samples_collected >= args.length:
                        break

    print(' ')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-s', '--samples-per-packet',
        type=int,
        default=256,
        help="Number of complex samples buffered before writing to file. Defaults to 256."
    )
    parser.add_argument(
        '-e', '--endian',
        type=str,
        default='little',
        choices=('big', 'little'),
        help='Endianness of the payload. Defaults to little.'
    )
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=0,
        help='Length of file in number of complex samples. Defaults to 0 (continuous stream).'
    )
    args = parser.parse_args()

    main(args)
