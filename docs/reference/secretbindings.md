
# Secret bindings

Secret bindings serve two purposes:
- tie service accounts to secrets (via kubernetes roles and rolebindings)
- provide the mutating webhook information to inject into the init container, listing which secrets to fetch and how to render them (via special annotations)

They are not strictly required to be used, since both purposes can be achieved in another way, but they bring bigger flexibility.

Gotchas:
- A pod can use more than one secret binding at a time.
- A bind can only be rendered once per pod

```
spec:
  serviceAccount: "" # required. the service account that accesses the secrets
  secrets: [
    { name }
  ] # required. list of secrets to be loaded into the accessor pod
  template: "" # optional. Rendering template for the secrets.
  target: "" # optional. Path where to render the template, defaults to /kscp/secrets/<bind name>
```