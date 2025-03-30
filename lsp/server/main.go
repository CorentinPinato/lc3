package server

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"lc3-lsp/analysis"
	"lc3-lsp/rpc"
	"lc3-lsp/structs"
	"log"
	"os"
)

type Server struct {
  scanner *bufio.Scanner
  writer io.Writer
  lookup *HandlerLookup
  logger *log.Logger
  state analysis.State
  publishCh chan *structs.Notification
}

func New(lookup *HandlerLookup) *Server {
  scanner := bufio.NewScanner(os.Stdin)
  scanner.Split(rpc.Split)

  publishCh := make(chan *structs.Notification)
  logger := defaultLogger()

  return &Server{
    scanner: scanner,
    writer: os.Stdout,
    lookup: lookup,
    logger: logger,
    state: analysis.NewState(publishCh, logger),
    publishCh: publishCh,
  }
}

func (s *Server) ListenAndServe() (error) {
  s.logger.Println("Starting lsp server...")
  go s.publish()
  for s.listen() {
    req, err := s.readRequest()
    if err != nil { s.logError(err); continue }

    err = s.handle(req)
    if err != nil { s.logError(err); continue }
  }
  close(s.publishCh)
  s.logger.Println("Stopping server...")
  return nil
}

func (s *Server) publish() {
  s.logger.Println("Starting publisher...")
  for notification := range s.publishCh {
    s.writeResponse(notification)
  }
  s.logger.Println("Stopping publisher...")
}

func (s *Server) listen() bool {
  return s.scanner.Scan()
}

func (s *Server) readRequest() (structs.IRequest, error) {
  method, contents, err := rpc.DecodeMessage(s.scanner.Bytes())
  if err != nil { return nil, err }
  s.logger.Printf("Request: %s", method)
  s.logger.Printf("RequestContent: %s\n", contents)

  NewRequestFunc := s.lookup.GetRequestFunc(method)
  if NewRequestFunc == nil {
    return nil, errors.New(fmt.Sprintf("Method `%s` not handled.", method))
  }
  req := NewRequestFunc()
  json.Unmarshal(contents, &req)

  return req, nil
}

func (s *Server) handle(req structs.IRequest) (error) {
  handleFunc := s.lookup.GetHandleFunc(req.GetMethod())
  response := handleFunc(&s.state, req)

  if response != nil {
    s.writeResponse(response)
  }

  return nil
}

func (s *Server) logError(err error) {
  s.logger.Printf("Error: %s", err)
}

func (s *Server) writeResponse(msg any) {
  jsonMsg, _ := json.Marshal(msg)
  s.logger.Printf("Response: %s\n", jsonMsg)

  reply := rpc.EncodeMessage(msg)
  s.writer.Write([]byte(reply))
}

func defaultLogger() *log.Logger {
  filename := "/home/corentin/Code/vm/lsp/log.txt"
  logFile, err := os.OpenFile(filename, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0666)
  if err != nil {
    panic("Hey, you didn't give me a good file ! XD")
  }
  return log.New(logFile, "[lc3-lsp] ", log.Ldate|log.Ltime|log.Lshortfile)
}
