# GitHub setup for SEO

Paste these into GitHub when you create the repo. The **About** box (description +
topics) is the single highest-leverage SEO lever — GitHub's own search ranks heavily
on it, and Google indexes it. Don't skip it.

## Repo "About" description (the box on the right of the repo page)

> Self-hosted LLM cost analytics & optimization dashboard. Track OpenAI & Anthropic API spend, tokens, and latency with a 3-line Python SDK. Budgets, forecasting, and savings recommendations.

(Keep it under ~120 chars if you want it fully visible; the version above is fine —
GitHub truncates gracefully and still indexes the whole thing.)

## Topics (the tag chips — add all of these)

```
llm
llm-cost
llm-observability
llm-analytics
openai
anthropic
claude
cost-tracking
cost-optimization
finops
ai-cost
token-tracking
fastapi
react
python
self-hosted
dashboard
helicone-alternative
gpt-4o
monitoring
```

GitHub allows up to 20 topics — this list is exactly 20. Each topic is its own
browseable/searchable page on GitHub, so every one is a discovery surface.

## Website field

Point it at your live demo or docs if you deploy one. Otherwise leave blank.

## First commit / release tips

- Make the first line of the README H1 keyword-rich (already done).
- Add a short, keyword-bearing release description when you tag `v0.1.0`.
- If you publish the SDK to PyPI, the PyPI `keywords` in `pyproject.toml` are already set.
