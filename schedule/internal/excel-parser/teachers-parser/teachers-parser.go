package teachers_parser

import (
	"fmt"
	"github.com/xuri/excelize/v2"
	"schedule/internal/repositories/teacher"
	"strings"
)

func NewTeachersExcel(filePath string) *TeachersExcel {
	return &TeachersExcel{
		filePath: filePath,
	}
}

type TeachersExcel struct {
	filePath           string
	file               *excelize.File
	TeachersList       []string
	ParsedTeachersList []*teacher.Teacher
}

func (te *TeachersExcel) ReadExcelFile() error {
	f, err := excelize.OpenFile(te.filePath)
	if err != nil {
		return err
	}

	defer func() {
		if err := f.Close(); err != nil {
			fmt.Printf("failed to close excel file %s error: %s", te.filePath, err.Error())
		}
	}()

	te.file = f

	return nil
}

func (te *TeachersExcel) GetTeachersList() error {
	sheetName := te.file.GetSheetList()[0]

	rows, err := te.file.GetRows(sheetName)
	if err != nil {
		return err
	}

	for _, row := range rows {
		if len(row) == 0 {
			continue
		}
		if row[0] == "" || row[0] == " " {
			continue
		}
		te.TeachersList = append(te.TeachersList, row[0])
	}
	return nil
}

func (te *TeachersExcel) ParseTeachersNames() error {
	for _, rawName := range te.TeachersList {
		var lastName, firstName, fathersName string

		splitted := strings.Split(rawName, " ")
		switch len(splitted) {
		case 1:
			lastName = splitted[0]
		case 2:
			lastName = splitted[0]
			firstName = splitted[1]
		default:
			lastName = splitted[0]
			firstName = splitted[1]
			fathersName = splitted[2]
		}
		fmt.Println(lastName, firstName, fathersName)

		t := teacher.NewTeacher(lastName, firstName, fathersName)

		te.ParsedTeachersList = append(te.ParsedTeachersList, t)
	}
	return nil
}
