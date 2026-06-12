# Cost Safety

This project is designed for small hackathon demo runs, not unattended large-scale crawling.

## Local Runtime Guards

The application reads these environment variables:

```env
MAX_SOURCES_PER_RUN=3
MAX_INBOX_ITEMS_PER_RUN=5
MAX_CONTENT_CHARS_PER_ITEM=8000
FOUNDRY_RETRY_DELAY_SECONDS=75
```

Use `-1` only when you intentionally want to remove a local cap.

Recommended demo model:

```env
AZURE_AI_MODEL_DEPLOYMENT=o4-mini
```

Use stronger models only for final recording or evaluation if needed.

## Azure Budget

Create a Cost Management budget before running repeated cloud demos. In the Azure Portal:

1. Open Cost Management + Billing.
2. Select the subscription.
3. Go to Budgets.
4. Create a monthly budget, for example 10-20 EUR.
5. Add email alerts at 50%, 80%, and 100%.

## Azure CLI Starting Point

The exact budget command depends on the subscription scope and notification email. This is a template:

```powershell
$subscriptionId = az account show --query id -o tsv
$scope = "/subscriptions/$subscriptionId"

az consumption budget create `
  --budget-name "information-digest-demo-budget" `
  --amount 20 `
  --category Cost `
  --time-grain Monthly `
  --start-date "2026-06-01" `
  --end-date "2026-12-31" `
  --scope $scope
```

After creating the budget, add alerts in the portal so notifications go to the right email address.

## Deployment Guidance

For hackathon demos:

- Prefer Standard or GlobalStandard pay-as-you-go deployments.
- Avoid provisioned throughput unless you intentionally need reserved capacity.
- Keep `sources.json` small.
- Use `demo/seed_demo_data.py` for repeated video takes.
- Run `python -m pytest tests/ -q` before cloud demos.
- Keep retry enabled for small demo deployments, because low-capacity models may return 429 when scoring and synthesis run back-to-back.

## Observed During Smoke Test

The first real tiny E2E run completed successfully, but digest synthesis hit a 429 rate limit on the first attempt. The built-in retry waited 75 seconds and the second attempt succeeded.

This confirms that the low-capacity `o4-mini` deployment is suitable for careful demos, but not for rapid repeated end-to-end runs. Use `demo/seed_demo_data.py` and `demo/run_gold_only.py` for recording loops.
