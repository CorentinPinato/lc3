package textdocument

type TextDocumentContentChangeEvent struct {
  // Below is incremental related
  // Range Range `json:"range"`
  // RangeLength *int `json:"rangeLength"`
  Text string `json:"text"`
}
