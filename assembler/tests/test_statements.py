"""Unit tests for statement classes and resolution."""
import pytest
import statements
import tokens


# Independent opcode oracle for tests (do NOT derive from production code).
OPCODES = {
    "ADD": "0001",
    "AND": "0101",
    "NOT": "1001",
    "LD": "0010",
    "LDR": "0110",
    "LEA": "1110",
    "ST": "0011",
    "STR": "0111",
    "JMP": "1100",
    "RET": "1100",
    "JSR": "0100",
    "BR": "0000",
    "GETC": "1111",
    "OUT": "1111",
    "PUTS": "1111",
    "IN": "1111",
    "HALT": "1111",
}


def opcode(mnemonic: str) -> str:
    """Return the expected 4-bit opcode for the given mnemonic (test-local source of truth)."""
    return OPCODES[mnemonic]


REGS = {
    "R0": "000",
    "R1": "001",
    "R2": "010",
    "R3": "011",
    "R4": "100",
    "R5": "101",
    "R6": "110",
    "R7": "111",
}


def imm(value: int, bits: int) -> str:
    """Two's complement binary encoding for immediate fields (test-local oracle)."""
    if value < 0:
        value = (1 << bits) + value
    return f"{value:0{bits}b}"


class TestArithmetic:
    """Tests for Arithmetic statement resolution."""
    
    def test_add_with_registers(self):
        """Test ADD instruction with all registers."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Register("R3", 1)
        ]
        stmt = statements.Arithmetic(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("ADD"))  # ADD opcode
        # DR, SR1, SR2
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[13:16] == REGS["R3"]
    
    def test_add_with_immediate(self):
        """Test ADD instruction with immediate value."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        stmt = statements.Arithmetic(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("ADD"))  # ADD opcode
        # DR, SR1, imm flag and value
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[10] == "1"  # Immediate mode flag
        assert result[11:16] == imm(5, 5)
    
    def test_add_wrong_argument_count(self):
        """Test ADD with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1)
        ]
        stmt = statements.Arithmetic(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "3 arguments" in str(exc_info.value)

    def test_add_invalid_last_argument_type(self):
        """Test ADD with invalid last argument type raises error."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.String('"X"', 1),
        ]
        stmt = statements.Arithmetic(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "either a Number or a Register" in str(exc_info.value)
    
    def test_arithmetic_match(self):
        """Test Arithmetic.match class method."""
        toks = [tokens.Operation("ADD", 1)]
        assert statements.Arithmetic.match(toks) is True
        
        toks = [tokens.Operation("NOT", 1)]
        assert statements.Arithmetic.match(toks) is False


class TestDirective:
    """Tests for Directive statement resolution."""
    
    def test_fill_directive(self):
        """Test .FILL directive resolution."""
        toks = [
            tokens.Directive(".FILL", 1),
            tokens.Number("#42", 1)
        ]
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result == f"{42:016b}"
    
    def test_stringz_directive(self):
        """Test .STRINGZ directive resolution."""
        toks = [
            tokens.Directive(".STRINGZ", 1),
            tokens.String('"Hi"', 1)
        ]
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert isinstance(result, list)
        assert len(result) == 3  # 'H', 'i', null
    
    def test_blkw_directive(self):
        """Test .BLKW directive resolution."""
        toks = [
            tokens.Directive(".BLKW", 1),
            tokens.Number("#3", 1)
        ]
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_end_directive(self):
        """Test .END directive returns empty string."""
        toks = [tokens.Directive(".END", 1)]
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert result == ""
    
    def test_directive_wrong_argument_count(self):
        """Test directive with wrong argument count raises error."""
        toks = [tokens.Directive(".FILL", 1)]
        stmt = statements.Directive(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "one value" in str(exc_info.value)

    def test_directive_invalid_argument_type(self):
        """Test directive with non-literal argument raises error."""
        toks = [
            tokens.Directive(".FILL", 1),
            tokens.Label("LBL", 1),
        ]
        stmt = statements.Directive(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "only takes a `Literal` argument" in str(exc_info.value)


class TestBranch:
    """Tests for Branch statement resolution."""
    
    def test_branch_with_label(self):
        """Test branch instruction with label."""
        toks = [
            tokens.Operation("BR", 1),
            tokens.Label("LABEL", 1)
        ]
        # x3000 1 .ORIG ...
        # x3001 2 ...
        # x3002 3 ...
        # x3003 4 ...
        # x3004 5 LABEL
        symbols_table = {"LABEL": {"address": 0x3004, "line": 5}}
        stmt = statements.Branch(toks, symbols_table)
        stmt.addr = 0x3000
        result = stmt.resolve()

        assert len(result) == 16
        assert result.startswith(opcode("BR"))
        assert result[4:7] == "111"  # nzp flags
        assert result[7:16] == imm(3, 9)  # x3004 - x3000 - 1 == 3
    
    def test_branch_with_number(self):
        """Test branch instruction with numeric offset."""
        toks = [
            tokens.Operation("BRnzp", 1),
            tokens.Number("#5", 1)
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("BR"))
        assert result[4:7] == "111"  # nzp flags
        assert result[7:16] == imm(5, 9)
    
    def test_branch_conditional_flags(self):
        """Test branch instruction with conditional flags."""
        toks = [
            tokens.Operation("BRn", 1),
            tokens.Number("#-2", 1)
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()
        
        assert result[4] == "1"  # n flag
        assert result[5] == "0"  # z flag
        assert result[6] == "0"  # p flag
        assert result[7:16] == imm(-2, 9)

    def test_branch_flag_z(self):
        """Test BRz sets only the z flag."""
        toks = [
            tokens.Operation("BRz", 1),
            tokens.Number("#0", 1),
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()

        assert result.startswith(opcode("BR"))
        assert result[4:7] == "010"

    def test_branch_flag_p(self):
        """Test BRp sets only the p flag."""
        toks = [
            tokens.Operation("BRp", 1),
            tokens.Number("#0", 1),
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()

        assert result.startswith(opcode("BR"))
        assert result[4:7] == "001"

    def test_branch_flag_np(self):
        """Test BRnp sets n and p flags."""
        toks = [
            tokens.Operation("BRnp", 1),
            tokens.Number("#0", 1),
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()

        assert result.startswith(opcode("BR"))
        assert result[4:7] == "101"

    def test_branch_flag_nz(self):
        """Test BRnz sets n and z flags."""
        toks = [
            tokens.Operation("BRnz", 1),
            tokens.Number("#0", 1),
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()

        assert result.startswith(opcode("BR"))
        assert result[4:7] == "110"

    def test_branch_flag_zp(self):
        """Test BRzp sets z and p flags."""
        toks = [
            tokens.Operation("BRzp", 1),
            tokens.Number("#0", 1),
        ]
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()

        assert result.startswith(opcode("BR"))
        assert result[4:7] == "011"
    
    def test_branch_wrong_argument_count(self):
        """Test branch with wrong argument count raises error."""
        toks = [tokens.Operation("BR", 1)]
        stmt = statements.Branch(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "1 argument" in str(exc_info.value)

    def test_branch_invalid_argument_type(self):
        """Test branch with invalid argument type raises error."""
        toks = [
            tokens.Operation("BR", 1),
            tokens.Register("R1", 1),
        ]
        stmt = statements.Branch(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "only takes a `Label` or `Number` argument" in str(exc_info.value)


class TestJump:
    """Tests for Jump statement resolution."""
    
    def test_jmp_with_register(self):
        """Test JMP instruction with register."""
        toks = [
            tokens.Operation("JMP", 1),
            tokens.Register("R7", 1)
        ]
        stmt = statements.Jump(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("JMP"))
        # Base register (R7) in bits 7-9
        assert result[7:10] == REGS["R7"]
        assert result[4] == "0"  # Register mode
    
    def test_ret_instruction(self):
        """Test RET instruction (no arguments)."""
        toks = [tokens.Operation("RET", 1)]
        stmt = statements.Jump(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result[4:7] == "000"
        assert result.startswith(opcode("RET"))
        assert result[7:10] == REGS["R7"]

    def test_ret_with_argument_raises_error(self):
        """Test RET with an argument raises error."""
        toks = [
            tokens.Operation("RET", 1),
            tokens.Register("R0", 1),
        ]
        stmt = statements.Jump(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes no argument" in str(exc_info.value)
    
    def test_jsr_with_label(self):
        """Test JSR instruction with label."""
        toks = [
            tokens.Operation("JSR", 1),
            tokens.Label("SUBROUTINE", 1)
        ]
        symbols_table = {"SUBROUTINE": {"address": 0x3050, "line": 10}}
        stmt = statements.Jump(toks, symbols_table)
        result = resolve_at(stmt)

        assert len(result) == 16
        assert result.startswith(opcode("JSR"))
        assert result[4] == "1"  # PCoffset mode
        assert int(result[5:], 2) == 0x3050 - 0x3000 - 1

    def test_jmp_missing_argument_raises_error(self):
        """Test non-RET jump without operand raises error."""
        toks = [tokens.Operation("JMP", 1)]
        stmt = statements.Jump(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 1 argument" in str(exc_info.value)

class TestLoad:
    """Tests for Load statement resolution."""
    
    def test_ld_instruction(self):
        """Test LD instruction."""
        toks = [
            tokens.Operation("LD", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Load(toks, symbols_table)
        stmt.addr = 0x3000
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("LD"))
        assert result[4:7] == "000"
        assert int(result[10:], 2) == 0x3005 - 0x3000 - 1
        assert result[7:10] == REGS["R0"]
    
    def test_ldr_instruction(self):
        """Test LDR instruction."""
        toks = [
            tokens.Operation("LDR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        stmt = statements.Load(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("LDR"))  # LDR opcode
        # DR and base register
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[10:16] == imm(5, 6)
    
    def test_lea_instruction(self):
        """Test LEA instruction."""
        toks = [
            tokens.Operation("LEA", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Load(toks, symbols_table)
        stmt.addr = 0x3000
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("LEA"))
        assert result[4:7] == "000"
        assert result[7:10] == REGS["R0"]
        assert int(result[7:16], 2) == 0x3005 - 0x3000 - 1

    def test_ldr_wrong_argument_count_raises_error(self):
        """Test LDR with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("LDR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
        ]  # Missing offset
        stmt = statements.Load(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 3 arguments" in str(exc_info.value)

    def test_load_wrong_argument_count_raises_error(self):
        """Test non-LDR load with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("LD", 1),
            tokens.Register("R0", 1),
        ]  # Missing label/offset
        stmt = statements.Load(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 2 arguments" in str(exc_info.value)

class TestLogical:
    """Tests for Logical statement resolution."""
    
    def test_not_instruction(self):
        """Test NOT instruction."""
        toks = [
            tokens.Operation("NOT", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1)
        ]
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("NOT"))  # NOT opcode
        assert result[7:10] == REGS["R2"]
        assert result[4:7] == REGS["R1"]
        assert result.endswith("111111")
    
    def test_and_with_register(self):
        """Test AND instruction with register."""
        toks = [
            tokens.Operation("AND", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Register("R3", 1)
        ]
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("AND"))  # AND opcode
        # DR, SR1, SR2 (register mode)
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[10:13] == "000"  # Register mode
        assert result[13:16] == REGS["R3"]
    
    def test_and_with_immediate(self):
        """Test AND instruction with immediate."""
        toks = [
            tokens.Operation("AND", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("AND"))
        # DR, SR1, imm flag and value
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[10] == "1"  # Immediate mode
        assert result[11:16] == imm(5, 5)

    def test_not_wrong_argument_count_raises_error(self):
        """Test NOT with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("NOT", 1),
            tokens.Register("R1", 1),
        ]  # Missing SR
        stmt = statements.Logical(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 2 arguments" in str(exc_info.value)

    def test_and_wrong_argument_count_raises_error(self):
        """Test AND with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("AND", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
        ]  # Missing third operand
        stmt = statements.Logical(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 3 arguments" in str(exc_info.value)


class TestStore:
    """Tests for Store statement resolution."""
    
    def test_st_instruction(self):
        """Test ST instruction."""
        toks = [
            tokens.Operation("ST", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Store(toks, symbols_table)
        stmt.addr = 0x3000
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("ST"))
        # SR, offset
        assert result[4:7] == REGS["R0"]
        assert int(result[7:], 2) == 0x3005 - 0x3000 - 1
    
    def test_str_instruction(self):
        """Test STR instruction."""
        toks = [
            tokens.Operation("STR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        stmt = statements.Store(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("STR"))  # STR opcode
        # SR and base register
        assert result[4:7] == REGS["R1"]
        assert result[7:10] == REGS["R2"]
        assert result[10:16] == imm(5, 6)

    def test_str_wrong_argument_count_raises_error(self):
        """Test STR with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("STR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
        ]  # Missing offset
        stmt = statements.Store(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 3 arguments" in str(exc_info.value)

    def test_st_wrong_argument_count_raises_error(self):
        """Test ST with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("ST", 1),
            tokens.Register("R0", 1),
        ]  # Missing label
        stmt = statements.Store(toks, {})

        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "takes 2 arguments" in str(exc_info.value)


class TestTrap:
    """Tests for Trap statement resolution."""
    
    def test_getc_instruction(self):
        """Test GETC trap instruction."""
        toks = [tokens.Operation("GETC", 1)]
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("GETC"))  # TRAP opcode
        assert result[4:8] == "0000"
        assert result.endswith(f"{0x20+0:08b}")
    
    def test_puts_instruction(self):
        """Test PUTS trap instruction."""
        toks = [tokens.Operation("PUTS", 1)]
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("PUTS"))
        assert result[4:8] == "0000"
        assert result.endswith(f"{0x20+2:08b}")
    
    def test_halt_instruction(self):
        """Test HALT trap instruction."""
        toks = [tokens.Operation("HALT", 1)]
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith(opcode("HALT"))
        assert result[4:8] == "0000"
        assert result.endswith(f"{0x20+5:08b}")
    
    def test_trap_with_argument_raises_error(self):
        """Test trap instruction with argument raises error."""
        toks = [
            tokens.Operation("HALT", 1),
            tokens.Register("R0", 1)
        ]
        stmt = statements.Trap(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "does not take arguments" in str(exc_info.value)


class TestStatementBase:
    """Tests for base Statement class."""
    
    def test_label_addr_undefined_label(self):
        """Test that undefined label raises StmtError."""
        toks = [tokens.Operation("LD", 1)]
        stmt = statements.Statement(toks, {})
        stmt.addr = 0x3000
        
        with pytest.raises(statements.StmtError) as exc_info:
            stmt.label_addr("UNDEFINED")
        assert "Undefined Label" in str(exc_info.value)
    
    def test_label_addr_defined_label(self):
        """Test label address calculation."""
        toks = [tokens.Operation("LD", 1)]
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Statement(toks, symbols_table)
        stmt.addr = 0x3000
        
        result = stmt.label_addr("LABEL")
        # Offset should be 0x3005 - 0x3000 - 1 = 4
        assert result == "#4"
    
    def test_to_hex(self):
        """Test to_hex conversion."""
        toks = [tokens.Operation("ADD", 1)]
        stmt = statements.Statement(toks, {})
        
        hex_val = stmt.to_hex()
        assert hex_val.startswith("0x")

    def test_statement_repr_includes_class_name(self):
        """Test __repr__ implementation for Statement."""
        toks = [tokens.Operation("ADD", 1)]
        stmt = statements.Statement(toks, {})

        rep = repr(stmt)
        assert "Stmt.Statement" in rep
        assert "ADD" in rep
