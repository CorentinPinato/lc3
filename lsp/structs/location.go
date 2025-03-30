package structs

type Location struct {
  URI string `json:"uri"`
  Range Range `json:"range"`
}
