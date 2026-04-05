# BillsOne — minimal billing API

FastAPI service with PostgreSQL and Alembic: create and list bills with nested sub-bills, plus optional filters on `GET /bills`.

Please check the journey.md and assumptions.md for more important info in regards to this repo.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL 12+ (empty database you can connect to)

## First-time setup (from scratch)

1. **Go to the project root** — the directory that contains `pyproject.toml`, `alembic.ini`, and this `README.md`.

2. **Create a PostgreSQL database** (and user if needed). Example:

   ```bash
   createdb billsone
   ```

   Match the database name to `DATABASE_NAME` in `.env` below.

3. **Install dependencies and env file:**

   ```bash
   uv sync
   cp .example.env .env
   ```

4. **Edit `.env`** — set `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, and `DATABASE_NAME` so they match your Postgres instance.

5. **Apply the schema** (must succeed before the app can run):

   ```bash
   uv run alembic upgrade head
   ```

6. **Start the API:**

   ```bash
   uv run start
   ```

   Open `http://127.0.0.1:8000/docs` to try the endpoints.

Optional: set `SEED_DUMMY_DATA=true` in `.env` to insert sample bills once when the `bills` table is empty.

## Database migrations (reference)

Create/upgrade schema (same as step 5):

```bash
uv run alembic upgrade head
```

Generate new revisions after model/schema changes in the codebase:

```bash
uv run alembic revision --autogenerate -m "describe_change"
```

After setup, run the API with `uv run start` (see step 6 above). Default: `http://127.0.0.1:8000`, docs at `/docs`.

## Environment variables

| Variable | Meaning |
|----------|---------|
| `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_NAME` | Required — PostgreSQL connection (see `.example.env`). There is no `DATABASE_TYPE` switch; only PostgreSQL is supported. |
| `SEED_DUMMY_DATA` | If `true` / `1` / `yes`, inserts demo bills **once** when the `bills` table is empty. Otherwise no seeding. |

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/bills` | Create a bill and its sub-bills in one payload |
| `GET` | `/bills` | List bills with sub-bills (**paginated**) |

### `POST /bills`

- Each line item may omit `reference` or send `null`. When `reference` is present, it must be unique among all sub-bills (case-insensitive); see `assumptions.md`.

### `GET /bills` behavior (matches the problem statement)

- **`skip` / `limit` paginate bills, not sub-bills.** For example, `limit=10` returns **up to 10 bill objects** in `items`. Each bill still includes its `sub_bills` array (see below).
- **`reference`** (optional) — Case-insensitive **substring** match on `SubBill.reference`.
  - **Which bills appear:** Only bills that have **at least one** sub-bill whose reference matches the substring.
  - **Which sub-bills appear:** For each such bill, **`sub_bills` contains only the sub-bills that match** the substring (non-matching line items on that bill are omitted from the response).
  - If the query parameter `reference` is omitted (or empty after trim), each bill includes **all** of its sub-bills, including line items where `reference` is null (`"reference": null` in JSON).
  - When the `reference` filter **is** applied, rows with `reference` NULL never match and are omitted from each bill’s `sub_bills` list for that response. Characters `%`, `_`, and `\` in the query parameter are treated as **literal** text (not SQL `LIKE` wildcards). An empty or whitespace-only value is treated as **no** reference filter (same as omitting the parameter).
- **`total_from`** — Minimum bill `total` (**inclusive**): only bills with `total >= total_from`.
- **`total_to`** — Maximum bill `total` (**inclusive**): only bills with `total <= total_to`.

### `GET /bills` query parameters (all optional except pagination defaults)

- **`reference`** — See behavior above.
- **`total_from`** — See behavior above.
- **`total_to`** — See behavior above.
- **`skip`** — Number of **bills** to skip from the start of the filtered, ordered list (default `0`, minimum `0`).
- **`limit`** — Maximum number of **bills** to return in this page (default **50**, minimum `1`, maximum **100**).

**Response body:** `{ "items": [ ... ], "total": <int>, "skip": <int>, "limit": <int> }` where `total` is the number of **bills** matching the filters across all pages (not a count of sub-bills).

Filters compose: e.g. `reference`, `total_from`, and `total_to` can be used together.

Implementation note: startup work (e.g. optional DB seed) runs in a FastAPI **lifespan** hook instead of deprecated startup events.

## Submission note

Published to a **public GitHub repository** as required by the exercise; this README is the primary place for assumptions and runbook detail.
