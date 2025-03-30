package structs

type Request struct {
  RPC string `json:"jsonrpc"`
  ID int `json:"id"`
  Method string `json:"method"` 
  Params any `json:"params"`
}

type IRequest interface {
  GetID() *int
  GetParams() any
  GetMethod() string
}

func (r *Request) GetID() *int {
  return &r.ID
}

func (r *Request) GetParams() any {
  return r.Params
}

func (r *Request) GetMethod() string {
  return r.Method
}
