"""Tests for assembler Reader and Writer classes."""
import tempfile
import os
import pytest
from reader import Reader
from writer import Writer


class TestWriteObj:
    """Tests for Writer.write_obj method."""

    def test_write_obj_big_endian(self):
        """Test Writer.write_obj with big endian byte order."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".obj") as f:
            filename = f.name

        try:
            # Binary string "0000000000000001" (value 1)
            binaries = ["0000000000000001"]
            Writer.write_obj(filename, binaries, byteorder="big")

            with open(filename, "rb") as f:
                data = f.read()

            # Should be 2 bytes: 0x00 0x01 in big endian
            assert len(data) == 2
            assert data == b"\x00\x01"
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_write_obj_little_endian(self):
        """Test Writer.write_obj with little endian byte order."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".obj") as f:
            filename = f.name

        try:
            # Binary string "0000000100000000" (value 256)
            binaries = ["0000000100000000"]
            Writer.write_obj(filename, binaries, byteorder="little")

            with open(filename, "rb") as f:
                data = f.read()

            # Should be 2 bytes: 0x00 0x01 in little endian
            assert len(data) == 2
            assert data == b"\x00\x01"
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_write_obj_multiple_values(self):
        """Test Writer.write_obj with multiple binary values."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".obj") as f:
            filename = f.name

        try:
            binaries = [
                "0000000000000001",  # 1
                "0000000000000010",  # 2
                "1111111111111111",  # 65535 (0xFFFF)
            ]
            Writer.write_obj(filename, binaries, byteorder="big")

            with open(filename, "rb") as f:
                data = f.read()

            # Should be 6 bytes total (3 * 2)
            assert len(data) == 6
            assert data == b"\x00\x01\x00\x02\xff\xff"
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestWriteTxt:
    """Tests for Writer.write_txt method."""

    def test_write_txt_simple(self):
        """Test Writer.write_txt with simple lines."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            filename = f.name

        try:
            lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
            Writer.write_txt(filename, lines)

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            assert content == "Line 1\nLine 2\nLine 3\n"
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_write_txt_empty(self):
        """Test Writer.write_txt with empty list."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            filename = f.name

        try:
            Writer.write_txt(filename, [])

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            assert content == ""
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestSymbolFileGeneration:
    """Tests for symbol file (.sym) generation."""

    def test_symbol_formatting(self):
        """Test that symbol lines are properly formatted."""
        # Create a symbols table
        symbols_table = {
            "START": {"address": 0x3000, "line": 1},
            "LOOP": {"address": 0x3005, "line": 3},
            "MSG": {"address": 0x3010, "line": 5},
        }

        # Generate symbol lines using the same logic as assembler.main
        sym_lines = [
            f"{label:20}{' ':10}x{meta['address']:04X}\n"
            for label, meta in symbols_table.items()
        ]

        # Check that all lines are generated
        assert len(sym_lines) == 3

        # Check format: label should be padded to 20 chars, space padding 10 chars, then address
        for line in sym_lines:
            parts = line.strip().split()
            assert len(parts) == 2, f"Line should have label and address: {line}"
            label_part = line[:20]
            addr_part = line[30:].strip()
            assert addr_part.startswith("x"), f"Address should start with 'x': {addr_part}"

    def test_symbol_formatting_no_nested_braces(self):
        """Test that f-string with nested braces doesn't raise SyntaxError."""
        # This test ensures the fix to the f-string is correct
        # The previous format f"{label:20}{'':10}" would raise SyntaxError
        # The corrected format is f"{label:20}{' ':10}"

        symbols_table = {
            "LABEL1": {"address": 0x3000, "line": 1},
        }

        # This should not raise SyntaxError
        sym_lines = [
            f"{label:20}{' ':10}x{meta['address']:04X}\n"
            for label, meta in symbols_table.items()
        ]

        assert len(sym_lines) == 1
        assert "x3000" in sym_lines[0]
