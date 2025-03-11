const std = @import("std");
const time = std.time;

const c = @cImport({
    @cInclude("stdiolib.h");
    @cInclude("termios.h");
    @cInclude("unistd.h");
});

const STDIN_FILENO = std.os.posix.STDIN_FILENO;
const termios: c.struct_termios = undefined;

extern fn cleanup_terminal() void {
    _ = c.tcsetattr(STDIN_FILENO, c.TCSANOW, &termios);
}

fn check_key() i64 {
    const stdin = std.io.getStdIn().reader();
    const stdout = std.io.getStdOut().writer();

    var buf:[10]u8 = undefined;

    try stdout.print("A number please: ", .{});

    if (try stdin.readUntilDelimiterOrEof(buf[0..], '\n')) |user_input| {
        return std.fmt.parseInt(i64, user_input, 10);
    } else {
        return @as(i64, 0);
    }
}

pub fn main() !void {
    const allocator = std.heap.page_allocator;

    _ = check_key();

    // Open file
    const file = std.fs.cwd().openFile("example.txt", .{}) catch unreachable;
    defer file.close();

    // Read file into buffer
    const file_size: u64 = file.getEndPos() catch unreachable;
    const buffer: []u8 = allocator.alloc(u8, file_size) catch unreachable;
    defer allocator.free(buffer);

    _ = file.readAll(buffer) catch unreachable;

    const Instruction = packed struct {
        operation: u4,
        instruction: u12,
    };

    const data = std.mem.bytesAsSlice(Instruction, buffer[0..]);
    var insts: []u16 = try std.heap.page_allocator.alloc(u16, buffer.len * 2);
    defer std.heap.page_allocator.free(insts);

    for (data, 0..) |inst, idx| {
        insts[idx] = @bitCast(inst);
        std.debug.print("{b:016}\n", .{insts[idx]});
    }
}
