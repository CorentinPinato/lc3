import re
import tokens

class PreParsingError(Exception):
    def __init__(self, message):
        super().__init__(message)

def get_origin(tokenized_lines):
    first_line = tokenized_lines[0]
    directive = first_line[0]
    if isinstance(directive, tokens.Directive) and directive.lexeme == ".ORIG" and len(first_line) == 2:
        number = first_line[1]
        if isinstance(number, tokens.Number):
            return number.to_int()
    raise PreParsingError("First line must be a '.ORIG' Directive followed by a Number literal.")

def has_end(tokenized_lines):
    directive = tokenized_lines[-1][0]
    if isinstance(directive, tokens.Directive) and directive.lexeme == ".END":
        return True
    raise PreParsingError("Last line must be a '.END' Directive.")


# Address Calculation: Pure, focused functions with clear responsibility
def _should_skip_address_increment(line):
    """Check if a line should not increment the address counter.

    Label-only lines do not consume memory; they just mark an address.

    Args:
        line: List of tokens for a source line

    Returns:
        bool: True if address should not increment for this line
    """
    # Label-only line: label without any instruction/directive
    return len(line) == 1 and isinstance(line[0], tokens.Label)


def _get_line_size(line):
    """Compute memory size (in words) consumed by a line.

    Rules:
    - .STRINGZ directive: size = string length (including null terminator)
    - .BLKW directive: size = block size
    - .ORIG and .END: size = 0 (no memory consumed)
    - Other instructions/directives: size = 1
    - Label-only lines: size = 0

    Args:
        line: List of tokens for a source line

    Returns:
        int: Number of words this line consumes
    """
    if not line:
        return 0

    # Check for directives that should be skipped
    if line[0].lexeme in [".ORIG", ".END"]:
        return 0

    # Label-only line consumes no space
    if _should_skip_address_increment(line):
        return 0

    # Check for .STRINGZ directive (string length + null terminator)
    if len(line) > 1 and isinstance(line[1], tokens.Directive) and line[1].lexeme == ".STRINGZ":
        if isinstance(line[-1], tokens.String):
            # Remove quotes and process escape sequences to get true length
            string_content = line[-1].lexeme.replace('"', '')
            string_content = re.sub(r'\\n', "\n", string_content)
            string_content = re.sub(r'\\e', "\033", string_content)
            return len(string_content) + 1  # +1 for null terminator

    # Check for .BLKW directive (block of words)
    if len(line) > 1 and isinstance(line[1], tokens.Directive) and line[1].lexeme == ".BLKW":
        if isinstance(line[-1], tokens.Number):
            return line[-1].to_int()

    # Default: normal instruction/directive consumes 1 word
    return 1


def _compute_line_addresses(tokenized_lines, origin):
    """Compute memory address for each token line.

    Pure function that computes addresses without mutating state.
    Addresses start at `origin` and increment by line size.

    Args:
        tokenized_lines: List[List[Token]] of tokenized source lines
        origin: Starting memory address (from .ORIG)

    Returns:
        List[int] where result[i] is the memory address for line i
    """
    addresses = []
    current_addr = origin

    for line in tokenized_lines:
        addresses.append(current_addr)

        # Increment address by line size (unless label-only)
        line_size = _get_line_size(line)
        if not _should_skip_address_increment(line):
            current_addr += line_size
        else:
            # Label-only lines don't increment address; they just mark it
            pass

    return addresses


def _extract_labels(tokenized_lines, addresses):
    """Extract labels and their addresses from tokenized lines.

    Pure function that builds a list of (label_token, address, line_number) tuples.

    Args:
        tokenized_lines: List[List[Token]] of tokenized source lines
        addresses: List[int] of addresses for each line

    Returns:
        List[(label_token, address, line_num)]
    """
    label_info = []

    for line_idx, line in enumerate(tokenized_lines):
        if not line:
            continue

        # First token might be a label
        if isinstance(line[0], tokens.Label):
            label_token = line[0]
            line_num = label_token.line
            address = addresses[line_idx]
            label_info.append((label_token, address, line_num))

    return label_info


def _build_symbol_table(label_info):
    """Build symbol table from extracted labels, checking for duplicates.

    Pure function that transforms label info into a symbol table dictionary.

    Args:
        label_info: List[(label_token, address, line_num)] from _extract_labels

    Returns:
        Dict[str, {address, line}]

    Raises:
        PreParsingError: If duplicate labels found
    """
    result = {}

    for label_token, address, line_num in label_info:
        lexeme = label_token.lexeme

        if lexeme in result:
            existing_line = result[lexeme]['line']
            raise PreParsingError(
                f"Duplicate '{lexeme}' Label on lines {existing_line} and {line_num}."
            )

        result[lexeme] = {'line': line_num, 'address': address}

    return result


def _annotate_token_addresses(tokenized_lines, addresses):
    """Annotate tokens with memory addresses (mutation side-effect).

    Assigns the computed address to each token in place.
    This is intentionally separated from address computation for clarity
    and to allow testing without side effects.

    Args:
        tokenized_lines: List[List[Token]] - will be mutated
        addresses: List[int] of computed addresses
    """
    for line_idx, line in enumerate(tokenized_lines):
        for token in line:
            token.addr = addresses[line_idx]


def symbols(tokenized_lines, origin):
    """Build symbol table from tokenized lines.

    Orchestrates pure functions to:
    1. Compute addresses for each line
    2. Extract and validate labels
    3. Build symbol table
    4. Annotate tokens with addresses

    Args:
        tokenized_lines: List[List[Token]] of tokenized source lines
        origin: Starting memory address (from .ORIG)

    Returns:
        Dict[str, {address, line}] - symbol table mapping labels to info
    """
    # 1. Compute line addresses (pure)
    addresses = _compute_line_addresses(tokenized_lines, origin)

    # 2. Extract labels (pure)
    label_info = _extract_labels(tokenized_lines, addresses)

    # 3. Build and validate symbol table (pure)
    symbol_table = _build_symbol_table(label_info)

    # 4. Annotate tokens with addresses (side-effect, done last)
    _annotate_token_addresses(tokenized_lines, addresses)

    return symbol_table

def remove_symbols(tokenized_lines):
    lines = [t[1:] if isinstance(t[0], tokens.Label) else t for t in [l for l in tokenized_lines]]
    return list(filter(lambda x: x != [], lines))
