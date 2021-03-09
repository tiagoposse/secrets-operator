
# Vault backend

Authentication and authorization to Vault has to be configured for both the injector and the operator. Currently, only (kubernetes engine auth)[https://www.vaultproject.io/docs/auth/kubernetes] is supported.

## Policies

```
vault policy write kscp-injector - <<EOF
path "kv/data/*" {
  capabilities = ["read"]
}
EOF
```

```
vault policy write kscp-operator - <<EOF
path "kv/data/*" {
  capabilities = ["read","create","update","delete"]
}
EOF
```

## Roles

```
vault write auth/kubernetes_test/role/kscp-operator \
        bound_service_account_names=kscp-operator \
        bound_service_account_namespaces=kscp \
        policies=kscp-operator \
```

```
vault write auth/kubernetes_test/role/kscp-injector \
        bound_service_account_names=kscp-injector \
        bound_service_account_namespaces=kscp \
        policies=kscp-injector \
        ttl=24h
```