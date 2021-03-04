package vault

import (
	"fmt"
	"os"

	"github.com/hashicorp/vault/api"
)

type VaultSecretManager struct {
	Client *api.Client
}

var token = os.Getenv("TOKEN")
var vault_addr = os.Getenv("VAULT_ADDR")

func newVaultSecretManager() *VaultSecretManager {
	config := &api.Config{
		Address: vault_addr,
	}

	client, err := api.NewClient(config)
	if err != nil {
		fmt.Println(err)
		return nil
	}

	client.SetToken(token)

	return &VaultSecretManager{
		Client: client,
	}
}

func (v *VaultSecretManager) CreatePolicy(pol *VaultPolicy) {
	v.Client.PutPolicy(pol.Name, pol.RulesToString())
}

func (v *VaultSecretManager) CreateSecret(secret *VaultSecret) {
	v.Client.Logical().Write(secret.GetFullPath(), secret.Spec.Values)
}

func (v *VaultSecretManager) CreateSecretIfNotExists(secret *VaultSecret) {

}

func (v *VaultSecretManager) CreateRole(role *VaultRole) {

}
