import tokens
import matcher

class TokenizerError(Exception):
    def __init__(self, lexeme, line):
        super().__init__(f"Lexeme `{lexeme}` on line {line} could not be Tokenized.")

token_matcher = matcher.Matcher()
token_matcher.add(tokens.Register)
token_matcher.add(tokens.Operation)
token_matcher.add(tokens.Label)
token_matcher.add(tokens.Directive)
token_matcher.add(tokens.Number)
token_matcher.add(tokens.String)

def tokenize(lines):
    result = [tokenize_line(line, idx+1) for idx,line in enumerate(lines)]
    return list(filter(lambda x: x != [], result))

def tokenize_line(raw, line):
    result = []
    lexemes = []

    lexeme = ""
    in_string = False
    last = len(raw) - 1
    for idx,char in enumerate(raw):
        if in_string:
            lexeme += char
            if char == '"':
                in_string = False
                lexemes.append(lexeme)
                lexeme = ""
            continue
        if char in [' ', ',']:
            if lexeme != "":
                lexemes.append(lexeme)
                lexeme = ""
            continue
        if char == '"':
            in_string = True
        if char == ';':
            lexeme = ""
            break
        lexeme += char
        if idx == last and lexeme != "":
            lexemes.append(lexeme)

    for lexeme in lexemes:
        klass = token_matcher.match(lexeme)
        if klass:
            result.append(klass(lexeme, line))
        else:
            raise TokenizerError(lexeme , line)

    return result
