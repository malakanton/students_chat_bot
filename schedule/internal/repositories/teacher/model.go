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
