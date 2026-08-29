# Run 2026-08-28-1038-baseline-t3

arm **baseline** · model `sonnet` · freeze `4456df103276` · python 3.12.10

| Case | Hidden | Visible | Wall clock | Cost (equiv. API) |
|---|---|---|---|---|
| 001-password-reset | 3/6 | 3/3 | 21s | $0.078 |
| 002-idempotency-key | 3/6 | 4/4 | 23s | $0.079 |
| 003-csv-import | 5/6 | 3/3 | 40s | $0.093 |
| **total** | **11/18 (61.1%)** | **10/10** | **84s** | **$0.249** |
