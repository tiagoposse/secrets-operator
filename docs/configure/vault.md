# Vault

## Requirements

Policy for both injector and controller:
```
vault policy write kscp - <<EOF
path "kv/data/*" {
  capabilities = ["read"]
}
EOF
```

Kubernetes role for the injector:
```
vault write auth/kubernetes/role/kscp-injector \
    bound_service_account_names=kscp-injector \
    bound_service_account_namespaces=secretsplane \
    policies=kscp \
    ttl=1h
```

Kubernetes role for the controller:
```
vault write auth/kubernetes/role/kscp-controller \
    bound_service_account_names=kscp-controller \
    bound_service_account_namespaces=secretsplane \
    policies=kscp \
    ttl=1h
```

## Values

```
operator:
  podAnnotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: kscp-operator
    vault.hashicorp.com/agent-inject-token: "true"

injector:
  podAnnotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: kscp-injector
    vault.hashicorp.com/agent-inject-token: "true"

backends:
  vault:
    enabled: true
    address: https://vault.example.com
    token_path: /vault/secrets/token
    defaultMountPoint: kv
```