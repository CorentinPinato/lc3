package structs

type Command struct {
  Title string `json:"title"`
  Command string `json:"command"`
  Arguments []interface{} `json:"arguments,omitempty"`
}
