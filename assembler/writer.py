"""Writer module for assembler output files.

Handles low-level I/O operations only. Formatting is delegated to presenters.
"""


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

