package messages

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type DidOpenTextDocumentNotification struct {
  // structs.Notification
  structs.Request
  Params DidOpenTextDocumentParams `json:"params"`
}

type DidOpenTextDocumentParams struct {
  TextDocument textdocument.TextDocumentItem `json:"textDocument"`
}

type DiagnosticsParams struct {
  URI string `json:"uri"`
  Diagnostics []textdocument.Diagnostic `json:"diagnostics"`
}

func NewDidOpenRequest() structs.IRequest {
  return &DidOpenTextDocumentNotification{}
}

func HandleDidOpen(s *analysis.State, request structs.IRequest) *structs.Response {
  req, ok := request.(*DidOpenTextDocumentNotification)
  if !ok { return nil }

  uri := req.Params.TextDocument.URI
  text := req.Params.TextDocument.Text

  // TODO: do something with the diagnostics
  // Probably need some sort of publish queue
  diagnostics := s.OpenDocument(uri, text)

  // Do not publish if no diagnostics to report.
  notification := &structs.Notification{
    RPC: "2.0",
    Method: "textDocument/publishDiagnostics",
    Params: DiagnosticsParams{
      URI: req.Params.TextDocument.URI,
      Diagnostics: diagnostics,
    },
  }
  s.Publish(notification)

  return nil
}
