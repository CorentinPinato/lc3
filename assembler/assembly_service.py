import pre_parsers
import parser
import tokenizer


def assemble_lines(lines):
    """
    Pure assembly pipeline.

    Input: list[str] raw assembly lines (without trailing newlines).
    Output:
      - stmts: parsed Statement objects
      - symbols: dict[label -> {line, address}]
      - binaries: list[str] 16-bit binary strings (no I/O performed)
    """
    tokenized = tokenizer.tokenize(lines.copy())

    origin = pre_parsers.get_origin(tokenized)
    pre_parsers.has_end(tokenized)
    symbols = pre_parsers.symbols(tokenized, origin)
    unlabeled = pre_parsers.remove_symbols(tokenized)

    stmts = parser.parse(unlabeled, symbols)

    binaries = []
    for b in (s.resolve() for s in stmts):
        if b is None or b == "":
            continue
        if isinstance(b, list):
            binaries.extend(b)
        else:
            binaries.append(b)

    return stmts, symbols, binaries

