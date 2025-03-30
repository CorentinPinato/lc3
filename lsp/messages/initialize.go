package messages

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/server"
)

type InitializeRequest struct {
  structs.Request
  Params InitializeRequestParams `json:"params"`
}

type InitializeRequestParams struct {
  ClientInfo *ClientInfo `json:"clientInfo"`
  // TODO: expand
}

type ClientInfo struct {
  Name string `json:"name"`
  Version string `json:"version"`
}

type InitializeResponse struct {
  structs.Response
  Result InitializeResult `json:"result"`
}

type InitializeResult struct {
  Capabilities server.ServerCapabilities `json:"capabilities"`
  ServerInfo server.ServerInfo `json:"serverInfo"`
}

func NewInitializeRequest() structs.IRequest {
  return &InitializeRequest{}
}

func HandleInitialize(s *analysis.State, request structs.IRequest) *structs.Response {
  return &structs.Response{
    RPC: "2.0",
    ID: request.GetID(),
    Result: InitializeResult{
      Capabilities: server.ServerCapabilities{
        TextDocumentSync: 1,
        HoverProvider: true,
        DefinitionProvider: true,
        CodeActionProvider: true,
        CompletionProvider: map[string]any{},
      },
      ServerInfo: server.ServerInfo{
        Name: "lc3_lsp",
        Version: "0.0.1",
      },
    },
  }
}
