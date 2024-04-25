# Radio Peripheral Example Project

Author: Aaron Lim

Hardware: Zybo Z7

Tool: Vivado 2023.2

## Description

An example radio peripheral project for the class _System On Chip FPGA Design Lab_ (EN.525.718) at
Johns Hopkins.

Generates a single complex sinusoid that gets mixed with an NCO, filtered, and decimated. Output is provided to the audio codec over I2S.

Design runs at 125 MHz and audio is delivered at 48.828125 kHz.

IQ (Left/Right) samples are available via an AXI4-L FIFO. An example Python app is provided to read data from the FIFO and stream to a host in UDP packets.

## Directory Structure

**ip_repo** : Packaged user IP

**src** : Various source files including top level VHDL, top level constraints, and c code to test the radio peripheral.

**tcl** : TCL scripts used to make and build the Vivado project.

**doug.bif** : Used to generate the FPGA bit.bin file.

**make_bitbinfile.bat** : Just regenerate the bit.bin.

**make_project.bat** : Generate the project, build it, export the hardware XSA, and generate the bit.bin.

**make_project.sh** : Same as make_project.bat but for linux.

## Linux Image

This project assumes you have already installed Linux onto the SD card of the board and can boot to it on startup. Having Python as part of the image is a plus.

## Building the Vivado Project

When building the project for the first time (i.e. there's no existing project), simply run the appropriate make_project.[bat,sh] script from the same directory that contains this README. If a project already exists, delete or move it before running the script.

To program the board, you will need the **design_1_wrapper.bit.bin** file at *vivado/radio_periph_lab/runs/impl_1/*

## Editing the project

If the project is updated and you need to re-export it as a TCL file, save that TCL file to the radio_periph_lab directory (that contains this README) so that file paths are relative to here. Then, copy that file to the *tcl* directory.

To rebuild the project without re-generating it (i.e. running implementation and bootgen), just comment out the first call to vivado in the make_project.[bat,sh] script.

## Networking with the Zybo

Connect to the board over serial (COM port) and run

```bash
ifconfig
```

to get the network information.

If connected to a router capable of DHCP an IP address should be assigned automatically and you just need to connect to the IP address of the board.

If the board does not automatically get an IP address, you need to assign one with:

```bash
ip addr 192.168.1.2/24 dev eth0
```

You can then set the specific network card interfacing with the Zybo to a static IP address on the 192.168.1.X network with a mask of 255.255.255.0 and the default gateway.

You should then be able to connect to the Zybo over ethernet at the IP address you assigned.

## Loading the FPGA image

You can drop the .bit.bin file onto the board via the SD card or over SCP using the ethernet connection. Once the .bit.bin file is on the board, run the following:

```bash
fpgautil -b <path_to_bitbin_file>
```

## User Software

Various user software is provided in **src/linux_software/** that can be manually dropped onto the board.

test_radio.c is a test program provided by the course instructor.

The Python files provide a Python API to interact with the audio codec and radio peripheral. All Python files should be placed in the same directory.
