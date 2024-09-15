package parser_tools

import (
	"regexp"
	"strings"
)

func PrepareLessonString(cellData interface{}) string {
	cellDataString := strings.TrimSpace(cellData.(string))
	noNewLines := strings.ReplaceAll(cellDataString, "\n", " ")
	noDoubleSpace := strings.Join(strings.Fields(noNewLines), " ")
	//return strings.TrimSpace(noDoubleSpace)
	return noDoubleSpace
}

func CleanUpSubjectString(s, subjectCode string, re *regexp.Regexp) string {
	subjName := strings.ReplaceAll(s, subjectCode, "")
	subjName = re.ReplaceAllLiteralString(subjName, "")
	subjName = strings.ReplaceAll(subjName, "()", "")
	subjName = strings.ReplaceAll(subjName, "( )", "")
	return strings.TrimSpace(subjName)
}
