> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# AT → GroupOS tag sync

How member tags get from the **MDS Members DB** into the **GroupOS app**. Last verified live **2026-07-28**.

## The chain

```
Members DB fields  →  {Tags n8n} (formula)  →  AT automation "Tang n8n"  →  n8n webhook  →  GroupOS tags
```

| Piece | ID |
|---|---|
| Members DB base / table | `appou5JVr0WIrioWS` / `tblfwOSROSHfuYUxv` |
| `Tags n8n` (formula, the payload) | `fldmSp9T859pfJ1jp` |
| AT automation "Tang n8n" (watches ONLY that field) | `wfljyfEMavJBMliIq` |
| n8n webhook it POSTs to | `groupos.app.n8n.cloud/webhook/aa86a448-60ee-4e42-adfb-96a04d019d80` |
| GroupOS community | `67011d987a2a81b28438a3d8` |

⚠️ **The n8n workflow behind that webhook is on a DIFFERENT n8n account** — `groupos.app.n8n.cloud` (GroupOS's own). The MDS instance is **`mdsco.app.n8n.cloud`**; that's what the n8n MCP is connected to and where every workflow named here lives. So the consumer can't be read or edited from here — treat it as a black box: it splits `Tags n8n` on `#%$*^` and applies each non-empty piece as a GroupOS tag **by name**, creating the tag if it doesn't exist (proven 2026-07-28).

It **replaces** the member's whole tag set from `Tags n8n` rather than adding to it (Andy, 2026-07-28). Consequence: a tag added by hand in the GroupOS UI is wiped on that member's next sync — Airtable is the full picture.

## The payload format

Three slots, joined by the delimiter `#%$*^`. Empty slots are fine (they've always occurred) — **keep the 3-slot shape**, the consumer splits on the delimiter.

```
SUBSTITUTE({Event Access}, ", ", "#%$*^")
& "#%$*^"
& SUBSTITUTE({Chapter Affiliation}, ", ", "#%$*^")
& "#%$*^"
& {WhatsApp Chat Tags}
```

| Slot | Source field | Notes |
|---|---|---|
| 1 | `Event Access` `fldfvkH6kYUHUyM3P` | multi-select, SUBSTITUTE splits it |
| 2 | `Chapter Affiliation` `fldjb2aq1huGHXC4G` | multi-select, SUBSTITUTE splits it |
| 3 | `WhatsApp Chat Tags` `fldHWMuPnlBcnSgTg` | ALL WhatsApp chats, derived (below) |

Slot 3 was the scratch field `test` until 2026-07-28 — it was pushing a literal **`test`** tag to 719 members in GroupOS. Removed.

## Slot 3: all WhatsApp chat tags (self-updating, no n8n, TWO fields total)

```
WhatsApp Chat Tags  fldHWMuPnlBcnSgTg   (formula)
  SUBSTITUTE(ARRAYJOIN({WhatsApp Chats (live)}, ", "), ", ", "#%$*^")

WhatsApp Chats (live)  fld9AnxtGiI1v6pez   (lookup)
  channels_present, through link "Whatsapp Channels Sync " flduRPYGBCcvbuZWW
  → mirror table tbloYx3PuoIFmULtj (Airtable sync of the WA DB)
  → WA DB appT9TVZWhv7io4CN / tbli8B589iNbsGF0Z
  → rewritten daily 6am ET by n8n "Whapi Sync" Lo45BM43boK1gM19 from real Whapi group membership
```

The tag name **is the chat name** (`MDS TikTok`, `MDS Logistics`). One SUBSTITUTE swaps the `, ` separators for the `#%$*^` delimiter — the same trick slot 1 uses on Event Access — so the whole chat list becomes separate tags in one field.

**A brand-new WhatsApp channel needs ZERO work**: flag it active in the WA DB Chats table, and the next 6am sync puts it in `channels_present`, which flows straight through to a new GroupOS tag. Joins and leaves likewise. Only the **18 chats flagged active** appear — the Whapi sync only reads active ones, which is what keeps the 13 dead/old chats out.

Scaled from a single TikTok tag to all 18 on 2026-07-28 by **repurposing** the old `TikTok Channel Tag` field rather than adding 17 more (Airtable field budget is limited) — net zero new fields.

## State as of 2026-07-28

- **All 18 active chats** now tag automatically. All 18 GroupOS tags created 16:05Z, named exactly after the chats. Includes **MDS Centurion 20M+** — Andy's explicit call; note that tag reveals membership of the invite-only $20M+ channel to anyone who can see tags in the app.
- TikTok specifically: **131 members** (from 132 matched WA rows — Leo Limin has 2 numbers, both in the chat). 98 Current + 22 New + 10 Staff + 1 no-status. Staff included, per Andy; **Andy confirmed 131 in the app UI** — so Staff DO carry app tags.
- **0 members** still emit `test` (was 719).
- The interim `TikTok Channel` tag `6a68c837c32aac77a6a336cf` (15:18Z) is now **superseded by `MDS TikTok`** and carries nobody.
- **Duplicates are harmless**: the 4 members with two phone numbers emit repeated chat names (Leo Limin has `MDS TikTok` twice). GroupOS dedupes by name — verified, only one tag object per name exists.
- **7 WhatsApp numbers in the TikTok chat are unidentified** (no Members DB match): 2 rows with no phone, MDS Bot, Chip Ge (+1 786-863-0984), +63 917 270 3130, +40 738 610 340, +1 862-276-1269.

## Traps

- **The `Whatsapp Channels Sync ` link has a trailing space** in its name. Use the field ID `flduRPYGBCcvbuZWW` when writing via API.
- **The matcher used to drop links silently — FIXED 2026-07-28.** `4B79OVfyT2a9a3Xt` → node `Build Link2 Ops` only writes the Members-side link when `action==='match'|'clear'`, and skips without error when `Find WA Mirror` returns 0 rows (the mirror is a *synced* table and can lag). That left **94 of 579** matched members unlinked, which silently under-tagged them because the tag reads through that link. Backfilled → 579/579, **and** a self-healing `Reconcile: *` branch was added off the `Daily 8am ET` trigger: it lists mirror rows that are `match_status='matched'` but have no `Members` link, re-looks-them-up, and repairs them — logging (never silently skipping) anything it can't fix. It writes the **mirror** side of the two-way link on purpose, so it can only ADD and can never replace a member's link to a second phone's row. Normally returns 0 rows.
- **`WhatsApp Channels` `fldVkWX4IPUKA6kJb`** was a multi-select that *looked* like the WA channel field but was empty on all 3,100 members — **DELETED 2026-07-28**, along with the scratch `test` field `fldN7dOuf80mNgO26`. Use `WhatsApp Chats (live)`.
- **The Chats table's `member_count` is stale** (said 137 when WhatsApp showed 138). Count from `channels_present`, not from that field.
- **GroupOS PAT is public tier**: `tags_list.usage_count` is null and `members_get` returns no tags, so **per-member tag assignment can't be verified from here** — check the app UI (that's how the 131 was confirmed on 2026-07-28).
- A GroupOS tag object is **not deleted** when it stops being applied. The old `test` tag `68083a55f7251cf241690dd1` still exists and needs manual deletion in the app if you want it gone from the list.
