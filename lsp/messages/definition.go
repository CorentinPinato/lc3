package messages

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type DefinitionRequest struct {
  structs.Request
  Params DefinitionParams `json:"params"`
}

type DefinitionResponse struct {
  structs.Response
  Result structs.Location `json:"result"`
}

type DefinitionParams struct {
  textdocument.TextDocumentPositionParams
}

func NewDefinitionRequest() structs.IRequest {
  return &DefinitionRequest{}
}

func HandleDefinition(state *analysis.State, request structs.IRequest) *structs.Response {
  req, ok := request.(*DefinitionRequest)
  if !ok { return nil } 

  uri := req.Params.TextDocument.URI
  position := req.Params.Position

  return &structs.Response{
    RPC: "2.0",
    ID: request.GetID(),
    Result: structs.Location{
      URI: uri,
      Range: structs.Range{
        Start: structs.Position{
          Line: position.Line - 1,
          Character: 0,
        },
        End: structs.Position{
          Line: position.Line - 1,
          Character: 0,
        },
      },
    },
  }
}
