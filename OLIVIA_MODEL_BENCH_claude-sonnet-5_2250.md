# Model bench — claude-sonnet-5 — 7 questions

- **Answer quality:** 7 judged · PASS 5 · PARTIAL 0 · **FAIL 2 (28.6%)**
- **Cost:** $0.5306 total · $0.07580 per answer cold · **$0.01060 per answer steady-state** (warm prefix, cache-write excluded — the number production actually pays; list prices, no intro discount)
- **Latency:** median 8.9s · max 19.8s
- **Tokens:** fresh in 100 · cached in 97,017 (100% cached) · out 2,985 · 15 model calls (2.1 per answer)
- **Blended rate:** $0.74 per 1M tokens (all tokens, cache discounts included — comparable to the console's own number)
- **Model time vs tool time:** model 7.5s per answer, rest is Supabase/Voyage (identical infrastructure for both vendors)
- **Forced first fetch:** per model
- **Loop errors:** 0

- **FAIL** Q3042 [ORGANIC/EVENTS] Recommend some calls for me to attend
  - Invents specific calls and schedule instead of admitting the live calls calendar isn't accessible yet.
- **FAIL** Q3015 [ORGANIC/EVENTS] I'm registered for the upcoming summit in Singapore
  - Irrelevant TikTok partner deals dumped before addressing the actual Singapore summit question, which is thread-lost/dodge.
