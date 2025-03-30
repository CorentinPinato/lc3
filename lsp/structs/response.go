package structs

type Response struct {
  RPC string `json:"jsonrpc"`
  ID *int `json:"id,omitempty"`

  Result any `json:"result,omitempty"`
  Error any `json:"error,omitempty"`
}
