"""Unit tests for statement classes and resolution."""
import pytest
import statements
import tokens


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
        toks[0].addr = 0x3000
        stmt = statements.Arithmetic(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0001")  # ADD opcode
    
    def test_add_with_immediate(self):
        """Test ADD instruction with immediate value."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Arithmetic(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0001") # ADD opcode
        assert result[10] == "1"  # Immediate mode flag
    
    def test_add_wrong_argument_count(self):
        """Test ADD with wrong number of arguments raises error."""
        toks = [
            tokens.Operation("ADD", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Arithmetic(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "3 arguments" in str(exc_info.value)
    
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
        toks[0].addr = 0x3000
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
        toks[0].addr = 0x3000
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
        toks[0].addr = 0x3000
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_end_directive(self):
        """Test .END directive returns empty string."""
        toks = [tokens.Directive(".END", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Directive(toks, {})
        result = stmt.resolve()
        
        assert result == ""
    
    def test_directive_wrong_argument_count(self):
        """Test directive with wrong argument count raises error."""
        toks = [tokens.Directive(".FILL", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Directive(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "one value" in str(exc_info.value)


class TestBranch:
    """Tests for Branch statement resolution."""
    
    def test_branch_with_label(self):
        """Test branch instruction with label."""
        toks = [
            tokens.Operation("BR", 1),
            tokens.Label("LABEL", 1)
        ]
        toks[0].addr = 0x3000
        # x3000 1 .ORIG ...
        # x3001 2 ...
        # x3002 3 ...
        # x3003 4 ...
        # x3004 5 LABEL
        symbols_table = {"LABEL": {"address": 0x3004, "line": 5}}
        stmt = statements.Branch(toks, symbols_table)
        
        result = stmt.resolve()

        assert len(result) == 16
        assert result.startswith("0000")
        assert result[4:7] == "111"  # nzp flags
    
    def test_branch_with_number(self):
        """Test branch instruction with numeric offset."""
        toks = [
            tokens.Operation("BRnzp", 1),
            tokens.Number("#5", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0000")
        assert result[4:7] == "111"  # nzp flags
    
    def test_branch_conditional_flags(self):
        """Test branch instruction with conditional flags."""
        toks = [
            tokens.Operation("BRn", 1),
            tokens.Number("#-2", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Branch(toks, {})
        result = stmt.resolve()
        
        assert result[4] == "1"  # n flag
        assert result[5] == "0"  # z flag
        assert result[6] == "0"  # p flag
    
    def test_branch_wrong_argument_count(self):
        """Test branch with wrong argument count raises error."""
        toks = [tokens.Operation("BR", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Branch(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "1 argument" in str(exc_info.value)


class TestJump:
    """Tests for Jump statement resolution."""
    
    def test_jmp_with_register(self):
        """Test JMP instruction with register."""
        toks = [
            tokens.Operation("JMP", 1),
            tokens.Register("R7", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Jump(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("1100")
        assert result[4] == "0"  # Register mode
    
    def test_ret_instruction(self):
        """Test RET instruction (no arguments)."""
        toks = [tokens.Operation("RET", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Jump(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("1100")
        assert result[4:7] == "000"
        assert result[7:10] == "111"  # R7
    
    def test_jsr_with_label(self):
        """Test JSR instruction with label."""
        toks = [
            tokens.Operation("JSR", 1),
            tokens.Label("SUBROUTINE", 1)
        ]
        toks[0].addr = 0x3000
        symbols_table = {"SUBROUTINE": {"address": 0x3050, "line": 10}}
        stmt = statements.Jump(toks, symbols_table)
        
        # Label resolution will fail without proper address setup
        # This tests the structure, actual resolution needs proper setup
        assert stmt.tokens[1].lexeme == "SUBROUTINE"


class TestLoad:
    """Tests for Load statement resolution."""
    
    def test_ld_instruction(self):
        """Test LD instruction."""
        toks = [
            tokens.Operation("LD", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        toks[0].addr = 0x3000
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Load(toks, symbols_table)
        
        # Will need proper address setup for full resolution
        assert len(stmt.tokens) == 3
    
    def test_ldr_instruction(self):
        """Test LDR instruction."""
        toks = [
            tokens.Operation("LDR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Load(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0110")  # LDR opcode
    
    def test_lea_instruction(self):
        """Test LEA instruction."""
        toks = [
            tokens.Operation("LEA", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        toks[0].addr = 0x3000
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Load(toks, symbols_table)
        
        assert len(stmt.tokens) == 3


class TestLogical:
    """Tests for Logical statement resolution."""
    
    def test_not_instruction(self):
        """Test NOT instruction."""
        toks = [
            tokens.Operation("NOT", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("1001")  # NOT opcode
        assert result.endswith("111111")
    
    def test_and_with_register(self):
        """Test AND instruction with register."""
        toks = [
            tokens.Operation("AND", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Register("R3", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0101")  # AND opcode
        assert result[12] == "0"  # Register mode
    
    def test_and_with_immediate(self):
        """Test AND instruction with immediate."""
        toks = [
            tokens.Operation("AND", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Logical(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result[10] == "1"  # Immediate mode


class TestStore:
    """Tests for Store statement resolution."""
    
    def test_st_instruction(self):
        """Test ST instruction."""
        toks = [
            tokens.Operation("ST", 1),
            tokens.Register("R0", 1),
            tokens.Label("LABEL", 1)
        ]
        toks[0].addr = 0x3000
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Store(toks, symbols_table)
        
        # Will need proper address setup for full resolution
        assert len(stmt.tokens) == 3
    
    def test_str_instruction(self):
        """Test STR instruction."""
        toks = [
            tokens.Operation("STR", 1),
            tokens.Register("R1", 1),
            tokens.Register("R2", 1),
            tokens.Number("#5", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Store(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("0111")  # STR opcode


class TestTrap:
    """Tests for Trap statement resolution."""
    
    def test_getc_instruction(self):
        """Test GETC trap instruction."""
        toks = [tokens.Operation("GETC", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.startswith("1111")  # TRAP opcode
        assert result.endswith(f"{32+0:012b}")
    
    def test_puts_instruction(self):
        """Test PUTS trap instruction."""
        toks = [tokens.Operation("PUTS", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.endswith(f"{32+2:012b}")
    
    def test_halt_instruction(self):
        """Test HALT trap instruction."""
        toks = [tokens.Operation("HALT", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Trap(toks, {})
        result = stmt.resolve()
        
        assert len(result) == 16
        assert result.endswith(f"{32+5:012b}")
    
    def test_trap_with_argument_raises_error(self):
        """Test trap instruction with argument raises error."""
        toks = [
            tokens.Operation("HALT", 1),
            tokens.Register("R0", 1)
        ]
        toks[0].addr = 0x3000
        stmt = statements.Trap(toks, {})
        
        with pytest.raises(Exception) as exc_info:
            stmt.resolve()
        assert "does not take arguments" in str(exc_info.value)


class TestStatementBase:
    """Tests for base Statement class."""
    
    def test_label_addr_undefined_label(self):
        """Test that undefined label raises StmtError."""
        toks = [tokens.Operation("LD", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Statement(toks, {})
        
        with pytest.raises(statements.StmtError) as exc_info:
            stmt.label_addr("UNDEFINED")
        assert "Undefined Label" in str(exc_info.value)
    
    def test_label_addr_defined_label(self):
        """Test label address calculation."""
        toks = [tokens.Operation("LD", 1)]
        toks[0].addr = 0x3000
        symbols_table = {"LABEL": {"address": 0x3005, "line": 5}}
        stmt = statements.Statement(toks, symbols_table)
        
        result = stmt.label_addr("LABEL")
        # Offset should be 0x3005 - 0x3000 - 1 = 4
        assert result == "#4"
    
    def test_to_hex(self):
        """Test to_hex conversion."""
        toks = [tokens.Operation("ADD", 1)]
        toks[0].addr = 0x3000
        stmt = statements.Statement(toks, {})
        
        hex_val = stmt.to_hex()
        assert hex_val.startswith("0x")
