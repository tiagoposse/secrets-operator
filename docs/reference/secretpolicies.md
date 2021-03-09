
# Secret policies

Policies control the creation and update of secrets via regex patterns. Patterns can be defined for both allowing and rejecting secret paths.
Currently only secrets paths are checked.

```
allow:
  - pattern: "" # required. pattern to match the secret path with
    backends: [] # optional. backends this pattern applies to
reject:
  - pattern: "" # required. pattern to match the secret path with
    backends: [] # optional. backends this pattern applies to
```