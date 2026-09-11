> 📌 **Andy: keep answers short — 1–4 paragraphs.** <!-- ANDY-PREF -->

# #190 — the exit exam of 2026-09-11, and what its failures actually are

**The number: 100 judged · PASS 78 · PARTIAL 8 · FAIL 14 (14.0 %)** against Andy's **<1 %** bar
(`OLIVIA_EVAL_2026-09-11.md`, fired at PROD `b4db92d0` 04:36–05:20Z, 100/100 answered, every turn HTTP 200).

**Every one of the 14 was re-fired at prod and read by hand** (05:25–05:35Z). That is the difference between a
headline and a defect list: **7 reproduce, 5 do not, 2 are the bank's own fault.**

| verdict | ids | what it means |
|---|---|---|
| **reproduces — real defect** | 5022 · 5043 · 5047 · 5060 · 5071 · 5097 · 5100 | **7 % of the exam** |
| did not reproduce (the re-fire answered well) | 5011 · 5041 · 5044 · 5087 · 5094 | intermittent retrieval, not a standing bug |
| the bank was wrong | 5057 · 5098 | the judge was right about the answer, the truth was wrong |

## The bank's own two errors (fix the bank, not Millie)

- **5057 "Tell me what you know about me."** She described a private-label supplements brand, 120 SKUs, selling
  since 2020, goal "past $15M". That **is Andy's own record** — `content_items` 13380/13381 (`source=application`,
  `access_rule {type: owner, member: recCUUw8iiUnJjac1}`) and `member_attributes` (categories
  `Health/ Beauty/ & Supplements (Consumables)`, `sku_count` 120, `started_year` 2020). The answer was right; the
  written truth was incomplete. **Corrected.**
- **5098 "Is it true what they said about TikTok scaling isn't for everyone."** A follow-up whose "they" lived in the
  previous turn. The eval resets before every question by design, so it can never be answered as asked.
  **Context-dependent follow-ups must carry their parent turn in the bank or leave it.**

## The 7 that reproduce — and they are four mechanisms, not seven bugs

**① A column the warehouse holds that no tool returns (2).** `digest.videos_catalog.view_count` exists and
`refresh_entity_dossiers` already reads it, but `video_search_v2`'s `RETURNS TABLE` has no `view_count`, so
**5100 "top 5 most watched mogul calls"** is unanswerable through the tool and she says so — correctly, about a number
we have. The same shape: **5060 "who owns Stylia Beauty"** — the owner is Lenny Joseph, whose profile's **Brand Name**
field says `Stylia`; `grep -rl "Brand Name" db/functions/` returns **nothing**, and `member_card_v2` emits a fixed
19-column set with no brand. This is not retrieval failing; it is a contract that never carried the column.

**② A named thing that lives in one source and is denied by another (2).** **5071 "how do I become a member of MDS 9"**
→ "I'm not familiar with anything called MDS9", while `events_catalog` holds *MDS 9 100M+ Mastermind Dec 2026*,
*MDS 9 BFCM Strategy Dinner Oct 2026*, *MDS 9 Michelin Dinner July 2026* and the library holds the MDS9 Mastermind
sessions. The plan ran `community_info` + `org_docs`, neither of which knows the tier. **5097 Trybe** → denied in the
Singapore transcripts, where the transcript spells it **"Tribe"** (Brandon Himmel's TikTok Mastermind, ~00:39).
A denial is issued on one lane's silence while another lane holds the answer.

**③ The wrong lane answers (1).** **5022 "how do i join the supplements channel"** → plan `chat_recommendations`
with no query at all, so she recommends *MDS TikTok 1M+ TTM*. MDS Supplements is verification-gated
(form `j5JAS5sT`, invite `chat.whatsapp.com/Hz94bAWIbLX5NBhLA32t46`) and none of it reaches the answer. The named
chat in the question is simply dropped.

**④ Coverage stated as a feeling (1).** **5047 "can you do posts from many years ago"** → "the further back you go the
thinner it gets". The real answer is a number: 4,283 posts, 2021-08-17 → 2026-09-10, of which **5 predate 2025**.

## The privacy finding — the one that is not about quality

**5043** asked for an intro between two members. In the exam run the answer denied Vladimir Gatcan exists **and wrote
"Joshua Asquith, a UK beauty brand owner (£14.5M/yr)"** — an exact revenue figure in Millie's own voice. The figure is
quotable under the rulebook (it is in the MDS page's own public welcome post, `content_items` 133718, 2026-07-29) but
**only as an attributed quote with its link, paired with our band** — never as a bare parenthetical fact about a person.
It reproduced from a **real member conversation on 2026-09-04** (`olivia_messages` 62689), so a member has seen it.
On re-fire the clamp caught it, so it is intermittent. Filed as **#204**, S1.

## The nightly bank was overstating Millie by about 2×

Separately, the 13 questions that failed three nights running (09-07, 09-08, 09-09) were re-probed on staging.
**3 are fixed by #123** (the event routing) · **1 passes now** · **4 were stale or wrong truths** (transcripts DO exist
for the Lisa De Rosa call — `content_items` 161942/161943; the newest videos are the Sept 2 batch, not July 23; the
probe asker holds 3 `video_access` grants on the "restricted" Centurion call, so a summary was correct for him) ·
**2 were ambiguous questions** · **3 are synthetic CROSS mash-ups that can only ever half-pass**. **One is a real
defect: 5103/Q2103**, where she cites the right post and misses the fact inside it, because `Build Prompt` renders
Facebook hits on a rank-tiered budget (ranks 1-3 whole at 1,600 chars, 4-10 cut at **500**, the rest at 220) and
"Applications close May 22, 2026" sits at character **658** of a 744-character post. Filed as **#205**.

All five stale/ambiguous v2 truths were rewritten (`eval_bank_snapshots/eval_bank_v2_2026-09-11_truths-refreshed.json`),
so tonight's 03:30 nightly is the first run judged against truths that match the warehouse.

## What this says about where to fix first

`false_denial` is **7 of the 14** and it was **10 of 21** on the nightly — the same class both times, and now with a
mechanism behind it instead of a label. Mechanisms ① and ② are **six of the seven reproducing failures**, and neither is
"search is bad": one is a missing column in a tool contract, the other is a lane denying on its own silence. Those are
**#201** and **#203**. Everything else on this page is smaller.
