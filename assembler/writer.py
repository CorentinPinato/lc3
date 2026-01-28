"""Writer module for assembler output files."""


class Writer:
    """Handles writing assembler output files in various formats."""

    @staticmethod
    def write_obj(filename, binaries, byteorder="big"):
        """Write binary values to an object file in binary format.
        
        Args:
            filename: Path to output .obj file
            binaries: List of binary strings (e.g., "0000000000000001")
            byteorder: Byte order for conversion ("big" or "little")
        """
        with open(filename, "wb") as file:
            for b in binaries:
                file.write(int(b, 2).to_bytes(2, byteorder=byteorder))

    @staticmethod
    def write_txt(filename, data):
        """Write text data to a file.
        
        Args:
            filename: Path to output text file
            data: List of strings to write
        """
        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(data)

    @staticmethod
    def build_listing(lines, stmts, symbols_table):
        """Build a listing table from assembly lines, statements, and symbols.
        
        Args:
            lines: Original assembly source lines
            stmts: List of parsed statements
            symbols_table: Dictionary of symbols with addresses
            
        Returns:
            List of formatted listing lines
        """
        # invert symbols to address -> label for listing
        addr_to_label = {f"x{v['address']:04X}": k for k, v in symbols_table.items()}

        table = [["ADDR", "HEX", "BINARY", "LABEL", "LINE", "CODE"]]
        stmt_idx = 0

        for idx, line in enumerate(lines):
            line_num = idx + 1

            stmt = None
            if stmt_idx < len(stmts) and stmts[stmt_idx].line == line_num:
                stmt = stmts[stmt_idx]

            addr = f"x{stmt.addr:04X}" if stmt and stmt.addr is not None else ""

            binary = stmt.resolve() if stmt else ""
            long_binary = isinstance(binary, list)
            rest = []
            if long_binary:
                binary, *rest = binary

            hexa = f"x{int(binary, 2):04X}" if binary else ""
            label = addr_to_label.get(addr, "")

            if stmt:
                stmt_idx += 1

            table.append([addr, hexa, binary, label, line_num, line])

            if long_binary and stmt and stmt.addr is not None:
                a = stmt.addr + 1
                for b in rest:
                    table.append([f"x{int(a):04X}", f"x{int(b, 2):04X}", b, "", "", ""])
                    a += 1

        return ["{0:6}| {1:6}| {2:16}| {3:20}| {4:4}| {5:}\n".format(*row) for row in table]
