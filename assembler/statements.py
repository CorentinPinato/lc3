import tokens as Tokens

class StmtError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Statement:
    def __init__(self, tokens, symbols_table):
        self.line = tokens[0].line
        self.addr = tokens[0].addr if tokens[0].addr is not None else None
        self.tokens = tokens
        self.symbols_table = symbols_table

    def label_addr(self, label):
        address = self.symbols_table.get(label, False)
        if address:
            return f"#{address['address'] - self.addr - 1}"
        raise StmtError(f"Undefined Label '{label}' used on line {self.line}.")

    def resolve(self):
        return f"{0:016b}"

    def to_hex(self):
        return hex(int(self.resolve(), 2))

    def __repr__(self):
        return f"<Stmt.{self.__class__.__name__} {self.tokens}]>"

class Arithmetic(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["ARITHMETIC"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)
        if size != 4:
            raise Exception(f"Error on line {self.line}: Operation takes 3 arguments, {size} found.")

        if isinstance(tokens[3], Tokens.Register):
            return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + "000" + tokens[3].to_bin(3)
        if isinstance(tokens[3], Tokens.Number):
            return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + "1" + tokens[3].to_bin(5)
        raise Exception(f"Error on line {self.line}: Operation takes either a Number or a Register as last argument.")

class Directive(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Directive)

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)
        if size == 1 and tokens[0].lexeme == ".END":
            return ""
        if size != 2:
            raise Exception(f"Error on line {self.line}: directive takes one value, {size-1} found.")

        if tokens[0].lexeme == '.BLKW':
            return [f"{0:016b}"] * tokens[-1].to_int()
        if isinstance(tokens[1], Tokens.Number) or isinstance(tokens[1], Tokens.String):
            return tokens[1].to_bin(16)
        raise Exception(f"Error on line {self.line}: directive only takes a `Literal` argument.")

class Branch(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["BRANCH"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)

        if size != 2:
            raise Exception(f"Error on line {self.line}: Operation takes 1 argument, {size-1} found.")
        if not isinstance(tokens[1], Tokens.Label) and not isinstance(tokens[1], Tokens.Label):
            raise Exception(f"Error on line {self.line}: Operation only takes a `Label` or `Number` argument.")

        tokens = [Tokens.Number(self.label_addr(t.lexeme), t.line) if isinstance(t, Tokens.Label) else t for t in tokens]
        if tokens[0].lexeme == "BR":
            n = z = p = "1"
        else:
            n = "1" if 'n' in tokens[0].lexeme else "0"
            z = "1" if 'z' in tokens[0].lexeme else "0"
            p = "1" if 'p' in tokens[0].lexeme else "0"
        return tokens[0].to_bin(4) + n + z + p + tokens[1].to_bin(9)

class Jump(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["JUMP"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)

        if tokens[0].lexeme == "RET":
            if size != 1:
                raise Exception(f"Error on line {self.line}: Operation takes no argument.")
            return tokens[0].to_bin(4) + "000" + "111" + "000000"

        if size != 2:
            raise Exception(f"Error on line {self.line}: Operation takes 1 argument, {size-1} found.")

        if isinstance(tokens[1], Tokens.Label):
            flag = "1"
            offset = Tokens.Number(self.label_addr(tokens[1].lexeme), self.line).to_bin(11, True)
        else:
            flag = "0"
            offset = "00" + tokens[1].to_bin(3) + "000000"

        return tokens[0].to_bin(4) + flag + offset

class Load(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["LOAD"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)

        if tokens[0].lexeme == "LDR":
            if size != 4:
                raise Exception(f"Error on line {self.line}: Operation takes 3 arguments, {size-1} found.")
            return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + tokens[3].to_bin(6)

        tokens = [Tokens.Number(self.label_addr(t.lexeme), t.line) if isinstance(t, Tokens.Label) else t for t in tokens]

        if size != 3:
            raise Exception(f"Error on line {self.line}: Operation takes 2 arguments, {size-1} found.")
        return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(9, True)

class Logical(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["LOGICAL"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)

        if tokens[0].lexeme == "NOT":
            if size != 3:
                raise Exception(f"Error on line {self.line}: Operation takes 2 arguments, {size-1} found.")
            return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + "111111"
        if size != 4:
            raise Exception(f"Error on line {self.line}: Operation takes 3 arguments, {size-1} found.")
        if isinstance(tokens[-1], Tokens.Register):
            flag = "0"
            offset = "00" + tokens[-1].to_bin(3)
        else:
            flag = "1"
            offset = tokens[-1].to_bin(5)
        return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + flag + offset

class Store(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["STORE"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)

        if tokens[0].lexeme == "STR":
            if size != 4:
                raise Exception(f"Error on line {self.line}: Operation takes 3 arguments, {size-1} found.")
            return tokens[0].to_bin(4) + tokens[1].to_bin(3) + tokens[2].to_bin(3) + tokens[3].to_bin(6)

        if size != 3:
            raise Exception(f"Error on line {self.line}: Operation takes 2 arguments, {size-1} found.")
        laddr = Tokens.Number(self.label_addr(tokens[2].lexeme), self.line)
        return tokens[0].to_bin(4) + tokens[1].to_bin(3) + laddr.to_bin(9, True)

class Trap(Statement):
    @classmethod
    def match(cls, tokens):
        return isinstance(tokens[0], Tokens.Operation) and (tokens[0].lexeme in Tokens.OPERATIONS["TRAP"])

    def resolve(self):
        tokens = self.tokens
        size = len(tokens)
        if size > 1:
            raise Exception(f"Error on line {self.line}: Operation does not take arguments, {size-1} found.")
        opcode = tokens[0].to_bin(4)
        match tokens[0].lexeme:
            case "GETC":
                return f"{opcode}{32+0:012b}"
            case "OUT":
                return f"{opcode}{32+1:012b}"
            case "PUTS":
                return f"{opcode}{32+2:012b}"
            case "IN":
                return f"{opcode}{32+3:012b}"
            case "HALT":
                return f"{opcode}{32+5:012b}"
