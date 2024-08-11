package subject

type Subject struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
	Code string `json:"code"`
}

func (s *Subject) SetIdAndCode(id int, code string) {
	s.Id = id
	s.Code = code
}
