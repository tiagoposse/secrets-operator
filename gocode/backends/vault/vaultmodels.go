package vault

import (
	"fmt"
	"strings"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type VaultSecret struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec VaultSecretSpec `json:"spec"`
}

type VaultSecretSpec struct {
	Path       string
	MountPoint string
	Values     map[string]string
}

type VaultSecretList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []VaultSecret `json:"items"`
}

func (secret *VaultSecret) GetFullPath() string {
	return fmt.Sprintf("%s/%s", secret.Spec.MountPoint, secret.Spec.Path)
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type VaultPolicy struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec VaultPolicySpec `json:"spec"`
}

type VaultPolicySpec struct {
	Rules []VaultPolicyRule
}

type VaultPolicyRule struct {
	Path         string
	Capabilities []string
}

type VaultPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []VaultPolicy `json:"items"`
}

func (pol *VaultPolicy) RulesToString() string {
	var ruleDescription strings.Builder

	for _, rule := range pol.Spec.Rules {
		capsWithQuotes := make([]string, len(rule.Capabilities))

		for i, cap := range rule.Capabilities {
			capsWithQuotes[i] = fmt.Sprintf("\"%s\"", cap)
		}

		fmt.Fprintf(&ruleDescription, "path \"%s\" {\n  capabilities = [%s]\n}\n", rule.Path, strings.Join(capsWithQuotes, ","))
	}

	return ruleDescription.String()
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type VaultRole struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec VaultRoleSpec `json:"spec"`
}

type VaultRoleSpec struct {
	BoundServiceAccounts []string
	BoundNamespaces      []string
	Policies             []string
}

type VaultRoleList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`
	Items           []VaultRole `json:"items"`
}
