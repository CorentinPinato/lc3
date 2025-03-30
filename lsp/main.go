package main

import (
	"lc3-lsp/messages"
	"lc3-lsp/server"
)

func main() {
  lookup := server.NewHandlerLookup()
  lookup.Handle("initialize", messages.HandleInitialize, messages.NewInitializeRequest)
  lookup.Handle("textDocument/didOpen", messages.HandleDidOpen, messages.NewDidOpenRequest)
  lookup.Handle("textDocument/didChange", messages.HandleDidChange, messages.NewDidChangeRequest)
  lookup.Handle("textDocument/completion", messages.HandleCompletion, messages.NewCompletionRequest)
  lookup.Handle("textDocument/codeAction", messages.HandleCodeAction, messages.NewCodeActionRequest)
  lookup.Handle("textDocument/definition", messages.HandleDefinition, messages.NewDefinitionRequest)
  lookup.Handle("textDocument/hover", messages.HandleHover, messages.NewHoverRequest)

  server := server.New(lookup)
  err := server.ListenAndServe()

  if err != nil {
    panic(err)
  }
}
