package messages

import (
  "strings"
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
)

type CodeActionRequest struct {
  structs.Request
  Params CodeActionParams `json:"params"`
}

type CodeActionResponse struct {
  structs.Response
  Result []CodeAction `json:"result"`
}

type CodeActionParams struct {
  TextDocument textdocument.TextDocumentIdentifier `json:"textDocument"`
  Range structs.Range `json:"range"`
  Context CodeActionContext `json:"context"`
}

type CodeActionContext struct {
  Diagnostics []textdocument.Diagnostic `json:"diagnostics"`
}

type CodeAction struct {
  Title string `json:"title"`
  Edit *structs.WorkspaceEdit `json:"edit"`
  Command *structs.Command `json:"command,omitempty"`
}

func NewCodeActionRequest() structs.IRequest {
  return &CodeActionRequest{}
}

func HandleCodeAction(s *analysis.State, request structs.IRequest) *structs.Response {
  req, ok := request.(*CodeActionRequest)
  if !ok { return nil }

  uri := req.Params.TextDocument.URI
  text := s.Documents[uri]
  s.Logger.Printf("Text: %s\n", uri)

  actions := []CodeAction{}
  for row, line := range strings.Split(text, "\n"){
    idx := strings.Index(line, "VS Code")
    if idx >= 0 {
      replaceChange := map[string][]structs.TextEdit{}
      replaceChange[uri] = []structs.TextEdit{
        {
          Range: lineRange(row, idx, idx + len("VS Code")),
          NewText: "Neovim",
        },
      }

      actions = append(actions, CodeAction{
        Title: "Replace VS C*de with a superior editor",
        Edit: &structs.WorkspaceEdit{Changes: replaceChange},
      })

      censorChange := map[string][]structs.TextEdit{}
      censorChange[uri] = []structs.TextEdit{
        {
          Range: lineRange(row, idx, idx + len("VS Code")),
          NewText: "VS C*de",
        },
      }

      actions = append(actions, CodeAction{
        Title: "Censor to VS C*de",
        Edit: &structs.WorkspaceEdit{Changes: censorChange},
      })
    }
  }
  return &structs.Response{
    RPC: "2.0",
    ID: request.GetID(),
    Result: actions,
  }
}

func lineRange(line, start, end int) structs.Range {
  return structs.Range{
    Start: structs.Position{
      Line: line,
      Character: start,
    },
    End: structs.Position{
      Line: line,
      Character: end,
    },
  }
}
