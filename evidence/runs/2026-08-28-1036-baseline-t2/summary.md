# Run 2026-08-28-1036-baseline-t2

arm **baseline** · model `sonnet` · freeze `4456df103276` · python 3.12.10

| Case | Hidden | Visible | Wall clock | Cost (equiv. API) |
|---|---|---|---|---|
| 001-password-reset | 3/6 | 3/3 | 22s | $0.079 |
| 002-idempotency-key | 3/6 | 4/4 | 23s | $0.082 |
| 003-csv-import | 5/6 | 3/3 | 44s | $0.108 |
| **total** | **11/18 (61.1%)** | **10/10** | **90s** | **$0.269** |
