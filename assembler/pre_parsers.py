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

def symbols(tokenized_lines, origin):
    labels = []
    idx = 0
    for line in tokenized_lines:
        if line[0].lexeme in [".ORIG", ".END"]:
            continue
        for t in line:
            t.addr = origin + idx
        if isinstance(line[-1], tokens.String):
            idx += len(re.sub(r'\\n', "\n", line[-1].lexeme.replace('"', '')))
        if isinstance(line[0], tokens.Label):
            label = line[0]
            if len(line) == 1:
                idx -= 1
            elif isinstance(line[1], tokens.Directive) and line[1].lexeme == ".BLKW":
                idx += line[-1].to_int() - 1
            labels.append(label)
        idx += 1

    result = {}
    for label in labels:
        if result.get(label.lexeme, False):
            line = result[label.lexeme]['line']
            raise PreParsingError(f"Duplicate '{label.lexeme}' Label on lines {line} and {label.line}.")

        result[label.lexeme] = { 'line': label.line, 'address': label.addr } 
    return result

def remove_symbols(tokenized_lines):
    lines = [t[1:] if isinstance(t[0], tokens.Label) else t for t in [l for l in tokenized_lines]]
    return list(filter(lambda x: x != [], lines))
