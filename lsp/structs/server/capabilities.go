package server

type ServerCapabilities struct {
  TextDocumentSync int `json:"textDocumentSync"`
  HoverProvider bool `json:"hoverProvider"`
  DefinitionProvider bool `json:"definitionProvider"`
  CodeActionProvider bool `json:"codeActionProvider"`
  CompletionProvider map[string]any `json:"completionProvider"`
}
