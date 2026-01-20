# Test Suite for LC-3 Assembler

This directory contains comprehensive unit and integration tests for the assembler.

## Test Structure

- `test_tokens.py` - Tests for token classes (Label, Number, String, Register, Directive, Operation)
- `test_tokenizer.py` - Tests for tokenization of assembly source lines
- `test_pre_parsers.py` - Tests for pre-parsing validation (origin, end, symbols)
- `test_statements.py` - Tests for statement resolution (Arithmetic, Branch, Jump, Load, Store, Logical, Trap, Directive)
- `test_integration.py` - End-to-end tests for the complete assembly pipeline

## Running Tests

### Using pytest (recommended)

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_tokens.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_tokens.py::TestLabel::test_valid_labels
```

### Using unittest (alternative)

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Test Coverage

Install `coverage`:
```bash
python3 -m pip install coverage
```

Run coverage:
```bash
coverage run -m pytest
```

Get coverage report:
```bash
coverage report -m
```

Current coverage:
```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
matcher.py                     10      0   100%
parser.py                      18      1    94%   22
pre_parsers.py                 46      0   100%
statements.py                 158     16    90%   27, 44, 63, 77, 99, 103, 106-107, 125, 131, 145, 148, 168, 172, 191, 195
tests/__init__.py               0      0   100%
tests/test_integration.py     164      3    98%   118, 179-180
tests/test_pre_parsers.py     115      0   100%
tests/test_statements.py      232      0   100%
tests/test_tokenizer.py       100      0   100%
tests/test_tokens.py          118      0   100%
tokenizer.py                   50      0   100%
tokens.py                      55      1    98%   10
---------------------------------------------------------
TOTAL                        1066     21    98%
```

The test suite covers:

### Happy Paths
- Valid token matching for all token types
- Correct tokenization of various instruction formats
- Proper symbol table generation
- Correct binary resolution for all instruction types
- End-to-end assembly of complete programs

### Error Cases
- Invalid tokens raise `TokenizerError`
- Missing `.ORIG` or `.END` directives raise `PreParsingError`
- Duplicate labels raise `PreParsingError`
- Undefined label usage raises `StmtError`
- Wrong argument counts raise appropriate exceptions
- Invalid instruction formats are caught

### Edge Cases
- Label-only lines
- Comments in source code
- String escape sequences
- Negative numbers
- Hexadecimal and decimal number formats
- Multiple labels and forward references
- `.STRINGZ` and `.BLKW` directives

## Adding New Tests

When adding new features or fixing bugs:

1. Add unit tests for the specific component
2. Add integration tests if the feature affects the pipeline
3. Ensure both happy paths and error cases are covered
4. Run the full test suite before committing

## Notes

- Tests use pytest fixtures and assertions
- Some tests may need adjustment based on actual implementation details
- Integration tests verify the complete pipeline from source to binary output
