package models

import (
	"fmt"
	"regexp"
)

var SecretValueType = newValueEnum()

type secretValueType struct {
	Gen    *regexp.Regexp
	GenVar *regexp.Regexp
	Manual *regexp.Regexp
}

func newValueEnum() *secretValueType {
	return &secretValueType{
		GenVar: regexp.MustCompile(`gen([0-9]+)$"`),
		Gen:    regexp.MustCompile(`^gen$`),
		Manual: regexp.MustCompile(`^manual$`),
	}
}

type Secret struct {
	Name   string
	Values map[string]string
}

func (s *Secret) CreateSecret() {

}

func (s *Secret) ProcessValues() {
	for _, value := range s.Values {
		switch {
		case SecretValueType.Gen.MatchString(value):
			fmt.Println("Gen")
		case SecretValueType.GenVar.MatchString(value):
			fmt.Println("GenVar")
		case SecretValueType.Manual.MatchString(value):
			fmt.Println("Manual")

		default:
			fmt.Println("HERE")
		}
	}
}
