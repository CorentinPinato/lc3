"""Reader module for assembler input files."""


class Reader:
    """Handles reading assembly source files."""

    @staticmethod
    def read_lines(filename):
        """Read lines from an assembly file, stripping newlines.

        Args:
            filename: Path to assembly file

        Returns:
            List of source lines with newlines removed
        """
        with open(filename, "r", encoding="utf-8") as file:
            return [line.rstrip("\n") for line in file]
