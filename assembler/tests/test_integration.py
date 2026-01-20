"""Integration tests for the full assembly pipeline."""
import pytest
import tempfile
import os
import tokenizer
import pre_parsers
import parser
import statements


class TestFullPipeline:
    """Tests for complete assembly pipeline."""
    
    def test_simple_program(self):
        """Test assembly of a simple program."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        pre_parsers.has_end(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert len(stmts) == 4
        assert stmts[0].line == 1
        assert stmts[1].line == 2
    
    def test_program_with_label(self):
        """Test assembly of program with label."""
        lines = [
            ".ORIG x3000",
            "LOOP ADD R1 R2 R3",
            "BR LOOP",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert "LOOP" in symbols
        assert len(stmts) == 5
    
    def test_program_with_string(self):
        """Test assembly of program with string directive."""
        lines = [
            ".ORIG x3000",
            "HELLO .STRINGZ \"Hi\"",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert "HELLO" in symbols
        # String should produce multiple binary words
        result = stmts[1].resolve()
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_program_with_blkw(self):
        """Test assembly of program with .BLKW directive."""
        lines = [
            ".ORIG x3000",
            "ARRAY .BLKW #3",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert "ARRAY" in symbols
        result = stmts[1].resolve()
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_binary_resolution(self):
        """Test that all statements can be resolved to binaries."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "NOT R1 R2",
            "LD R0 LABEL",
            "LABEL .FILL #42",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        binaries = []
        for stmt in stmts:
            result = stmt.resolve()
            if result == "":
                continue
            if isinstance(result, list):
                binaries.extend(result)
            else:
                binaries.append(result)
        
        assert len(binaries) > 0
        # All binaries should be 16 bits
        for b in binaries:
            assert len(b) == 16
            assert all(c in "01" for c in b)
    
    def test_label_forward_reference(self):
        """Test forward reference to label."""
        lines = [
            ".ORIG x3000",
            "BR TARGET",
            "ADD R1 R2 R3",
            "TARGET HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert symbols["TARGET"] == { "address": int("0x3002", 16), "line": 4 }
        print(int(stmts[1].resolve()[7:], 2)) == 1 # 1 + step = 2 from current place
        assert len(stmts) == 5
    
    def test_multiple_statements_resolution(self):
        """Test resolution of multiple statement types."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "AND R1 R2 #5",
            "NOT R1 R2",
            "LD R0 LABEL",
            "ST R1 LABEL",
            "BRnzp LABEL",
            "JMP R7",
            "GETC",
            "PUTS",
            "LABEL HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        # Should have 10 statements (excluding .ORIG, .END, and LABEL line)
        assert len(stmts) >= 9
        
        # All should resolve without errors
        for stmt in stmts:
            result = stmt.resolve()
            if result != "":
                if isinstance(result, list):
                    for b in result:
                        assert len(b) == 16
                else:
                    assert len(result) == 16


class TestErrorCases:
    """Tests for error handling in the pipeline."""
    
    def test_missing_origin(self):
        """Test that missing .ORIG is caught."""
        lines = [
            "ADD R1 R2 R3",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.get_origin(tokenized)
    
    def test_missing_end(self):
        """Test that missing .END is caught."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2 R3",
            "HALT"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        with pytest.raises(pre_parsers.PreParsingError):
            pre_parsers.has_end(tokenized)
    
    def test_duplicate_labels(self):
        """Test that duplicate labels are caught."""
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
    
    def test_undefined_label_in_statement(self):
        """Test that undefined label usage is caught."""
        lines = [
            ".ORIG x3000",
            "LD R0 UNDEFINED",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        # Should raise error when resolving
        with pytest.raises(statements.StmtError) as exc_info:
            stmts[1].resolve()
        assert "Undefined Label" in str(exc_info.value)
    
    def test_invalid_token(self):
        """Test that invalid tokens are caught during tokenization."""
        with pytest.raises(tokenizer.TokenizerError):
            tokenizer.tokenize([".INVALID_TOKEN"])
    
    def test_wrong_argument_count(self):
        """Test that wrong argument counts are caught."""
        lines = [
            ".ORIG x3000",
            "ADD R1 R2",  # Missing third argument
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        with pytest.raises(Exception) as exc_info:
            stmts[1].resolve()
        assert "arguments" in str(exc_info.value)


class TestComplexPrograms:
    """Tests for more complex assembly programs."""
    
    def test_program_with_comments(self):
        """Test program with comments."""
        lines = [
            "; Hello world",
            ".ORIG x3000",
            "ADD R1 R2 R3 ; This is a comment",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert len(stmts) == 4
    
    def test_program_with_multiple_strings(self):
        """Test program with multiple string directives."""
        lines = [
            ".ORIG x3000",
            "MSG1 .STRINGZ \"Hello\"",
            "MSG2 .STRINGZ \"World\"",
            "END_MSG2",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)

        # String "Hello" has 5 chars + null = 6 words
        # 3000 H
        # 3001 e
        # 3002 l
        # 3003 l
        # 3004 o
        # 3005 null
        assert len(stmts) == 5
        assert symbols["MSG1"] == { "address": int("0x3000", 16), "line": 2 }
        assert symbols["MSG2"] == { "address": int("0x3006", 16), "line": 3 }
        assert symbols["END_MSG2"] == { "address": int("0x300c", 16), "line": 4 }
    
    def test_program_with_label_only_lines(self):
        """Test program with label-only lines."""
        lines = [
            ".ORIG x3000",
            "START",
            "ADD R1 R2 R3",
            "LOOP",
            "BR START",
            "HALT",
            ".END"
        ]
        
        tokenized = tokenizer.tokenize(lines)
        origin = pre_parsers.get_origin(tokenized)
        symbols = pre_parsers.symbols(tokenized, origin)
        unlabeled = pre_parsers.remove_symbols(tokenized)
        stmts = parser.parse(unlabeled, symbols)
        
        assert "START" in symbols
        assert "LOOP" in symbols
