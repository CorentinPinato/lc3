package messages

import (
  "fmt"
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type HoverRequest struct {
  structs.Request
  Params HoverParams `json:"params"`
}

type HoverResponse struct {
  structs.Response
  Result HoverResult `json:"result"`
}

type HoverParams struct {
  textdocument.TextDocumentPositionParams
  // structs.WorkDoneProgressParams
}

type HoverResult struct {
  Contents string `json:"contents"`
}

func NewHoverRequest() structs.IRequest {
  return &HoverRequest{}
}

func HandleHover(s *analysis.State, request structs.IRequest) *structs.Response {
  req, ok := request.(*HoverRequest)
  if !ok { return nil }

  uri := req.Params.TextDocument.URI
  document := s.Documents[uri]

  return &structs.Response{
    RPC: "2.0",
    ID: request.GetID(),
    Result: HoverResult{
      Contents: fmt.Sprintf("File: %s, Characters: %d", uri, len(document)),
    },
  }
}
