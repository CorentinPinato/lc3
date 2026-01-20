"""Unit tests for pre_parsers module."""
import pytest
import pre_parsers
import tokens
import tokenizer
from tests.conftest import run_pipeline


class TestGetOrigin:
    """Tests for get_origin function."""
    
    def test_valid_origin(self):
        """Test getting origin from valid .ORIG directive."""
        lines = [".ORIG x3000", "HALT", ".END"]
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        assert origin == 0x3000
    
    def test_valid_origin_decimal(self):
        """Test getting origin from decimal number."""
        lines = [".ORIG #12288", "HALT", ".END"]
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        assert origin == 0x3000
    
    def test_missing_origin_raises_error(self):
        """Test that missing .ORIG raises PreParsingError."""
        lines = ["HALT", ".END"]
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.get_origin(tokenized)
    
    def test_origin_without_number_raises_error(self):
        """Test that .ORIG without number raises error."""
        lines = [".ORIG", "HALT", ".END"]
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.get_origin(tokenized)


class TestHasEnd:
    """Tests for has_end function."""
    
    def test_valid_end(self):
        """Test that valid .END directive passes."""
        lines = [".ORIG x3000", "HALT", ".END"]
        tokenized = tokenizer.tokenize(lines)
        assert pre_parsers.has_end(tokenized) is True
    
    def test_missing_end_raises_error(self):
        """Test that missing .END raises PreParsingError."""
        lines = [".ORIG x3000", "HALT"]
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.has_end(tokenized)
    
    def test_end_not_last_raises_error(self):
        """Test that .END not at end raises error."""
        lines = [".ORIG x3000", ".END", "HALT"]
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.has_end(tokenized)


class TestSymbols:
    """Tests for symbols function."""
    
    def test_simple_label(self):
        """Test symbol table creation for simple label."""
        lines = [
            ".ORIG x3000",
            "LABEL ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        symbols_table = result.symbols
        
        assert "LABEL" in symbols_table
        assert symbols_table["LABEL"]["address"] == result.origin  # After .ORIG
        assert symbols_table["LABEL"]["line"] == 2
    
    def test_label_only_line(self):
        """Test symbol table for label-only line."""
        lines = [
            ".ORIG x3000",
            "LABEL",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        symbols_table = result.symbols
        
        assert "LABEL" in symbols_table
        # Label-only line should not increment address
        assert symbols_table["LABEL"]["address"] == result.origin  # After .ORIG
    
    def test_multiple_labels(self):
        """Test symbol table with multiple labels."""
        lines = [
            ".ORIG x3000",
            "LABEL1 ADD R1 R2 R3",
            "LABEL2 LD R0 LABEL1",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        symbols_table = result.symbols
        
        assert "LABEL1" in symbols_table
        assert "LABEL2" in symbols_table
        assert symbols_table["LABEL1"]["address"] == result.origin  # After .ORIG
        assert symbols_table["LABEL2"]["address"] == result.origin + 1
    
    def test_duplicate_label_raises_error(self):
        """Test that duplicate labels raise PreParsingError."""
        lines = [
            ".ORIG x3000",
            "LABEL ADD R1 R2 R3",
            "LABEL LD R0 LABEL",
            "HALT",
            ".END"
        ]
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        
        with pytest.raises(pre_parsers.PreParsingError) as exc_info:
            pre_parsers.symbols(tokenized, origin)
        assert "Duplicate" in str(exc_info.value)
        assert "LABEL" in str(exc_info.value)
    
    def test_string_directive_address_calculation(self):
        """Test address calculation with .STRINGZ directive."""
        lines = [
            ".ORIG x3000",
            "HELLO .STRINGZ \"Hi\"",
            "HELLO_END",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        symbols_table = result.symbols
        
        assert "HELLO" in symbols_table
        # String "Hi" is 2 chars + null = 3 words
        # Second label is located just after the 3 words string.
        assert symbols_table["HELLO"]["address"] == result.origin  # After .ORIG
        assert symbols_table["HELLO_END"]["address"] == result.origin + 3
    
    def test_blkw_directive_address_calculation(self):
        """Test address calculation with .BLKW directive."""
        lines = [
            ".ORIG x3000",
            "ARRAY .BLKW #3",
            "ARRAY_END",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        symbols_table = result.symbols
        
        assert "ARRAY" in symbols_table
        # .BLKW #3 allocates 3 words, so next address should be origin + 3
        # Second label is located just after the 3 words.
        assert symbols_table["ARRAY"]["address"] == result.origin  # After .ORIG
        assert symbols_table["ARRAY_END"]["address"] == result.origin + 3
    
    def test_address_assignment_to_tokens(self):
        """Test that addresses are assigned to tokens."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        result = run_pipeline(lines)
        
        # Check that tokens have addresses assigned
        assert result.tokenized[1][0].addr == result.origin  # After .ORIG


class TestRemoveSymbols:
    """Tests for remove_symbols function."""
    
    def test_remove_label_from_line(self):
        """Test that labels are removed from tokenized lines."""
        lines = [
            ".ORIG x3000",
            "LABEL ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        tokenized = tokenizer.tokenize(lines)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        
        # Label should be removed
        assert len(unlabeled[1]) == 4  # ADD R1 R2 R3 (no label)
        assert isinstance(unlabeled[1][0], tokens.Operation)
    
    def test_label_only_line_removed(self):
        """Test that label-only lines are removed."""
        lines = [
            ".ORIG x3000",
            "LABEL",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        tokenized = tokenizer.tokenize(lines)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        
        # Label-only line should be filtered out
        assert len(unlabeled) == 4  # .ORIG, ADD, HALT, .END (minus label line)
        assert isinstance(unlabeled[1][0], tokens.Operation)
    
    def test_no_labels_unchanged(self):
        """Test that lines without labels are unchanged."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        tokenized = tokenizer.tokenize(lines)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        
        assert len(unlabeled) == len(tokenized)
        assert len(unlabeled[1]) == 4
