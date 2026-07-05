# Multi-entity decisions

Module single-entity by default: one entity sharing module name. Becomes multi-entity when entities tightly coupled — wouldn't make sense apart. Canonical example: `auth` groups `user`, `role`, `session`.

Decision rule for "sub-entity vs separate module":

> Entity referenceable without parent in URL?

- Yes -> separate module. Example: `GET /categories/:id` — category independent of products, own module.
- No -> sub-entity of parent. Example: `GET /areas/:id/security/roles/:rid` — role needs `area_id`, lives inside `area` module.

Single-entity and multi-entity modules follow same prefix rules. Only difference = number of distinct prefixes in module files.
