package teacher

import (
	"schedule/internal/lib/random"
)

type Teacher struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
	TgId int64  `json:"tg_id"`
	Code string `json:"code"`
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
