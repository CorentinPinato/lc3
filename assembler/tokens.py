import re

class Token:
    def __init__(self, lexeme, line):
        self.lexeme = lexeme
        self.line = line
        self.addr = None

    def __repr__(self):
        return f"<Token.{self.__class__.__name__} {self.lexeme}>"

class Label(Token):
    @classmethod
    def match(cls, lexeme):
        return bool(re.match('^[A-Z][A-Z0-9_]*$', lexeme))

class Number(Token):
    @classmethod
    def match(cls, lexeme):
        return bool(re.match('^(#-?([0-9]|[1-9][0-9]*)|x[0-9A-F]{4})$', lexeme))

    def to_int(self):
        if 'x' in self.lexeme:
            return int(self.lexeme[-4:], 16)
        return int(self.lexeme.replace('#', ''), 10)

    def to_bin(self, size, signed = True):
        num = self.to_int()
        if signed:
            num = 2**size + num if num < 0 else num
        return f"{num:0{size}b}"

class String(Token):
    @classmethod
    def match(cls, lexeme):
        return bool(re.match('^".*"$', lexeme))

    def to_bin(self, size):
        lex = re.sub(r'\\n', "\n", self.lexeme)
        lex = re.sub(r'\\e', "\033", lex)
        bins = [f"{ord(char):0{size}b}" for char in list(lex)[1:-1]]
        bins.append(f"{0:0{size}b}")
        return bins

class Register(Token):
    @classmethod
    def match(cls, lexeme):
        return bool(re.match('^R[0-7]$', lexeme))

    def to_bin(self, size):
        num = int(self.lexeme.replace("R", ""))
        return f"{num:0{size}b}"

DIRECTIVES = [".ORIG", ".STRINGZ", ".FILL", ".END", ".BLKW"]
class Directive(Token):
    @classmethod
    def match(cls, lexeme):
        return lexeme in DIRECTIVES

OPERATIONS = {
    # LOAD
    "LOAD": { "LEA": "1110", "LD": "0010", "LDI": "1010", "LDR": "0110" },
    # STORE
    "STORE": { "ST": "0011", "STI": "1011", "STR":"0111" },
    # ARITHMETIC
    "ARITHMETIC": { "ADD": "0001" },
    # LOGICAL
    "LOGICAL": { "NOT": "1001", "AND": "0101" },
    # JUMP
    "JUMP": { "JMP": "1100", "RET": "1100", "JSR": "0100" },
    # BRANCH
    "BRANCH": { "BR": "0000", "BRnzp": "0000", "BRn": "0000", "BRz": "0000", "BRp": "0000", "BRnp": "0000", "BRnz": "0000", "BRzp": "0000" },
    # TRAP
    "TRAP": { "GETC": "1111", "OUT": "1111", "IN": "1111", "PUTS": "1111", "HALT": "1111" }
}

# Precompute flat lookup structures at module load time
OPCODE_MAP = {op: code for category in OPERATIONS.values() for op, code in category.items()}
OPERATION_SET = set(OPCODE_MAP.keys())

class Operation(Token):
    @classmethod
    def match(cls, lexeme):
        return lexeme in OPERATION_SET

    def to_bin(self, size):
        if self.lexeme not in OPCODE_MAP:
            raise ValueError(f"Unknown operation: {self.lexeme}")
        value = OPCODE_MAP[self.lexeme]
        return f"{int(value, 2):0{size}b}"
