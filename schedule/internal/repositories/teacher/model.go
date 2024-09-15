package teacher

import (
	"schedule/internal/lib/random"
)

func NewTeacher(lastName, firstName, fathersName string) *Teacher {
	return &Teacher{
		LastName:    lastName,
		FirstName:   firstName,
		FathersName: fathersName,
	}
}

type Teacher struct {
	Id          int    `json:"id"`
	LastName    string `json:"second_name"`
	FirstName   string `json:"first_name"`
	FathersName string `json:"fathers_name"`
	Initials    string `json:"initials"`
	TgId        int64  `json:"tg_id"`
	Code        string `json:"code"`
}

func (t *Teacher) SetCode(size int) {
	t.Code = random.GenerateCode(size)
}

func (t *Teacher) SetId(id int) {
	t.Id = id
}

func (t *Teacher) SetTgId(tgId int64) {
	t.TgId = tgId
}

func (t *Teacher) SetInitials() {
	var firstNameShort, fathersNameShots string

	if t.FirstName != "" {
		firstNameShort = string([]rune(t.FirstName)[0])
		t.Initials = firstNameShort + "."
	}

	if t.FathersName != "" {
		fathersNameShots = string([]rune(t.FathersName)[0])
		t.Initials += fathersNameShots + "."
	}
}
