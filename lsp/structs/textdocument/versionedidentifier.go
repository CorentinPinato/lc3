package textdocument

type VersionedTextDocumentIdentifier struct {
  TextDocumentIdentifier
  Version int `json:"version"`
}
