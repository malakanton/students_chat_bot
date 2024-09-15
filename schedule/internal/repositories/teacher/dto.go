package teacher

type TeacherDTO struct {
	Id          int    `json:"id"`
	LastName    string `json:"second_name"`
	FirstName   string `json:"first_name"`
	FathersName string `json:"fathers_name"`
	Initials    string `json:"initials"`
	TgId        int64  `json:"tg_id"`
}
