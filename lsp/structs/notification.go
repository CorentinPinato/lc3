package structs

type Notification struct {
  RPC string `json:"jsonrpc"`
  Method string `json:"method"` 
  Params any `json:"params"`
}
