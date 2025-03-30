package structs

type WorkspaceEdit struct {
  Changes map[string][]TextEdit `json:"changes"`
}
