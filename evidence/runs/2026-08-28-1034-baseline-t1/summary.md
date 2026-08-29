# Run 2026-08-28-1034-baseline-t1

arm **baseline** · model `sonnet` · freeze `4456df103276` · python 3.12.10

| Case | Hidden | Visible | Wall clock | Cost (equiv. API) |
|---|---|---|---|---|
| 001-password-reset | 3/6 | 3/3 | 18s | $0.072 |
| 002-idempotency-key | 3/6 | 4/4 | 33s | $0.089 |
| 003-csv-import | 5/6 | 3/3 | 49s | $0.117 |
| **total** | **11/18 (61.1%)** | **10/10** | **99s** | **$0.278** |
