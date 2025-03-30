package analysis

import (
	"lc3-lsp/structs"
	"lc3-lsp/structs/textdocument"
	"log"
	"strings"
)

type State struct {
  Documents map[string]string
  publishCh chan *structs.Notification
  Logger *log.Logger
}

func NewState(publishCh chan *structs.Notification, logger *log.Logger) State {
  return State{
    Documents: map[string]string{},
    publishCh: publishCh,
    Logger: logger,
  }
}

func (s *State) Publish(notification *structs.Notification) {
  s.publishCh <- notification
}

func (s *State) OpenDocument(uri, text string) []textdocument.Diagnostic {
  s.Documents[uri] = text

  return s.GetDiagnostics(text)
}

func (s *State) UpdateDocument(uri, text string) []textdocument.Diagnostic {
  s.Documents[uri] = text

  return s.GetDiagnostics(text)
}

func (s *State) GetDiagnostics(text string) []textdocument.Diagnostic {
  diagnostics := []textdocument.Diagnostic{}

  for row, line := range strings.Split(text, "\n") {
    if strings.Contains(line, "VS Code") {
      idx := strings.Index(line, "VS Code")
      newDiagnostic := textdocument.Diagnostic{
        Range: lineRange(row, idx, idx + len("VS Code")),
        Severity: 1,
        Source: "Common Sense",
        Message: "Please make sure we use good language.",
      }
      diagnostics = append(diagnostics, newDiagnostic)
    }
    if strings.Contains(line, "Neovim") {
      idx := strings.Index(line, "Neovim")
      newDiagnostic := textdocument.Diagnostic{
        Range: lineRange(row, idx, idx + len("Neovim")),
        Severity: 4,
        Source: "Common Sense",
        Message: "Great Choice :)",
      }
      diagnostics = append(diagnostics, newDiagnostic)
    }
  }

  return diagnostics
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
