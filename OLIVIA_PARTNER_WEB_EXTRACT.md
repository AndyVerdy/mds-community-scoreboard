# Partner web profile extraction (#160) — instructions for the extraction agent

You are given a directory of JSON bundles, one per MDS partner, produced by `scripts/partner_web_crawl.py`:
`{"partner_id","name","website","resolved_url","status","fetched_at","pages":[{"url","title","words","text"}]}`.

For EACH bundle assigned to you, write ONE line of JSON (JSONL) to your output file with exactly this shape:

```
{"partner_id": "<from bundle>", "name": "<from bundle>", "resolved_url": "<from bundle>",
 "crawl_status": "<bundle.status: ok|empty|unreachable|no_website>",
 "summary": "<= 600 chars. What the company says it does, for whom, and how it is different. Third person, plain, no hype words, no marketing adjectives. Start with the company name.",
 "services": ["<concrete service or product line>", ...],            // 3-12 items, short noun phrases
 "markets": ["Amazon US", "Shopify", "Walmart", "TikTok Shop", "EU", ...],  // channels/geographies they serve, as stated
 "pricing": "<pricing model + any concrete numbers stated on the site, e.g. 'from $1,200/mo; custom quotes; free audit'> or null if not stated",
 "people": [{"name": "<full name>", "role": "<title>", "linkedin": "<url or null>"}],   // founders / leadership named on the site; [] if none
 "integrations": ["QuickBooks", "Xero", "Amazon Seller Central", ...],    // tools/platforms they integrate with, as stated
 "proof": ["<case study, named client, award, metric the site states>", ...],   // [] if none
 "founded": "<year>" or null, "hq": "<city, country>" or null,
 "confidence": 0.0-1.0,      // how well the pages support the profile (empty/unreachable -> 0.1)
 "pages": [{"url": "<url>", "words": <n>}]}   // copy from the bundle, text dropped
```

Rules:
- Use ONLY what the pages say. Nothing from your own knowledge about the company. If a field is not on the pages, use null / [].
- This is what the PARTNER says about itself. Never add opinions, ratings or member judgment.
- Keep every string in plain English, no emojis, no exclamation marks, no quotes of marketing slogans.
- Bundles with status `empty`, `unreachable` or `no_website` still get a line: summary = "No usable website content (<status>)", other fields null/[], confidence 0.1.
- Never skip a bundle. Never invent a partner_id. One JSON object per line, valid JSON, UTF-8.
- Do not read more than one bundle at a time into context; process them in order and append to the output file as you go (`>>`).

Work method (cheap and deterministic):
1. `ls <dir>` to get your files. 2. For each file: `python3 -c` to print `name, resolved_url, status` and the first ~2,500 words of the pages, pricing/about pages first (the bundle already caps text). 3. Write the JSON line. 4. Move on.
Report at the end: number of lines written, number with confidence < 0.5, and the 5 partners with the richest people lists.
