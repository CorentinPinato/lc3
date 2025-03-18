import matcher
import statements

stmt_matcher = matcher.Matcher()
stmt_matcher.add(statements.Directive)
stmt_matcher.add(statements.Arithmetic)
stmt_matcher.add(statements.Logical)
stmt_matcher.add(statements.Load)
stmt_matcher.add(statements.Store)
stmt_matcher.add(statements.Jump)
stmt_matcher.add(statements.Branch)
stmt_matcher.add(statements.Trap)

def parse_line(tokenized_line, symbols_table):
    klass = stmt_matcher.match(tokenized_line)
    return klass(tokenized_line, symbols_table)

def parse(tokenized_lines, symbols_table):
    return [parse_line(line, symbols_table) for line in tokenized_lines]

def to_binaries(stmts):
    return [stmt.resolve() for stmt in stmts]
