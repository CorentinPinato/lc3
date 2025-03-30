package server

import (
	"lc3-lsp/analysis"
	"lc3-lsp/structs"
)

// type HandleFunc func (*analysis.State, structs.IRequest) *structs.Response
type HandleFunc func (*analysis.State, structs.IRequest) *structs.Response
type RequestFunc func () structs.IRequest

type Lookup interface {
  Handle(string, HandleFunc, any)  
  Resolve(structs.Request) structs.Response
}

type LookupPair struct {
  HandleFunc HandleFunc
  RequestFunc RequestFunc
}

func (l *HandlerLookup) Handle(pattern string, handleFunc HandleFunc, requestFunc RequestFunc) {
  l.handlers[pattern] = LookupPair{HandleFunc: handleFunc, RequestFunc: requestFunc}
}

func (l *HandlerLookup) GetHandleFunc(method string) HandleFunc {
  pair := l.handlers[method]
  return pair.HandleFunc
}

func (l *HandlerLookup) GetRequestFunc(method string) RequestFunc {
  pair := l.handlers[method]
  return pair.RequestFunc
}

type HandlerLookup struct {
  state *analysis.State
  handlers map[string]LookupPair
}

func NewHandlerLookup() *HandlerLookup {
  return &HandlerLookup{
    handlers: make(map[string]LookupPair),
  }
}

func (l *HandlerLookup) SetState(state *analysis.State) {
  l.state = state
}
