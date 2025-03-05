# LC3 Project

This project aims to create an emulator and assembler for the LC3 (Light Computer 3)

# Emulator

The emulator is written in C for simplicity and performance, although this could be re-written
in a more modern language in the future.

## Usage

In the `emulator` directory you will find the `lc3-vm` executable which is the emulator, it takes
a `.obj` file (AKA image) that contains machine code to execute.

```bash
./lc3-vm file.obj

```

# Assembler

The Assembler is written in Python in order to have something working in a short amount
of time.

## Usage

In the `assembler` directory you will find the `assembler` executable which will assemble assembly code,
it takes a `.asm` file and will output a `.obj` file with the same prefix name (e.g `hello.asm` => `hello.obj`).

```bash
./assembler file.asm
```

# Images

The `images` directory will contain example assembly code (`.asm`) and their corresponding images (`.obj`)
for refencing and example purposes.
