const std = @import("std");
// const allocator = std.heap.page_allocator;

const Register = enum(u4) {
    R0 = 0,
    R1,
    R2,
    R3,
    R4,
    R5,
    R6,
    R7,
    PC, // program counter
    COND,
    COUNT,
};

const Operation = enum(u4) {
    BR = 0, // Branch
    ADD, // Add
    LD, // Load
    ST, // Store
    JST, // Jump Register
    AND, // Bitwise AND
    LDR, // Load Register
    STR, // Store Register
    RTI, // Unused
    NOT, // Bitwise NOT
    LDI, // Load Indirect
    STI, // Store Indirect
    JMP, // Jump
    RES, // reserved (unused)
    LEA, // Load Effective Address
    TRAP, // Execute Trap
};

// Condition Flags
//
const Flag = enum(i2) {
    NEG = -1, // Negative
    ZRO = 0, // Zero
    POS = 1, // Positive
};

const Trap = enum(u3) {
    GETC = 0x20, // Get character from keyboard, not echoed onto the terminal
    OUT, // Output a character
    PUTS, // Output a word string
    IN, // Get character from keyboard, echoed onto the terminal
    PUTSP, // Output a byte string
    HALT, // Halt the program
};

// Memory Mapped Registers
//
const MemoryRegister = enum(u1) {
    KBSR = 0xFE00, // Keyboard status
    KBDR = 0xFE02, // Keyboard data
};

// TODO: Revisit this bit
const MEMORY_MAX_SIZE = (1 << 16); // 65_536 locations of 16-bit each
const MEMORY_MAX_END = MEMORY_MAX_SIZE - 1;

const Instruction = packed struct {
    const Self = @This();
    opcode: u4,
    rest: u12,

    pub fn print(self: Self) void {
        std.debug.print("{b:04}{b:012}\n", .{ self.opcode, self.rest });
    }
};

var MEMORY = std.mem.zeroes([MEMORY_MAX_SIZE]Instruction);
var REGISTERS = std.mem.zeroes([Register.COUNT]Instruction);

// Swap to little endian
//
fn swap16(x: u16) u16 {
    return (x << 8) | (x >> 8);
}

fn read_image(file_path: []const u8) void {
    // var origin: u16 = 1;
    // origin = swap16(origin);

    const max_read = MEMORY_MAX_END;
    // const pointer = MEMORY;

    // Open file
    const file = std.fs.cwd().openFile(file_path, .{}) catch unreachable;
    defer file.close();

    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    const allocator = arena.allocator();
    defer arena.deinit();

    // Read file into buffer
    const file_size: u64 = file.getEndPos() catch unreachable;
    const buffer: []u8 = allocator.alloc(u8, file_size) catch unreachable;
    defer allocator.free(buffer);

    _ = file.readAll(buffer) catch unreachable;

    const instructions = std.mem.bytesAsSlice(Instruction, buffer[0..]);
    var max: usize = 0;
    // TODO: Raise error on file being too large.
    if (instructions.len < max_read) {
        max = instructions.len;
    } else {
        max = max_read;
    }

    @memcpy(MEMORY[0..max], instructions[0..max]);
}

fn get_char() u8 {
    // TODO probably lib
}

fn check_key() void {
    // TODO:
}

fn mem_read(address: u16) u16 {
    if (address == MemoryRegister.KBSR) {
        if (check_key()) {
            MEMORY[MemoryRegister.KBSR] = (1 << 15);
            MEMORY[MemoryRegister.KBDR] = get_char();
        } else {
            MEMORY[MemoryRegister.KBSR] = 0;
        }
    }
    return MEMORY[address];
}

pub fn main() !void {
    const process = std.process;
    var args = process.args();
    const stdout = std.io.getStdOut().writer();

    _ = args.skip(); // skip executable name
    const image_path = args.next() orelse process.exit(2);

    try stdout.print("{s}\n", .{image_path});

    // Read image into memory
    read_image(image_path);

    // Print to check memory
    for (MEMORY, 0..) |inst, idx| {
        inst.print();
        if (idx == 20) {
            break;
        }
    }
}
