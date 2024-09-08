package teacher

type TeacherDTO struct {
	Id       int    `json:"id"`
	Name     string `json:"name"`
	FullName string `json:"full_name"`
	TgId     string `json:"tg_id"`
}
