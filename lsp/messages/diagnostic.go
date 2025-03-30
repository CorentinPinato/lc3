package messages

import (
  "lc3-lsp/structs"
  "lc3-lsp/structs/textdocument"
)

type PublishDiagnosticNotification struct {
  structs.Notification
  Params PublishDiagnosticParams `json:"params"`
}

type PublishDiagnosticParams struct {
  URI string `json:"uri"`
  Diagnostics []textdocument.Diagnostic `json:"diagnostics"`
}
