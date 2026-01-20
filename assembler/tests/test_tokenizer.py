"""Unit tests for tokenizer module."""
import pytest
import tokenizer
import tokens


class TestTokenizer:
    """Tests for tokenization functionality."""
    
    def test_simple_line(self):
        """Test tokenization of a simple instruction line."""
        result = tokenizer.tokenize(["ADD R1 R2 R3"])
        assert len(result) == 1
        assert len(result[0]) == 4
        assert isinstance(result[0][0], tokens.Operation)
        assert isinstance(result[0][1], tokens.Register)
        assert isinstance(result[0][2], tokens.Register)
        assert isinstance(result[0][3], tokens.Register)
    
    def test_line_with_comma(self):
        """Test tokenization handles commas as separators."""
        result = tokenizer.tokenize(["ADD R1, R2, R3"])
        assert len(result) == 1
        assert len(result[0]) == 4
    
    def test_string_tokenization(self):
        """Test tokenization of string literals."""
        result = tokenizer.tokenize(['.STRINGZ "Hello"'])
        assert len(result) == 1
        assert len(result[0]) == 2
        assert isinstance(result[0][0], tokens.Directive)
        assert isinstance(result[0][1], tokens.String)
        assert result[0][1].lexeme == '"Hello"'
    
    def test_string_with_spaces(self):
        """Test tokenization of strings containing spaces."""
        result = tokenizer.tokenize(['.STRINGZ "Hello World"'])
        assert len(result) == 1
        assert isinstance(result[0][1], tokens.String)
        assert result[0][1].lexeme == '"Hello World"'
    
    def test_comment_handling(self):
        """Test that comments are properly ignored."""
        result = tokenizer.tokenize(["; comment only", "ADD R1 R2 R3 ; This is a comment"])
        assert len(result) == 1
        assert len(result[0]) == 4
    
    def test_empty_line(self):
        """Test that empty lines are filtered out."""
        result = tokenizer.tokenize(["", "ADD R1 R2 R3", ""])
        assert len(result) == 1
        assert len(result[0]) == 4
    
    def test_multiple_lines(self):
        """Test tokenization of multiple lines."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        result = tokenizer.tokenize(lines)
        assert len(result) == 4
        assert isinstance(result[0][0], tokens.Directive)
        assert isinstance(result[1][0], tokens.Operation)
        assert isinstance(result[2][0], tokens.Operation)
        assert isinstance(result[3][0], tokens.Directive)
    
    def test_line_numbers(self):
        """Test that line numbers are correctly assigned."""
        lines = [
            "ADD R1 R2 R3",
            "LD R0 LABEL",
            "HALT"
        ]
        result = tokenizer.tokenize(lines)
        assert result[0][0].line == 1
        assert result[1][0].line == 2
        assert result[2][0].line == 3
    
    def test_label_with_instruction(self):
        """Test tokenization of labeled instructions."""
        result = tokenizer.tokenize(["LABEL ADD R1 R2 R3"])
        assert len(result) == 1
        assert len(result[0]) == 5
        assert isinstance(result[0][0], tokens.Label)
        assert result[0][0].lexeme == "LABEL"
    
    def test_label_only_line(self):
        """Test tokenization of label-only lines."""
        result = tokenizer.tokenize(["LABEL"])
        assert len(result) == 1
        assert len(result[0]) == 1
        assert isinstance(result[0][0], tokens.Label)
    
    def test_hex_number(self):
        """Test tokenization of hexadecimal numbers."""
        result = tokenizer.tokenize([".ORIG x3000"])
        assert len(result) == 1
        assert isinstance(result[0][1], tokens.Number)
        assert result[0][1].lexeme == "x3000"
    
    def test_decimal_number(self):
        """Test tokenization of decimal numbers."""
        result = tokenizer.tokenize(["ADD R1 R2 #5"])
        assert len(result) == 1
        assert isinstance(result[0][3], tokens.Number)
        assert result[0][3].lexeme == "#5"
    
    def test_negative_number(self):
        """Test tokenization of negative numbers."""
        result = tokenizer.tokenize(["ADD R1 R2 #-5"])
        assert len(result) == 1
        assert isinstance(result[0][3], tokens.Number)
        assert result[0][3].lexeme == "#-5"
    
    def test_invalid_token_raises_error(self):
        """Test that invalid tokens raise TokenizerError."""
        with pytest.raises(tokenizer.TokenizerError) as exc_info:
            tokenizer.tokenize([".INVALID_TOKEN"])
        assert "INVALID_TOKEN" in str(exc_info.value)
    
    def test_string_with_escape_sequences(self):
        """Test tokenization of strings with escape sequences."""
        result = tokenizer.tokenize(['.STRINGZ "Hello\\nWorld"'])
        assert len(result) == 1
        assert isinstance(result[0][1], tokens.String)
        # Escape sequence should be preserved in lexeme
    
    def test_branch_instruction(self):
        """Test tokenization of branch instructions."""
        result = tokenizer.tokenize(["BRnzp LABEL"])
        assert len(result) == 1
        assert isinstance(result[0][0], tokens.Operation)
        assert isinstance(result[0][1], tokens.Label)
    
    def test_directive_with_value(self):
        """Test tokenization of directives with values."""
        result = tokenizer.tokenize([".FILL #42"])
        assert len(result) == 1
        assert isinstance(result[0][0], tokens.Directive)
        assert isinstance(result[0][1], tokens.Number)
    
    def test_blkw_directive(self):
        """Test tokenization of .BLKW directive."""
        result = tokenizer.tokenize([".BLKW #10"])
        assert len(result) == 1
        assert isinstance(result[0][0], tokens.Directive)
        assert result[0][0].lexeme == ".BLKW"
        assert isinstance(result[0][1], tokens.Number)
