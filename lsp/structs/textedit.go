package structs

type TextEdit struct {
  Range Range `json:"range"`
  NewText string `json:"newText"`
}
