"""Unit tests for token classes and their matching/conversion methods."""
import pytest
import tokens


class TestLabel:
    """Tests for Label token matching."""
    
    def test_valid_labels(self):
        """Test that valid labels match correctly."""
        valid_labels = ["HELLO", "LABEL1", "A", "TEST_LABEL", "R0", "X123"]
        for label in valid_labels:
            assert tokens.Label.match(label), f"'{label}' should be a valid label"
    
    def test_invalid_labels(self):
        """Test that invalid labels do not match."""
        invalid_labels = ["hello", "1LABEL", "_LABEL", "label", "test-label", ""]
        for label in invalid_labels:
            assert not tokens.Label.match(label), f"'{label}' should not be a valid label"
    
    def test_label_creation(self):
        """Test Label token creation."""
        label = tokens.Label("HELLO", 1)
        assert label.lexeme == "HELLO"
        assert label.line == 1
        assert label.addr is None


class TestNumber:
    """Tests for Number token matching and conversion."""
    
    def test_valid_decimal_numbers(self):
        """Test valid decimal number formats."""
        valid_numbers = ["#0", "#123", "#-5", "#-123", "#5"]
        for num in valid_numbers:
            assert tokens.Number.match(num), f"'{num}' should be a valid number"
    
    def test_valid_hex_numbers(self):
        """Test valid hexadecimal number formats."""
        valid_hex = ["x0000", "x3000", "xFFFF", "x1234", "xABCD"]
        for num in valid_hex:
            assert tokens.Number.match(num), f"'{num}' should be a valid hex number"
    
    def test_invalid_numbers(self):
        """Test that invalid numbers do not match."""
        invalid_numbers = ["123", "x123", "xGHIJ", "#", "x", "x12345"]
        for num in invalid_numbers:
            assert not tokens.Number.match(num), f"'{num}' should not be a valid number"
    
    def test_to_int_decimal(self):
        """Test decimal to integer conversion."""
        num = tokens.Number("#123", 1)
        assert num.to_int() == 123
        
        num_neg = tokens.Number("#-5", 1)
        assert num_neg.to_int() == -5
    
    def test_to_int_hex(self):
        """Test hexadecimal to integer conversion."""
        num = tokens.Number("x3000", 1)
        assert num.to_int() == 0x3000
        
        num_hex = tokens.Number("xFFFF", 1)
        assert num_hex.to_int() == 0xFFFF
    
    def test_to_bin_unsigned(self):
        """Test binary conversion without sign."""
        num = tokens.Number("#5", 1)
        assert num.to_bin(4, signed=False) == "0101"
        assert num.to_bin(8, signed=False) == "00000101"
    
    def test_to_bin_signed_positive(self):
        """Test binary conversion with sign for positive numbers."""
        num = tokens.Number("#5", 1)
        assert num.to_bin(4, signed=True) == "0101"
    
    def test_to_bin_signed_negative(self):
        """Test binary conversion with sign for negative numbers."""
        num = tokens.Number("#-1", 1)
        result = num.to_bin(4, signed=True)
        # Should be two's complement: 2^4 - 1 = 15 = 1111
        assert result == "1111"
        
        num = tokens.Number("#-5", 1)
        result = num.to_bin(4, signed=True)
        # Should be 2^4 - 5 = 11 = 1011
        assert result == "1011"


class TestString:
    """Tests for String token matching and conversion."""
    
    def test_valid_strings(self):
        """Test valid string formats."""
        valid_strings = ['"Hello"', '""', '"Test"', '"Hello World"']
        for s in valid_strings:
            assert tokens.String.match(s), f"'{s}' should be a valid string"
    
    def test_invalid_strings(self):
        """Test that invalid strings do not match."""
        invalid_strings = ['Hello', '"unclosed', 'no quotes', '""extra']
        for s in invalid_strings:
            assert not tokens.String.match(s), f"'{s}' should not be a valid string"
    
    def test_to_bin_simple(self):
        """Test string to binary conversion."""
        s = tokens.String('"Hi"', 1)
        result = s.to_bin(16)
        assert isinstance(result, list)
        assert len(result) == 3  # 'H', 'i', null terminator
        assert result[0] == f"{ord('H'):016b}"
        assert result[1] == f"{ord('i'):016b}"
        assert result[2] == "0000000000000000"
    
    def test_to_bin_with_escape_sequences(self):
        """Test string conversion with escape sequences."""
        s = tokens.String('"Hi\\n"', 1)
        result = s.to_bin(16)
        assert len(result) == 4  # 'H', 'i', '\n', null


class TestRegister:
    """Tests for Register token matching and conversion."""
    
    def test_valid_registers(self):
        """Test valid register formats."""
        valid_regs = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]
        for reg in valid_regs:
            assert tokens.Register.match(reg), f"'{reg}' should be a valid register"
    
    def test_invalid_registers(self):
        """Test that invalid registers do not match."""
        invalid_regs = ["R8", "R9", "r0", "REG0", "R", "R-1"]
        for reg in invalid_regs:
            assert not tokens.Register.match(reg), f"'{reg}' should not be a valid register"
    
    def test_to_bin(self):
        """Test register to binary conversion."""
        for i in range(8):
            reg = tokens.Register(f"R{i}", 1)
            assert reg.to_bin(3) == f"{i:03b}"


class TestDirective:
    """Tests for Directive token matching."""
    
    def test_valid_directives(self):
        """Test valid directive formats."""
        valid_directives = [".ORIG", ".STRINGZ", ".FILL", ".END", ".BLKW"]
        for d in valid_directives:
            assert tokens.Directive.match(d), f"'{d}' should be a valid directive"
    
    def test_invalid_directives(self):
        """Test that invalid directives do not match."""
        invalid_directives = [".orig", ".UNKNOWN", "ORIG", ".", ""]
        for d in invalid_directives:
            assert not tokens.Directive.match(d), f"'{d}' should not be a valid directive"


class TestOperation:
    """Tests for Operation token matching and conversion."""
    
    def test_valid_operations(self):
        """Test valid operation formats."""
        valid_ops = ["ADD", "NOT", "LD", "ST", "BR", "JMP", "RET", "GETC", "PUTS", "HALT"]
        for op in valid_ops:
            assert tokens.Operation.match(op), f"'{op}' should be a valid operation"
    
    def test_invalid_operations(self):
        """Test that invalid operations do not match."""
        invalid_ops = ["add", "UNKNOWN", "LDX", ""]
        for op in invalid_ops:
            assert not tokens.Operation.match(op), f"'{op}' should not be a valid operation"
    
    def test_to_bin_load_operations(self):
        """Test binary conversion for load operations."""
        op = tokens.Operation("LD", 1)
        assert op.to_bin(4) == "0010"
        
        op = tokens.Operation("LEA", 1)
        assert op.to_bin(4) == "1110"
    
    def test_to_bin_arithmetic_operations(self):
        """Test binary conversion for arithmetic operations."""
        op = tokens.Operation("ADD", 1)
        assert op.to_bin(4) == "0001"
    
    def test_to_bin_trap_operations(self):
        """Test binary conversion for trap operations."""
        op = tokens.Operation("HALT", 1)
        assert op.to_bin(4) == "1111"
        
        op = tokens.Operation("GETC", 1)
        assert op.to_bin(4) == "1111"
