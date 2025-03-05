#!/usr/bin/python3

import re
import sys

OPERATIONS = [
    "ADD",
    "BR",
    "LD",
    "RES",
    "LDR",
    "LDI",
    "LEA",
    "ST",
    "STR",
    "STI",
    "NOT",
    "AND",
    "JMP",
    "JSR",
    "RTI"
]

TRAPS = [
    "PUTS",
    "HALT",
    "GETC"
]

RESERVED = [
    ".ORIG",
    ".STRINGZ",
    ".END"
]

symbols = {}

# LABEL // alias
# OP LABEL
# OP REGISTER REGISTER REGISTER
# OP REGISTER REGISTER NUMBER

def isRegister(token):
    return bool(re.match('^R[0-7]$', token))
# end

def isLabel(token):
    return bool(re.match('^[A-Z0-9_]+$', token))
# end

def isOperation(token):
    return bool(token in OPERATIONS)
# end

def isTrap(token):
    return bool(token in TRAPS)
# end

def isNumber(token):
    return bool(re.match('^#-?[1-9][0-9]*$', token)) or bool(re.match('^x[0-9a-f]+$', token))
# end

def fromHex(hex):
    return int("0" + hex, 16)
# end

def isBranch(token):
    return bool(re.match('^BRn?z?p?$', token))

ARGS = sys.argv

file = open(ARGS[1], "r")
lines = []
for line in file:
    line = re.sub(';.*$', '', line)
    line = line.replace("\n", '')
    tokens = line.split(" ")
    tokens = list(filter(lambda x : x not in ['', '\n'], tokens))

    if tokens != []:
        lines.append(tokens)
# end
file.close()

top = lines.pop(0)
if top[0] != ".ORIG":
    print("Error: File must have `.ORIG` at the very top.")
if len(top) < 2:
    print("Error: `.ORIG` must have one value.")
if len(top) > 2:
    print("Error: `.ORIG` only takes one value.")
if not isNumber(top[1]):
    print("Error: `.ORIG` param must be a number.")
start = fromHex(top[1])

idx = 0
for line in lines:
    token = line[0]
    if isLabel(token):
        if token not in OPERATIONS and token not in RESERVED and token not in TRAPS:
            if token in symbols:
                print("Error: Duplicate label for `{}`".format(token))
            symbols[hex(start + idx)] = token
            idx -= 1
    idx += 1
# end

last = lines.pop(-1)
if last[0] != '.END':
    print("Error: File must end with `.END`")

lines = list(filter(lambda x : (x[0] not in symbols.values()) or (len(x) > 1), lines))

for k,v in symbols.items():
    print("{}\t=>\t{}".format(k, v))
# end

print()
print("{}\t|{}\t|{}".format("ADDR.", "LABEL", "ASSEMBLY"))
print("{}\t|{}\t|{}".format("-----", "-----", "--------"))
for idx, line in enumerate(lines):
    addr = hex(start + idx)
    label = symbols.get(addr, "")
    print("{}\t|{}\t|{}".format(addr, label, " ".join(line)))
# end

def regToBin(reg):
    return "{0:03b}".format(int(reg.replace("R", "").replace(",", ""), 10))
# end

def numToBin(num):
    return "{0:06b}".format(int(num.replace("#", "")))
# end


def isString(tokens):
    return bool(".STRINGZ" in tokens)
# end

def intToTwos(num, size):
    inverse = 2**size + num if num < 0 else num
    return "{0:0{1}b}".format(inverse, size)
# end

labels = {v: k for k, v in symbols.items()}
def parse(addr, tokens):
    token = tokens[0]

    if isString(tokens):
        chars = list(re.search('"(.*)"', " ".join(tokens)).group(1))
        bins = []
        print(chars)
        escaped = False
        for c in chars:
            if escaped:
                if c == 'n':
                    bins.append("{0:016b}".format(10))
                escaped = False
                continue
            if c == '\\':
                escaped = True
                continue
            bins.append("{0:016b}".format(ord(c)))
        bins.append("{0:016b}".format(0))
        return bins
    # end

    if isTrap(token):
        opcode = "1111"
        base = "00000010"
        match token:
            case "GETC":
                return opcode + base + "0000"
            case "PUTS":
                return opcode + base + "0010"
            case "HALT":
                return opcode + base + "0101"
    # end
    if isBranch(token):
        opcode = "0000"
        if token == "BR":
            n = z = p = "1"
        else:
            n = "1" if bool("n" in token) else "0"
            z = "1" if bool("z" in token) else "0"
            p = "1" if bool("p" in token) else "0"
        offset = tokens[1]

        if offset in labels:
            offset = labels[offset]
        return opcode + n + z + p + intToTwos(int(offset, 16) - addr, 9)
    # end
    if isOperation(token):
        match token:
            case "LEA":
                opcode = "1110"
                dest = regToBin(tokens[1])
                offset = tokens[2]
                if offset in labels:
                    offset = labels[offset]
                return opcode + dest + intToTwos(int(offset, 16) - addr, 9)
            case "LDR":
                opcode = "0110"
                dest = regToBin(tokens[1])
                base = regToBin(tokens[2])
                offset = numToBin(tokens[3])
                return opcode + dest + base + offset
            case "ADD":
                opcode = "0001"
                dest = regToBin(tokens[1])
                base = regToBin(tokens[2])
                if isRegister(tokens[3]):
                    mode = "0"
                    return opcode + dest + base + mode + "00" + regToBin(tokens[3])
                else:
                    mode = "1"
                    return opcode + dest + base + mode + intToTwos(int(tokens[3].replace("#", ""), 10), 5)
            case "AND":
                opcode = "0101"
                dest = regToBin(tokens[1])
                base = regToBin(tokens[2])
                if isRegister(tokens[3]):
                    mode = "0"
                    return opcode + dest + base + mode + "00" + regToBin(tokens[3])
                else:
                    mode = "1"
                    return opcode + dest + base + mode + intToTwos(int(tokens[3].replace("#", ""), 10), 5)
            case "STR":
                opcode = "0111"
                reg = regToBin(tokens[1])
                base = regToBin(tokens[2])
                offset = numToBin(tokens[3])
                return opcode + reg + base + offset

    return " "*16
    # end
# end

print()
print("{} | {}".format("BINARY" + " "*10, "ASSEMBLY"))
print("{} | {}".format("-"*16, "--------"))
bins = []
for idx, tokens in enumerate(lines):
    bin = parse(start + idx + 1, tokens)
    if type(bin) is list:
        bins = bins + bin
    else:
        bins.append(bin)

for bin in bins:
    print(hex(int(bin, 2)))
# end

with open(ARGS[1].replace(".asm", ".myobj"), "wb") as file:
    file.write(int('0x3000', 16).to_bytes(2))
    for bin in bins:
        print(bin)
        file.write(int(bin, 2).to_bytes(2))
