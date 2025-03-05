#include <stdio.h>
#include <stdint.h>
#include <signal.h>
// unix only
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/termios.h>
#include <sys/mman.h>

// Instruction set documentation: https://www.cs.colostate.edu/~cs270/.Spring23/resources/PattPatelAppA.pdf
// Online Assembler: https://wchargin.com/lc3web/
//

// Memory
#define MEMORY_MAX (1 << 16)
uint16_t memory[MEMORY_MAX]; // 65536 locations of 16-bit each

// Registers
enum {
  R_R0 = 0,
  R_R1,
  R_R2,
  R_R3,
  R_R4,
  R_R5,
  R_R6,
  R_R7,
  R_PC, // program counter
  R_COND,
  R_COUNT
};
uint16_t reg[R_COUNT];

// Opcodes
enum {
  OP_BR = 0, // branch
  OP_ADD,    // add 
  OP_LD,     // load
  OP_ST,     // store
  OP_JSR,    // jump register
  OP_AND,    // bitwise and
  OP_LDR,    // load register
  OP_STR,    // store register
  OP_RTI,    // unused
  OP_NOT,    // bitwise not
  OP_LDI,    // load indirect
  OP_STI,    // store indirect
  OP_JMP,    // jump
  OP_RES,    // reserved (unused)
  OP_LEA,    // load effective address
  OP_TRAP    // execute trap
};

// Condition flags
enum {
  FL_POS = 1 << 0, // Positive
  FL_ZRO = 1 << 1, // Zero
  FL_NEG = 1 << 2, // Negative
};


// Trap Codes
enum {
  TRAP_GETC = 0x20,  // get character from keyboard, not echoed onto the terminal
  TRAP_OUT = 0x21,   // output a character
  TRAP_PUTS = 0x22,  // output a word string
  TRAP_IN = 0x23,    // get character from keyboard, echoed onto the terminal
  TRAP_PUTSP = 0x24, // output a byte string
  TRAP_HALT = 0x25   // halt the program
};

// Memory Mapped Registers
enum {
  MR_KBSR = 0xFE00, // keyboard status
  MR_KBDR = 0xFE02  // keyboard data
};

struct termios original_tio;

void disable_input_buffering() {
  tcgetattr(STDIN_FILENO, &original_tio);
  struct termios new_tio = original_tio;
  new_tio.c_lflag &= ~ICANON & ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &new_tio);
}

void restore_input_buffering() {
  tcsetattr(STDIN_FILENO, TCSANOW, &original_tio);
}

uint16_t check_key() {
  fd_set readfds;
  FD_ZERO(&readfds);
  FD_SET(STDIN_FILENO, &readfds);

  struct timeval timeout;
  timeout.tv_sec = 0;
  timeout.tv_usec = 0;
  return select(1, &readfds, NULL, NULL, &timeout) != 0;
};

void handle_interrupt(int signal) {
  restore_input_buffering();
  printf("\n");
  exit(-2);
}

uint16_t sign_extend(uint16_t x, int bit_count) {
  if ((x >> (bit_count - 1)) & 1) {
      x |= (0xFFFF << bit_count);
  }
  return x;
}

uint16_t swap16(uint16_t x) {
  return (x << 8) | (x >> 8);
}

void update_flags(uint16_t r) {
  if (reg[r] == 0) {
    reg[R_COND] = FL_ZRO;
  }
  else if (reg[r] >> 15) {
    // A 1 at left-most position indicates negative number.
    reg[R_COND] = FL_NEG;
  }
  else {
    reg[R_COND] = FL_POS;
  }
}

void read_image_file(FILE* file) {
  // The origin tells us where in memory to place the image.
  uint16_t origin;
  fread(&origin, sizeof(origin), 1, file);
  origin = swap16(origin);

  // We know the maximum file size, so we only need 1 fread.
  uint16_t max_read = MEMORY_MAX - origin;
  uint16_t* p = memory + origin;
  size_t read = fread(p, sizeof(uint16_t), max_read, file);

  // Swap to little endian.
  while (read-- > 0) {
    *p = swap16(*p);
    ++p;
  }
}

int read_image(const char* image_path) {
    FILE* file = fopen(image_path, "rb");
    if (!file) { return 0; };
    read_image_file(file);
    fclose(file);
    return 1;
}

void mem_write(uint16_t address, uint16_t value) {
  memory[address] = value;
}

uint16_t mem_read(uint16_t address) {
  if (address == MR_KBSR) {
    if (check_key()) {
      memory[MR_KBSR] = (1 << 15);
      memory[MR_KBDR] = getchar();
    }
    else {
      memory[MR_KBSR] = 0;
    }
  }
  return memory[address];
}

char* intToBinary(uint16_t num) {
  char* binaryStr;
  binaryStr=malloc(17);
  
  for (int i = 15; i >= 0; i--) {
    int bit = (num >> i) & 1;
    if (bit) binaryStr[i] = '1';
    else binaryStr[i] = '0';
  }
  return binaryStr;
}

int main(int argc, const char* argv[]) {
  if (argc < 2) {
    // Show usage string
    //
    printf("LC3 [image-file1] ...\n");
    exit(2);
  }
  for (int j = 1; j < argc; ++j) {
    if (!read_image(argv[j])) {
        printf("Failed to load image: %s\n", argv[j]);
        exit(1);
    }
  }
  
  signal(SIGINT, handle_interrupt);
  disable_input_buffering();

  // One Flag needs to be set at any time.
  // therefore we're setting the Z flag.
  //
  reg[R_COND] = FL_ZRO;

  // Set the PC register to starting position.
  // 0x3000 is the default.
  //
  enum { PC_START = 0x3000 };
  reg[R_PC] = PC_START;

  int running = 1;
  while(running) {
    // Fetch
    //
    uint16_t instr = mem_read(reg[R_PC]++);

    // The instructions are composed of 16 bits.
    // The left-most 4 bits represent the op code (up to 16 codes)
    //
    uint16_t op = instr >> 12;

    // char* rpcStr = intToBinary(reg[R_PC]-1);
    // char* instrStr = intToBinary(instr);
    // printf("r_pc: %s ; opcode: %d ; instr: %s\n", rpcStr, op, instrStr);
    // printf("R0: %d ; R1: %d ; R2: %d ; R3: %d ; R4: %d ; R5: %d ; R6: %d ; R7: %d\n", reg[R_R0], reg[R_R1], reg[R_R2], reg[R_R3], reg[R_R4], reg[R_R5], reg[R_R6],reg[R_R7]);
    // printf("Str[0]: %d\n", memory[12309]);
    // printf("mem[1]: %d\n", memory[1]);
    fflush(stdout);

    switch(op) {
      case OP_ADD:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8   6 5  5 4 3 2    0
        // |op code|r_dest|reg.1|mode|00 |reg.2|
        // |0001   |xxx   |xxx  |0   |00 |xxx  |
        //
        // 15    12 11   9 8   6 5  5 4        0
        // |op code|r_dest|reg.1|mode|immed_val|
        // |0001   |xxx   |xxx  |1   |xxxxx    |
        //
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t reg1 = (instr >> 6) & 0x7;
        uint16_t mode = (instr >> 5) & 0x1;

        if (mode) {
          uint16_t imm = sign_extend(instr & 0x1F, 5);
          reg[dest] = reg[reg1] + imm;
        } else {
          uint16_t reg2 = instr & 0x7;
          reg[dest] = reg[reg1] + reg[reg2];
        }
        update_flags(dest);
        break;
      }
      case OP_AND:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8   6 5  5 4 3 2    0
        // |op code|r_dest|reg.1|mode|00 |reg.2|
        // |0001   |xxx   |xxx  |0   |00 |xxx  |
        //
        // 15    12 11   9 8   6 5  5 4        0
        // |op code|r_dest|reg.1|mode|immed_val|
        // |0001   |xxx   |xxx  |1   |xxxxx    |
        //
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t reg1 = (instr >> 6) & 0x7;
        uint16_t mode = (instr >> 5) & 0x1;

        if (mode) {
          uint16_t imm = sign_extend(instr & 0x1F, 5);
          reg[dest] = reg[reg1] & imm;
        } else {
          uint16_t reg2 = instr & 0x7;
          reg[dest] = reg[reg1] & reg[reg2];
        }
        update_flags(dest);
        break;
      }
      case OP_NOT:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8   6 5  5 4        0
        // |op code|r_dest|reg.1|1   |11111    |
        // |0001   |xxx   |xxx  |1   |11111    |
        //
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t reg1 = (instr >> 6) & 0x7;
        
        reg[dest] = ~reg[reg1];
        update_flags(dest);
        break;
      }
      case OP_BR:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12  11  10  9                      0
        // |op code| n | z | p |PC offset           |
        // |0000   | x | x | x |xxxxxxxxx           |
        //
        uint16_t cond_flag = (instr >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);
        
        if (cond_flag & reg[R_COND]) {
          reg[R_PC] += pc_offset;
        }
        break;
      }
      case OP_JMP: // RET
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11  9 8    6 5             0
        // |op code|000  |Base R|000000        |
        // |1100   |000  |xxx   |000000        |
        //
        uint16_t base_reg = (instr >> 6) & 0x7;
        reg[R_PC] = reg[base_reg];
        break;
      }
      case OP_JSR:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11  11 10                  0
        // |op code|l_flag|PC offser           |
        // |0100   |1     |xxxxxxxxxxx         |
        //
        // 15    12 11  11    8    6 5         0
        // |op code|l_flag|00|Base R|000000    |
        // |0100   |0     |00|xxx   |000000    |
        //
        reg[R_R7] = reg[R_PC]; // Address for JMP/RET (return to)
        uint16_t long_flag = (instr >> 11) & 1;

        if (long_flag) {
          uint16_t long_pc_offset = sign_extend(instr & 0x7FF, 11);
          reg[R_PC] += long_pc_offset;
        }
        else {
          uint16_t base_reg = (instr >> 6) & 0x7;
          reg[R_PC] = reg[base_reg];
        }
        break;
      }
      case OP_LD:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8                   0
        // |op code|r_dest|PC offset           |
        // |0001   |xxx   |xxxxxxxxx           |
        // 
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);

        reg[dest] = mem_read(reg[R_PC] + pc_offset);
        update_flags(dest); 
        break;
      }
      case OP_LDI:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8                   0
        // |op code|r_dest|PC offset           |
        // |0001   |xxx   |xxxxxxxxx           |
        //
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);

        reg[dest] = mem_read(mem_read(reg[R_PC] + pc_offset));
        update_flags(dest); 
        break;
      }
      case OP_LDR:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8    6 5            0
        // |op code|r_dest|Base R|PC offset    |
        // |0110   |xxx   |xxx   |xxxxxx       |
        //
        uint16_t dest = (instr >> 9) & 0x7;
        uint16_t base_reg = (instr >> 6) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x3F, 6);

        reg[dest] = mem_read(reg[base_reg] + pc_offset);
        update_flags(dest); 
        break;
      }
      case OP_LEA:
        {
          // (16-bit instruction)
          // 15----------------------------------0
          //
          // 15    12 11   9 8                   0
          // |op code|r_dest|PC offset           |
          // |0001   |xxx   |xxxxxxxxx           |
          //
          uint16_t dest = (instr >> 9) & 0x7;
          uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);

          reg[dest] = reg[R_PC] + pc_offset;
          update_flags(dest); 
        }
        break;
      case OP_ST:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8                   0
        // |op code|reg. 1|PC offset           |
        // |0011   |xxx   |xxxxxxxxx           |
        //
        uint16_t reg1 = (instr >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);

        mem_write(reg[R_PC] + pc_offset, reg[reg1]);
        break;
      }
      case OP_STI:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8                   0
        // |op code|reg. 1|PC offset           |
        // |0011   |xxx   |xxxxxxxxx           |
        //
        uint16_t reg1 = (instr >> 9) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x1FF, 9);

        mem_write(mem_read(reg[R_PC] + pc_offset), reg[reg1]);
        break;
      }
      case OP_STR:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11   9 8    6 5            0
        // |op code|reg. 1|Base R|PC offset    |
        // |0011   |xxx   |xxx   |xxxxxx       |
        //
        uint16_t reg1 = (instr >> 9) & 0x7;
        uint16_t base_reg = (instr >> 6) & 0x7;
        uint16_t pc_offset = sign_extend(instr & 0x3F, 6);

        mem_write(reg[base_reg] + pc_offset, reg[reg1]);
        break;
      }
      case OP_TRAP:
      {
        // (16-bit instruction)
        // 15----------------------------------0
        //
        // 15    12 11 8 7                     0
        // |op code|0000|trapvect              |
        // |1111   |xxx |xxxxxxx               |
        //
        reg[R_R7] = reg[R_PC];

        switch (instr & 0xFF)
        {
          case TRAP_GETC:
            {
              reg[R_R0] = (uint16_t)getchar();
              update_flags(R_R0);
            }
            break;
          case TRAP_OUT:
            {
              putc((char)reg[R_R0], stdout);
              fflush(stdout);
            }
            break;
          case TRAP_PUTS:
            {
              uint16_t* c = memory + reg[R_R0];
              while (*c) {
                putc((char)*c, stdout);
                ++c;
              }
              fflush(stdout);
            }
            break;
          case TRAP_IN:
            {
              printf("Enter a character: ");
              char c = getchar();
              putc(c, stdout);
              fflush(stdout);
              reg[R_R0] = (uint16_t)c;
              update_flags(R_R0);
            }
            break;
          case TRAP_PUTSP:
            {
              u_int16_t* c = memory + reg[R_R0];
              while (*c) {
                char char1 = (*c) & 0xFF;
                putc(char1, stdout);
                char char2 = (*c) >> 8;
                if (char2) putc(char2, stdout);
                ++c;
              }
              fflush(stdout);
            }
            break;
          case TRAP_HALT:
            {
              puts("\n----- Halting LC3 processor -----\n");
              fflush(stdout);
              running = 0;
            }
            break;
        }
        break;
      }
      case OP_RES:
        abort();
        break;
      case OP_RTI:
        abort();
        break;
      default:
        abort();
        break;
    }
  }

  restore_input_buffering();
}

