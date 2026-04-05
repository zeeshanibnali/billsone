
## Assumptions (requirements were partly open-ended)

1. **Database — PostgreSQL** — The service and migrations target **PostgreSQL** (12+). Run `alembic upgrade head` against a Postgres database before starting the app.

2. **Primary keys — UUID** — `bills.id` and `sub_bills.id` are **UUID** (v4-style random IDs from PostgreSQL `gen_random_uuid()` / application defaults). I have done this for future scalability handling. This keeps identifiers opaque and avoids sequential-ID hotspots if we later shard or cluster workloads (IDs are not guaranteed to be time-ordered; use `created_at` for ordering). 

3. **`total` vs sub-bill amounts** — On `POST /bills`, `total` must equal the sum of `sub_bills[].amount` (exact `Decimal` equality in the API). An empty `sub_bills` list is allowed only when `total` is zero.

4. **SubBill `reference` (optional)** — `reference` may be omitted or `null` on a line item; the row is still keyed by `id`. When `reference` is set, it must be **unique among all sub-bills case-insensitively**. The database enforces this with a **partial unique index** on `lower(reference)` **where `reference` is not null**, so many line items may share “no reference” without colliding. Duplicate non-null references in the same request body are rejected with **422** before insert. A conflict with an existing row returns **409** (`ReferenceConflictError`).

5. **Reference size** — `reference` is capped at **10** characters (API validation and `VARCHAR(10)` in PostgreSQL). Migrating from a longer `VARCHAR(128)` may **truncate** existing values to 10 characters (`left(trim(reference), 10)` in the migration); plan backups accordingly.

6. **Money representation** — Bill totals and sub-bill amounts are stored as `NUMERIC(18,4)` and modeled as `Decimal` in the API. **JSON encoding:** Pydantic v2 (used by FastAPI) encodes `Decimal` as a **JSON string**, not a number, so values are not rounded to binary floats. That is intentional for money. (JSON has no native decimal type; strings preserve exact values.) API consumers should parse those strings as decimals, not assume JSON numbers for money fields.

7. **Payload limits** — At most **500** sub-bills per create request (`MAX_SUB_BILLS_PER_BILL` in `bills_constants.py`). Exceeding this returns **422** (Pydantic validation and a service-level check). Adjust the constant if product needs change.

8. **Audit fields** — Schema and Responses include `created_at` and `updated_at` on bills and sub-bills.

9. **Timestamps — UTC** — It is better storing an instant in UTC (or as `timestamptz`, which PostgreSQL normalizes consistently) rather than saving ambiguous local wall times or a separate “timezone” column in the database—clients can convert to any display zone; the backend keeps one comparable timeline for sorting, auditing, and clustering.

10. **Scalability / indexing** — `bills.total` is indexed to support common `total_from` / `total_to` filters.

11. **List pagination (scalability)** — The exercise showed a bare JSON array; this API adds **pagination** for scalability: `GET /bills` returns `{ "items", "total", "skip", "limit" }` where `items` is the page of bills. That avoids unbounded responses as data grows. Default `limit` is **50**, maximum **100** (`DEFAULT_BILLS_PAGE_SIZE` / `MAX_BILLS_PAGE_SIZE` in code). Rows are ordered by bill `created_at` descending, then `id`.

12. **`GET /bills` without a `reference` query parameter** — Each bill includes **all** of its sub-bills, including rows where `reference` is null (those appear with `"reference": null` in JSON). **`GET /bills?reference=...`** still only returns bills that have at least one sub-bill whose non-null reference matches the substring; sub-bills with null `reference` never match that filter and are omitted from `sub_bills` when the filter is active (same as before).

13. **Errors** — Validation issues → **422**. Reference uniqueness conflicts → **409**. Unhandled server failures → **500** with a generic message (details logged server-side).

14. **Response shape** — Example JSON in the original brief sometimes omitted `id` fields; this API always returns stable UUID `id` values for bills and sub-bills, plus the audit timestamps above.

15. **`total_from` / `total_to` query types** — These optional query parameters are validated and parsed as **`Decimal`** (same `max_digits` / `decimal_places` as stored money), then compared to `NUMERIC` in SQL—no binary-float boundary ambiguity for filters.

16. **Rate limiting and reverse proxies** — Per-IP limits use the **direct TCP client address** (`slowapi` + `get_remote_address`). Behind a reverse proxy or load balancer, all traffic can appear to come from one IP unless the ASGI stack is configured to trust **`X-Forwarded-For`** (or similar) and expose the real client IP. Unmatched routes (e.g. **404**), where the framework does not resolve a view handler, are **not** rate-limited by `slowapi` middleware (library behavior).

17. **Alembic downgrades** — Some migrations (e.g. major schema steps) intentionally **do not support `downgrade`** or are destructive; treat production rollback as **restore from backup** or forward-fix, not `alembic downgrade`.

18. **Automated tests** — There is **no pytest (or similar) suite** in this repository yet. Behavior is validated manually and via OpenAPI `/docs`. Adding API tests would reduce regression risk for filters, totals, and conflict paths.
