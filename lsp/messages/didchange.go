package messages

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type DidChangeTextDocumentNotification struct {
  // structs.Notification
  structs.Request
  Params DidChangeTextDocumentParams `json:"params"`
}

type DidChangeTextDocumentParams struct {
  TextDocument textdocument.VersionedTextDocumentIdentifier `json:"textDocument"`
  ContentChanges []textdocument.TextDocumentContentChangeEvent `json:"contentChanges"`
}

func NewDidChangeRequest() structs.IRequest {
  return &DidChangeTextDocumentNotification{}
}

func HandleDidChange(s *analysis.State, request structs.IRequest) *structs.Response {
  req, ok := request.(*DidChangeTextDocumentNotification)
  if !ok { return nil }

  uri := req.Params.TextDocument.URI

  for _,change := range req.Params.ContentChanges {
    diagnostics := s.UpdateDocument(uri, change.Text)

    notification := &structs.Notification{
      RPC: "2.0",
      Method: "textDocument/publishDiagnostics",
      Params: DiagnosticsParams{
        URI: req.Params.TextDocument.URI,
        Diagnostics: diagnostics,
      },
    }
    s.Publish(notification)
  }

  return nil
}
