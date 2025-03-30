package messages

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type CompletionRequest struct {
  structs.Request
  Params CompletionParams `json:"params"`
}

type CompletionParams struct {
  textdocument.TextDocumentPositionParams
  Context *CompletionContext `json:"context,omitempty"`
}

type CompletionContext struct {

}

type CompletionResponse struct {
  structs.Response
  Result []CompletionItem `json:"result"`
}

type CompletionItem struct {
  Label string `json:"label"`
  Detail string `json:"detail"`
  Documentation string `json:"documentation"`
}

func NewCompletionRequest() structs.IRequest {
  return &CompletionRequest{}
}

func HandleCompletion(state *analysis.State, request structs.IRequest) *structs.Response {
  items := []CompletionItem{
    {
      Label: "Neovim (BTW)",
      Detail: "Very cool editor",
      Documentation: "Fun to watch in videos, don't forget to ...",
    },
    {
      Label: "LEA",
      Detail: "Operator",
      Documentation: "daaddad",
    },
    {
      Label: "STR",
      Detail: "Operator",
      Documentation: "daaddad",
    },
  }

  return &structs.Response{
    RPC: "2.0",
    ID: request.GetID(),
    Result: items,
  }
}
