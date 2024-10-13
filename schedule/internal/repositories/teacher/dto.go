package teacher

type TeacherDTO struct {
	Id          int    `json:"id"`
	LastName    string `json:"last_name"`
	FirstName   string `json:"first_name"`
	FathersName string `json:"fathers_name"`
	Initials    string `json:"initials"`
	TgId        int64  `json:"tg_id"`
}

func NewTeacherDto(teacher *Teacher) TeacherDTO {
	return TeacherDTO{
		Id:          teacher.Id,
		LastName:    teacher.LastName,
		FirstName:   teacher.FirstName,
		FathersName: teacher.FathersName,
		Initials:    teacher.Initials,
		TgId:        teacher.TgId,
	}
}
