package textdocument

import (
  "lc3-lsp/structs"
)

type Diagnostic struct {
  Range structs.Range `json:"range"`
  Severity int `json:"severity"`
  Source string `json:"source"`
  Message string `json:"message"`
}
