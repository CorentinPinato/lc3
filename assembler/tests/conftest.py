"""
Shared pytest helpers/fixtures for the assembler test suite.

Goal: keep tests focused on intent by centralizing common pipeline setup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import parser
import pre_parsers
import tokenizer


@dataclass(frozen=True)
class PipelineResult:
    lines: List[str]
    tokenized: List[list]
    origin: int
    symbols: Dict[str, Dict[str, Any]]
    unlabeled: List[list]
    stmts: List[Any]


def run_pipeline(lines: List[str]) -> PipelineResult:
    """
    Run the common assembly pipeline steps used by many tests.

    Note: this intentionally mirrors the current architecture (tokenizer/pre_parsers/parser)
    without invoking the CLI. It is a test helper, not production code.
    """
    tokenized = tokenizer.tokenize(lines)
    origin = pre_parsers.get_origin(tokenized)
    pre_parsers.has_end(tokenized)
    symbols = pre_parsers.symbols(tokenized, origin)
    unlabeled = pre_parsers.remove_symbols(tokenized)
    stmts = parser.parse(unlabeled, symbols)
    return PipelineResult(
        lines=lines,
        tokenized=tokenized,
        origin=origin,
        symbols=symbols,
        unlabeled=unlabeled,
        stmts=stmts,
    )
