package rpc_test

import (
	"lc3-lsp/rpc"
	"testing"
)

type EncodingExample struct {
  Testing bool
}

func TestEncode(t *testing.T) {
  expected := "Content-Length: 16\r\n\r\n{\"Testing\":true}"
  actual := rpc.EncodeMessage(EncodingExample{Testing: true})
  if expected != actual {
    t.Fatalf("Expected: %s, Actual: %s", expected, actual)
  }
}

func TestDecode(t *testing.T) {
  msg := "Content-Length: 15\r\n\r\n{\"method\":\"hi\"}"
  method, content, err := rpc.DecodeMessage([]byte(msg))
  contentLength := len(content)
  if err != nil { panic(err) }
  if contentLength != 15 {
    t.Fatalf("Expected: %d, Actual: %d", 15, contentLength)
  }
  if method != "hi" {
    t.Fatalf("Expected: %s, Actual: %s", "hi", method)
  }
}
