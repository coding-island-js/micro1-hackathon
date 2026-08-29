# Run 2026-08-28-1007-baseline

arm **baseline** · model `sonnet` · freeze `4456df103276` · python 3.12.10

| Case | Hidden | Visible | Wall clock | Cost (equiv. API) |
|---|---|---|---|---|
| 001-password-reset | 3/6 | 3/3 | 17s | $0.072 |
| 002-idempotency-key | 3/6 | 4/4 | 27s | $0.089 |
| 003-csv-import | 5/6 | 3/3 | 41s | $0.114 |
| **total** | **11/18 (61.1%)** | **10/10** | **86s** | **$0.276** |
