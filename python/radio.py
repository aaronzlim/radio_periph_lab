from ctypes import Structure, c_uint32

import codec


RADIO_BASE_ADDR : int = 0x43C0_0000
RADIO_SIZE      : int = 0x0000_0004


class RadioRegister(Structure):
    """Controls for our radio peripheral"""
    _fields_ = [
        ("adc_phase_incr", c_uint32), # Fake ADC DDS phase increment
        ("ddc_phase_incr", c_uint32), # Digital downconverter DDS phase increment
        ("reset",          c_uint32), # DDS reset
        ("timer",          c_uint32), # 32-bit free-running counter
    ]


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
--   exit               : Exit the program.
---------------------------------------------------------------------------------------------------
"""


def ui():
    print(HELP_TEXT)
    while True:
        pass # TODO: FINISH ME



if __name__ == '__main__':
    codec_on = int(codec.read_reg(codec.CODEC_ACTIVE_REG)[0],16)
    if not codec_on:
        codec.configure_codec()

    ui()
