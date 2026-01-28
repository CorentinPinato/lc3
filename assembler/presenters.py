"""Presenters module for formatting assembler output.

Separates domain logic from presentation concerns. Provides formatters that
transform assembly results into view models or strings for various output formats
(.lst, .sym, .bin, .hex).
"""


class SymbolPresenter:
    """Formats symbol table for .sym file output."""

    @staticmethod
    def format_symbol_lines(symbols_table):
        """Format symbol table as lines for .sym file.
        
        Args:
            symbols_table: Dict[label -> {address, line}]
            
        Returns:
            List[str] of formatted symbol lines
        """
        return [
            f"{label:20}{' ':10}x{meta['address']:04X}\n"
            for label, meta in symbols_table.items()
        ]


class BinaryPresenter:
    """Formats binary data for .bin and .hex file outputs."""

    @staticmethod
    def format_binary_lines(binaries):
        """Format binary strings for .bin file.
        
        Args:
            binaries: List[str] of 16-bit binary strings
            
        Returns:
            List[str] of formatted binary lines
        """
        return [f"{b}\n" for b in binaries]

    @staticmethod
    def format_hex_lines(binaries):
        """Format binary strings as hex for .hex file.
        
        Args:
            binaries: List[str] of 16-bit binary strings
            
        Returns:
            List[str] of formatted hex lines
        """
        return [f"{int(b, 2):04X}\n" for b in binaries]


class ListingPresenter:
    """Formats assembly listing table for .lst file output."""

    @staticmethod
    def format_listing(lines, stmts, symbols_table):
        """Format a detailed listing table from assembly lines and statements.
        
        Domain-agnostic: takes parsed results and produces a formatted view.
        
        Args:
            lines: Original assembly source lines
            stmts: List of parsed Statement objects
            symbols_table: Dict[label -> {address, line}]
            
        Returns:
            List[str] of formatted listing lines
        """
        # Invert symbols: address -> label for quick lookup
        addr_to_label = {
            f"x{v['address']:04X}": k
            for k, v in symbols_table.items()
        }

        # Build table rows: [ADDR, HEX, BINARY, LABEL, LINE, CODE]
        table = [["ADDR", "HEX", "BINARY", "LABEL", "LINE", "CODE"]]
        stmt_idx = 0

        for idx, line in enumerate(lines):
            line_num = idx + 1

            # Find corresponding statement for this source line
            stmt = None
            if stmt_idx < len(stmts) and stmts[stmt_idx].line == line_num:
                stmt = stmts[stmt_idx]

            # Get address and binary representation
            addr = f"x{stmt.addr:04X}" if stmt and stmt.addr is not None else ""
            binary = stmt.resolve() if stmt else ""
            
            # Handle multi-word results (e.g., .BLKW)
            long_binary = isinstance(binary, list)
            rest = []
            if long_binary:
                binary, *rest = binary

            hexa = f"x{int(binary, 2):04X}" if binary else ""
            label = addr_to_label.get(addr, "")

            if stmt:
                stmt_idx += 1

            # Add main row
            table.append([addr, hexa, binary, label, line_num, line])

            # Add overflow rows for multi-word statements
            if long_binary and stmt and stmt.addr is not None:
                a = stmt.addr + 1
                for b in rest:
                    table.append([
                        f"x{int(a):04X}",
                        f"x{int(b, 2):04X}",
                        b,
                        "",
                        "",
                        ""
                    ])
                    a += 1

        # Format rows as text with aligned columns
        return [
            "{0:6}| {1:6}| {2:16}| {3:20}| {4:4}| {5:}\n".format(*row)
            for row in table
        ]
