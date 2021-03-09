
Kubernetes Secrets Control Plane is an open source project that provides a way to manage external secrets as kubernetes resources.

# Releases

| Release | Release Date |
| --- | --- |
| v1.0    |              |
| --- | --- |


# Overview

KSCP is composed of 2 main components:
- An operator responsible for managing the secrets in the backends
- A webhook/webserver responsible for mutating pods to inject an init container and for answering secret read requests

Create secrets in a backend using an ExternalSecret:

```
apiVersion: kscp.io/v1alpha1
kind: ExternalSecret
metadata:
  name: test-vault
  namespace: default
spec:
  backend: vault
  values:
    pass: gen
```

The values inserted here are supposed to be placeholders, not the actual values. Read more (here)[/docs/reference/secrets.md]

Access to the secrets is controlled via kubernetes roles and rolebindings that couple a service account to ExternalSecrets. Example:

```
apiVersion: kscp.io/v1alpha1
kind: SecretBinding
metadata:
  name: test-simple
  namespace: test
spec:
  serviceAccount: test
  secrets:
    - name: test-vault
    - name: test-aws
  template: |
    password={{ test-vault.pass }}
    security_code={{ test-aws.sec_code }}
  target: /tmp/secrets
```

SecretBindings are not required to be used, they are simply an abstraction that is translated into kubernetes roles and role bindings.

Pods can then access the secrets through annotations:
```
apiVersion: v1
kind: Pod
metadata:
  name: test
  namespace: test
  annotations:
    secrets.kscp.io/inject-bindings: "test-vault,test-aws"
...
```

The webhook will deal with expanding this annotation and injecting an init container into the pod, that will deal with retrieving the secrets and rendering the template accordingly.

