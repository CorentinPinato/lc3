package textdocument

import "lc3-lsp/structs"

type TextDocumentPositionParams struct {
  TextDocument TextDocumentIdentifier `json:"textDocument"`
  Position structs.Position `json:"position"`
}
