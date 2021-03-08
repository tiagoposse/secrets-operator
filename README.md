# secrets-operator


# Installing the plugin



# Using Vault backend

Currently only authentication via kubernetes role is supported.

```
backends:
  vault:
    enabled: true
    address: http://vault.vault.svc.cluster.local
    token_path: /vault/secrets/token
```

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
