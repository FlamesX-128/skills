# Multi-entity decisions

Module is single-entity by default: one entity sharing the module's name. Becomes multi-entity when entities are so tightly coupled they wouldn't make sense apart — canonical example `auth` grouping `user`, `role`, `session`.

Decision rule for "sub-entity vs separate module":

> *Can the entity be referenced without mentioning the parent in the URL?*

- **Yes** -> separate module. Example: `GET /categories/:id` — category is independent of products, so `category` is its own module.
- **No** -> sub-entity of parent. Example: `GET /areas/:id/security/roles/:rid` — role doesn't exist without `area_id`, so `role` lives inside the `area` module.

Single-entity and multi-entity modules follow exactly the same prefix rules; the only difference = how many distinct prefixes appear in the module's files.
