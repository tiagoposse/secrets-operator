# Secrets

```
spec:
  values: {} # required the values for the secret
  backend: "" # required. aws, vault or gcp
  path: "" # default depends on backend
  maxVersions: 0 # max number of versions
  replication: "" # replication strategy
```