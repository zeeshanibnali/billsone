"""API limits aligned with schema and README assumptions."""

# Must match SubBillEntity.reference column length (VARCHAR).
REFERENCE_MAX_LENGTH = 10

# Guardrail against oversized payloads; adjust if product requires more line items.
MAX_SUB_BILLS_PER_BILL = 500

# Pagination for GET /bills
DEFAULT_BILLS_PAGE_SIZE = 50
MAX_BILLS_PAGE_SIZE = 100
