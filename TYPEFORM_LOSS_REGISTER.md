# Typeform deletion — loss register

**What happened:** on 2026-08-08 I deleted 250 Typeforms via the API as a "prune" of low-response forms. API deletes are permanent and bypass the trash. Andy's ruling after the fact: **never delete from Typeform, it is a source of record.** Prune scripts removed in `1aa0951`.

> **Corrected 2026-08-10.** The first two versions of this file claimed 96 forms lost 465 responses with no copy anywhere. **That was wrong.** The `typeform_backups/*.json` files are keyed `{form_id: {definition, responses, title}}` and I only ever read `definition` — so I reported the answers as gone while they sat in the same file. Recounted below from the actual backup contents.

| | forms | responses |
|---|---|---|
| deleted | 250 | — |
| had zero responses | 129 | 0 |
| **fully recoverable from `typeform_backups/`** | **102** | **512** |
| partially backed up | 0 | 0 saved, 0 lost |
| **no copy anywhere — genuinely lost** | **19** | **92** |
| **total responses unrecoverable** | | **92** |


**To export any of them:** the backups hold complete response objects (answers, emails, timestamps, hidden fields). `typeform_restored_csv/` has the three Channel Call Opt-ins as a worked example; the same loop exports any other form.


## ❌ No copy anywhere — genuinely lost (19)
The only responses this deletion actually destroyed.

| form id | title | responses | in backup | file |
|---|---|---|---|---|
| `Tugcd47E` | Charles Chakkalo _ Hot Seat 1 _ Session Survey _ Summit Milan | 9 | 0 | — |
| `GIwhKbyS` | Inspire 2026 _ Session Survey _ Isaac Medeiros - Affiliate Network on Youtube Shop | 9 | 0 | — |
| `aEu5UlJK` | MDS Inspire 2025 - Exhibition | 9 | 0 | — |
| `sGvCDqpp` | Michael Corrigan _ Session Survey _ Summit Milan | 9 | 0 | — |
| `E2uRJD3Q` | Inspire 2026 _ Session Survey _Bryce Alderson - Amazon Marketshare vs Margin | 8 | 0 | — |
| `nqGvqZXY` | Matthew Kalatsky _ Hot Seat 2 _ Session Survey _ Summit Milan | 8 | 0 | — |
| `mJqqtCfT` | Inspire 2026 _ Session Survey _ Eli Kroll - Customer Experience | 5 | 0 | — |
| `ZTYnU3ie` | MDS X Registration Creation | 5 | 0 | — |
| `MBZf37WV` | Inspire 2026 _ Session Survey _ Matt Bertrand - Managing Large Catalogs | 4 | 0 | — |
| `JerGboPG` | Partner Census Form | 4 | 0 | — |
| `Frq5qQpG` | Squad Registration (paid) | 4 | 0 | — |
| `Isd2kuyJ` | TikTok Shop City Tour Exhibitor Info | 4 | 0 | — |
| `Vr5FwcZW` | Event Registration Form - Mexico City | 3 | 0 | — |
| `uzixNKox` | Inspire 2026 _ Session Survey _ Alyssa Riccardelli -  Marketplace Success | 3 | 0 | — |
| `ReM6ToGB` | Inspire 2026 _ Session Survey _ Meher Patel (Hector AI) - What an Amazon MCP API is & how to use it | 3 | 0 | — |
| `PWZkWf7H` | MDS Summit Singapore 2026 Hack Contest | 2 | 0 | — |
| `PrJ9ZR1t` | Event Registration Form - Lisbon | 1 | 0 | — |
| `R5aFj6Ye` | Leo Limin _ Session Survey _ Summit Milan | 1 | 0 | — |
| `qLyLlGG1` | MDS Inspire 2026 Hack Contest | 1 | 0 | — |

## ✅ Fully recoverable from the backups (102)
Form gone from Typeform; every response sits on disk and can be exported to CSV on demand.

| form id | title | responses | in backup | file |
|---|---|---|---|---|
| `Hflzbz9C` | Advisory Council Agreement 8-4-2020 | 9 | 9 | batchH_2026-08-07.json |
| `B0wpgzt9` | Large SKU Channel Call Opt-in | 9 | 9 | batchH_2026-08-07.json |
| `GGESbUI5` | Member of the month - July 2025 | 9 | 9 | batchH_2026-08-07.json |
| `x7FctwBF` | Member of the month - October 2024 | 9 | 9 | batchH_2026-08-07.json |
| `kwwfCUtS` | Membership Level Change | 9 | 9 | batchH_2026-08-07.json |
| `k2ULAIkZ` | Resellers Channel Call Opt-in | 9 | 9 | batchH_2026-08-07.json |
| `zh5oWBow` | MDS Inspire Rooming Request | 9 | 9 | batchCG_2026-08-07.json |
| `dLxrg0RY` | Member issues 2026 | 9 | 9 | batchCG_2026-08-07.json |
| `DCM7fKNt` | UK Chapter Boardroom Ser 2025 | 9 | 9 | batchCG_2026-08-07.json |
| `alDsokGC` | Accelerator Channel Call Opt-in | 8 | 8 | batchH_2026-08-07.json |
| `IaRcNdOZ` | MDS Summit Singapore 2026 - Company Information | 8 | 8 | batchH_2026-08-07.json |
| `e32kNktM` | MVP Posts - Q2 2025 | 8 | 8 | batchH_2026-08-07.json |
| `dQdts0dF` | Member of the month - August 2025 | 8 | 8 | batchH_2026-08-07.json |
| `zdMeEnfT` | Member of the month - June 2025 | 8 | 8 | batchH_2026-08-07.json |
| `InJGjZ` | Order Follow Up | 8 | 8 | batchH_2026-08-07.json |
| `HFQa9TMA` | 2026 Ideas & Priorities | 8 | 8 | batchCG_2026-08-07.json |
| `ACOyOnvB` | MDS Inspire Lounge | 8 | 8 | batchCG_2026-08-07.json |
| `I5R0XTNB` | PacNorthWest Boardroom Meetup Oct 2024 | 8 | 8 | batchCG_2026-08-07.json |
| `caB4tKxu` | PacNorthWest Chapter Boardroom May 2026 | 8 | 8 | batchCG_2026-08-07.json |
| `sngkZSBx` | My branded typeform | 7 | 7 | batch2_not_in_warehouse_2026-08-07.json |
| `j0PYJRRO` | My branded typeform | 7 | 7 | batch2_not_in_warehouse_2026-08-07.json |
| `SpMG1PNK` | Member of the month - January 2025 | 7 | 7 | batchH_2026-08-07.json |
| `FAvSk2bQ` | Member of the month - May 2025 | 7 | 7 | batchH_2026-08-07.json |
| `ojtmZEOB` | Member of the month - October 2025 | 7 | 7 | batchH_2026-08-07.json |
| `UQrQ4QB0` | Public Events | 7 | 7 | batchH_2026-08-07.json |
| `qeWglJBY` | TikTok Shop City Tour Creator Campaign | 7 | 7 | batchH_2026-08-07.json |
| `b6ZkDAbu` | MDS App - Team Member Feature Survey | 7 | 7 | batchCG_2026-08-07.json |
| `CcHjzOm7` | NorthTex Dinner Poll | 7 | 7 | batchCG_2026-08-07.json |
| `NyT6G6qV` | Orange Co Chapter Boardroom April 2026 | 7 | 7 | batchCG_2026-08-07.json |
| `za8oU4Rf` | Orange County Boardroom May 2025 | 7 | 7 | batchCG_2026-08-07.json |
| `xLml7iw1` | Singapore Excursions | 7 | 7 | batchCG_2026-08-07.json |
| `HD43M46d` | Chapter Holiday Party 2025 | 6 | 6 | batchH_2026-08-07.json |
| `VBgcsZjM` | Member of the month - December 2024 | 6 | 6 | batchH_2026-08-07.json |
| `eNxfvptq` | Member of the month - February 2025 | 6 | 6 | batchH_2026-08-07.json |
| `Mj7yQmAp` | Member of the month - February 2026 | 6 | 6 | batchH_2026-08-07.json |
| `vOSxvwU2` | Member of the month - June 2026 | 6 | 6 | batchH_2026-08-07.json |
| `q87bOta8` | Member of the month - May 2026 | 6 | 6 | batchH_2026-08-07.json |
| `GtOEC9H1` | Member of the month - November 2024 | 6 | 6 | batchH_2026-08-07.json |
| `k8DS6L76` | Member of the month - November 2025 | 6 | 6 | batchH_2026-08-07.json |
| `tT20VMAn` | Member of the month - September 2024 | 6 | 6 | batchH_2026-08-07.json |
| `clCJcnLg` | New Member #ValueAdd Challenge | 6 | 6 | batchH_2026-08-07.json |
| `R9lbPgwB` | Podcast Subscriptions | 6 | 6 | batchH_2026-08-07.json |
| `oLqAwHYl` | Puerto Rico Charity Brainstorming | 6 | 6 | batchH_2026-08-07.json |
| `FTrYGRAf` | Site Inspection for MDS Events | 6 | 6 | batchH_2026-08-07.json |
| `uhRy0TpH` | TikTok Shop City Tour Lead Capture | 6 | 6 | batchH_2026-08-07.json |
| `GNV87msI` | TikTok Shop City Tour Shipping Details | 6 | 6 | batchH_2026-08-07.json |
| `g35bPTZT` | Research Survey For UK & European Sellers | 6 | 6 | batchCG_2026-08-07.json |
| `MqOelnmO` | San Diego Chapter Boardroom Bonding April 2026 | 6 | 6 | batchCG_2026-08-07.json |
| `mr1BytNT` | UK Chapter Boardroom June 2026 | 6 | 6 | batchCG_2026-08-07.json |
| `zGuOXecA` | UK Chapter Boardroom Nov 2025 | 6 | 6 | batchCG_2026-08-07.json |
| `VSq4R50C` | MDS Chapter Packs 2023-Partners (Part 2) | 5 | 5 | batch2_not_in_warehouse_2026-08-07.json |
| `y1mIeM6q` | Fast Moss Conference Booth | 5 | 5 | batchH_2026-08-07.json |
| `Ox48wSj1` | Member of the month - April 2025 | 5 | 5 | batchH_2026-08-07.json |
| `BfpYWNcl` | Member of the month - March 2025 | 5 | 5 | batchH_2026-08-07.json |
| `kFWb3DAi` | Member of the month - September 2025 | 5 | 5 | batchH_2026-08-07.json |
| `l9RTS0Jd` | SoTex Chapter Event Date | 5 | 5 | batchH_2026-08-07.json |
| `VEu0zGg4` | TikTok Shop Connection | 5 | 5 | batchH_2026-08-07.json |
| `Kd3b1puH` | Feedback Survey for MDS Events | 5 | 5 | batchCG_2026-08-07.json |
| `tIT3RVHy` | Intro Post-Call Survey | 5 | 5 | batchCG_2026-08-07.json |
| `uCPIuQwj` | Knowledge Base Creation Survey | 5 | 5 | batchCG_2026-08-07.json |
| `D3fuMxTH` | PacNorthWest Chapter Boardroom Nov '25 | 5 | 5 | batchCG_2026-08-07.json |
| `tTLfoS6g` | San Diego Boardroom April 2025 | 5 | 5 | batchCG_2026-08-07.json |
| `Hk8Qe4tG` | Partner Form - MDS Podcast Guest | 4 | 4 | batch2_not_in_warehouse_2026-08-07.json |
| `De53bvAh` | Lisbon Tuktuk Questions | 4 | 4 | batchH_2026-08-07.json |
| `D9oBpYIN` | MDS Day NYC 2025 | 4 | 4 | batchH_2026-08-07.json |
| `MMh97pE2` | MDS Invest Criteria | 4 | 4 | batchH_2026-08-07.json |
| `H1mrCOxi` | Member of the month - January 2026 | 4 | 4 | batchH_2026-08-07.json |
| `BlkSprMP` | New Member Application - Shopify | 4 | 4 | batchH_2026-08-07.json |
| `mKWwYRsJ` | Submit Document | 4 | 4 | batchH_2026-08-07.json |
| `AcLeYQQR` | TikTok Shop City Tour Lead List | 4 | 4 | batchH_2026-08-07.json |
| `v2RCFUd9` | YKUNI Website Contact Form | 4 | 4 | batchH_2026-08-07.json |
| `tboGRBag` | Airable Survey | 4 | 4 | batchCG_2026-08-07.json |
| `ZsztXrmC` | SoTex Chapter Boardroom Bonding April 2026 | 4 | 4 | batchCG_2026-08-07.json |
| `BH0cC0KY` | Channel Moderator monthly calls | 3 | 3 | batchH_2026-08-07.json |
| `xIu4spor` | MDS 10 Week Challenge | 3 | 3 | batchH_2026-08-07.json |
| `jTZ44G62` | Puerto Rico - Ecompreneur event date poll | 3 | 3 | batchH_2026-08-07.json |
| `pYTa3iyK` | SCFest Miami 2026 Conference Booth 2026 | 3 | 3 | batchH_2026-08-07.json |
| `eL29scDW` | First Onboarding Survey | 3 | 3 | batchCG_2026-08-07.json |
| `WMwRPPRr` | Member Satisfaction Draft | 3 | 3 | batchCG_2026-08-07.json |
| `m1dejwtP` | MDS Partner Perk Approval Form | 2 | 2 | batch2_not_in_warehouse_2026-08-07.json |
| `iqIe7GRm` | Business Branding & Identity Questionnaire | 2 | 2 | batchH_2026-08-07.json |
| `Nlxo0YMD` | Error 403 | 2 | 2 | batchH_2026-08-07.json |
| `DKndwlDE` | Error 404 | 2 | 2 | batchH_2026-08-07.json |
| `lc9aX4aA` | Women's Chapter Virtual Call Time | 2 | 2 | batchH_2026-08-07.json |
| `hKbALiFg` | DTC Mastermind Sep 2025 | 2 | 2 | batchCG_2026-08-07.json |
| `TfGjJOWJ` | Lunch on MDS | 2 | 2 | batchCG_2026-08-07.json |
| `jdgVSHVC` | Soflo boardroom 4 | 2 | 2 | batchCG_2026-08-07.json |
| `S9BMpqQw` | For Testing - Komal | 1 | 1 | batch2_not_in_warehouse_2026-08-07.json |
| `szz8pilk` | Partner Offer Form | 1 | 1 | batch2_not_in_warehouse_2026-08-07.json |
| `imAQQzd7` | Site Inspection for MDS Events (test) | 1 | 1 | batch2_not_in_warehouse_2026-08-07.json |
| `H3K535qn` | Amazon Buy With Prime Form | 1 | 1 | batchH_2026-08-07.json |
| `Tc2DgvwC` | Community Contribute | 1 | 1 | batchH_2026-08-07.json |
| `BC34iFXw` | Logistics Channel Call Opt-in | 1 | 1 | batchH_2026-08-07.json |
| `NENqozp9` | MDS Annual Census 2026 (v2) | 1 | 1 | batchH_2026-08-07.json |
| `bE21HxuC` | MDS Invest Due Diligence | 1 | 1 | batchH_2026-08-07.json |
| `VPClAOYU` | My new form | 1 | 1 | batchH_2026-08-07.json |
| `YaYktl9K` | Pre Member Application | 1 | 1 | batchH_2026-08-07.json |
| `PYxpuBrl` | Squad Archetype | 1 | 1 | batchH_2026-08-07.json |
| `M6YjqMVg` | Creative Team Feedback | 1 | 1 | batchCG_2026-08-07.json |
| `lFLFxPGT` | MDS NPS | 1 | 1 | batchCG_2026-08-07.json |
| `LVFf9Ikh` | MDS Provider Feedback | 1 | 1 | batchCG_2026-08-07.json |
| `OhfEuxWN` | Post Onboarding Survey for Community Platform | 1 | 1 | batchCG_2026-08-07.json |

## Deleted with zero responses (129)
No submitted data existed.

| form id | title | responses | in backup | file |
|---|---|---|---|---|
| `ruTtQKjZ` | 1. Free gift - Email | 0 | 0 | — |
| `ZA7aMOIU` | 10% off discount | 0 | 0 | — |
| `pqLN9Ws0` | 2026 MDS Invest Mastermind | 0 | 0 | — |
| `sTPhHahv` | 3. Free Gift - Social | 0 | 0 | — |
| `ZRv1WDR7` | APAC Chapter Bali Retreat 2025 | 0 | 0 | — |
| `vqDFPdf4` | Accelerator Channel Verification | 0 | 0 | — |
| `chxTXfhI` | Add on Networking Experiences (Partners) | 0 | 0 | — |
| `f7fUuELN` | Aggregator Raise Questionnaire | 0 | 0 | — |
| `MUgbfwYA` | Anita QR Landing Page | 0 | 0 | — |
| `vLMf7fSS` | Annual Census Master | 0 | 0 | — |
| `kHmYSMJH` | Brand Form | 0 | 0 | — |
| `ov48awRc` | Central Florida Chapter Boardroom April 2026 | 0 | 0 | — |
| `hY5tYXgv` | Chapter NPS Score | 0 | 0 | — |
| `q1UYb62m` | Eparé Product Tester Form NEW 4/6/22 | 0 | 0 | — |
| `AH5Q22dF` | Eparé Product Tester Form NEW 4/6/22 (copy) | 0 | 0 | — |
| `itUqlKGI` | Ephraim Ausch _ Session Survey _ Summit Ojai | 0 | 0 | — |
| `vjVLajJX` | Europe Chapter AI Mastermind June 2026 | 0 | 0 | — |
| `crzMviwH` | Europe Chapter Mallorca Retreat | 0 | 0 | — |
| `zn73QZXG` | Fireside Chat with Casey Gauss, founder & CEO of Viral Launch | 0 | 0 | — |
| `UwevTTJq` | Inspire 2026 _ Hack Contest 2026 Survey | 0 | 0 | — |
| `Die3Ampr` | Inspire 2026 _ Session Survey _ Fernando Becattini, Matt Greene, and Alex Yale - Retail Panel | 0 | 0 | — |
| `e3aaKIB2` | Inspire 2026 _ Session Survey _ Scott Deetz | 0 | 0 | — |
| `lDqHwZID` | Inspire 2026 _ Session Survey _ Speaker | 0 | 0 | — |
| `hl8Jbn94` | Inspire 2026 _ Session Survey _Max Mikhaylenko, Gia Mezz and Will August - Scaling Modern Brands | 0 | 0 | — |
| `I8EiR5WN` | Inspire 25 | 0 | 0 | — |
| `IplMz9PA` | LA Chapter Boardroom April 2026 | 0 | 0 | — |
| `gYp7Utiu` | Lunch on MDS (copy) | 0 | 0 | — |
| `Z2bcLh2Y` | MDS 2022 Town Hall | 0 | 0 | — |
| `shBScSmW` | MDS 2026 - Application | 0 | 0 | — |
| `LbQtet4c` | MDS Annual Census 2026 — BACKUP (Aug 4) | 0 | 0 | — |
| `KSQ9sVyq` | MDS Annual Census 2026 — EUGENE source-of-truth (Aug 4 backup) | 0 | 0 | — |
| `XfrZTEqg` | MDS App Team Member Access | 0 | 0 | — |
| `nRXLrg85` | MDS Census 2026 | 0 | 0 | — |
| `Tah7v9BV` | MDS DTC/Shopify Verification form | 0 | 0 | — |
| `NEvIZhq9` | MDS Experience - Michelin Restaurants | 0 | 0 | — |
| `yafOGykB` | MDS Inspire 2024 - Speaker Request Form | 0 | 0 | — |
| `PzfuODDq` | MDS Inspire 2025 - Vendors | 0 | 0 | — |
| `XFzifcGX` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `XrA1xuHV` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `G6DKnQgk` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `awJhlRL8` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `BnKGar1k` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `rQRM4kFl` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | — |
| `CkF2C47N` | MDS Inspire 2026 - New Member Bingo | 0 | 0 | — |
| `GrbfkR7S` | MDS Inspire Brochure (Partners) | 0 | 0 | — |
| `cLryKIxf` | MDS Inspire Partner Add ons | 0 | 0 | — |
| `lZwkVODb` | MDS Partner New Form 2026 | 0 | 0 | — |
| `KsOovPCi` | MDS Podcast Subscription | 0 | 0 | — |
| `RP1TfnCq` | MDS Q2 MVP | 0 | 0 | — |
| `aoggJSeO` | MDS Singapore Summit Hack Contest | 0 | 0 | — |
| `e09sT3Wn` | MDS Summit Barcelona - Best Value Add & Best in Show (copy) | 0 | 0 | — |
| `qev986J4` | MDS Summit Denver Hotel | 0 | 0 | — |
| `Epco8CTS` | MDS Summit Mexico City - Best Value Add | 0 | 0 | — |
| `gZa5tgF1` | MDS Summit Mexico City - Best Value Add (copy) | 0 | 0 | — |
| `vyFblnAG` | MDS Summit Milan 2025 - Company Information | 0 | 0 | — |
| `CsokVaXh` | MDS Takeover Lisbon- Best Value Add | 0 | 0 | — |
| `FrpuFpUq` | Member Satisfaction Survey App Event | 0 | 0 | — |
| `b8OMAQ6r` | Member Satisfaction Survey Template (copy) | 0 | 0 | — |
| `o9Li9az2` | Member of the month - December 2025 | 0 | 0 | — |
| `pmFcuSWB` | Member of the month - June 2024 | 0 | 0 | — |
| `XXjbX1He` | My branded typeform | 0 | 0 | — |
| `AGyUT22L` | My branded typeform | 0 | 0 | — |
| `H3iXqOrA` | My branded typeform | 0 | 0 | — |
| `zS1w019l` | My branded typeform | 0 | 0 | — |
| `DRrLdHfl` | My branded typeform | 0 | 0 | — |
| `Xyl6vx8d` | My branded typeform | 0 | 0 | — |
| `uWRY5oMR` | My branded typeform | 0 | 0 | — |
| `nm7Vuemg` | My branded typeform | 0 | 0 | — |
| `gvmQVhak` | My branded typeform | 0 | 0 | — |
| `rLwALXKi` | My branded typeform | 0 | 0 | — |
| `OdizTQN0` | My branded typeform | 0 | 0 | — |
| `hzevwXUB` | My branded typeform | 0 | 0 | — |
| `R3BabrmV` | My branded typeform | 0 | 0 | — |
| `CzoOaePS` | My branded typeform | 0 | 0 | — |
| `MRgWaivh` | My new form | 0 | 0 | — |
| `HOW6n9SG` | My new form | 0 | 0 | — |
| `Ju6gGjHW` | My new form | 0 | 0 | — |
| `nsDkz47U` | My new form | 0 | 0 | — |
| `f6Dt9F1f` | My new form | 0 | 0 | — |
| `Gku6ww7C` | My new form | 0 | 0 | — |
| `aBNJEcgp` | My new form | 0 | 0 | — |
| `WI5cZ6J8` | My new form | 0 | 0 | — |
| `oGp4dCXe` | My new form | 0 | 0 | — |
| `dKztJEX8` | My new form | 0 | 0 | — |
| `BFpXuxkJ` | My typeform | 0 | 0 | — |
| `gOKp1Tpu` | New Member Application - Amazon (copy) | 0 | 0 | — |
| `VxQBgwFN` | New Member Application - Amazon no responses | 0 | 0 | — |
| `aNeOkhKl` | New Member Application - Shopify/DTC | 0 | 0 | — |
| `T1eomicD` | New Member Application v2 | 0 | 0 | — |
| `eWQqAtop` | New York Chapter Boardroom Jan '26 | 0 | 0 | — |
| `hDLCoL47` | NorthTex Chapter Boardroom Bonding Sep 2025 | 0 | 0 | — |
| `JhfUINu8` | Northtex Boardroom March 2025 | 0 | 0 | — |
| `no1IvPwV` | Partner Event Feedback (NEW 5/2/22) | 0 | 0 | — |
| `Xybe1Qb2` | Partner Feedback Form | 0 | 0 | — |
| `d5AzRlIV` | Partner Feedback with MDS Members | 0 | 0 | — |
| `PBlf7VU5` | Partner_ Session Survey _ Summit Singapore | 0 | 0 | — |
| `bqrKikhF` | Partners & Category Part 1 | 0 | 0 | — |
| `FMU6I4tZ` | Partners & Category Part 2 | 0 | 0 | — |
| `Q1DE45JL` | Partners & Category Part 3 | 0 | 0 | — |
| `mWidbxXs` | Pet Mastermind Aug 2025 | 0 | 0 | — |
| `CFZighoL` | Proprietary Information Agreement 8-4-2020 | 0 | 0 | — |
| `sJMgZ6lW` | Real Estate Mastermind July 2025 | 0 | 0 | — |
| `wGcLthbD` | SCFest Miami 2026 - Activation Reg 2026 (Comp) | 0 | 0 | — |
| `fkzYu6ow` | Sample Partner Package | 0 | 0 | — |
| `hSrmng27` | Session Survey - Template Milan | 0 | 0 | — |
| `ZHrJo6G4` | Site Inspection for MDS Events (copy) | 0 | 0 | — |
| `Qyybxhoq` | SoFlo Chapter Boardroom March 2025 | 0 | 0 | — |
| `F8y1kMy3` | SoTex Chapter Boardroom Bonding April 2025 | 0 | 0 | — |
| `ikx7ZcTQ` | Southside Chapter Boardroom March 2026 | 0 | 0 | — |
| `yJQQiKTG` | Southside Chapter Lake Norman Day July 2026 | 0 | 0 | — |
| `JPayBXjh` | Speaker _ Session Survey _ Summit Singapore | 0 | 0 | — |
| `hQHBhefh` | Sponsorship Form [DEMO 2] (copy) | 0 | 0 | — |
| `Wc2pncnj` | Summit Ojai Best Valueadd June 2026 | 0 | 0 | — |
| `DbIEJ1EP` | Supplement Mastermind Oct 2025 | 0 | 0 | — |
| `JimFPB6O` | Talent Recruitment Quiz | 0 | 0 | — |
| `AulRD4fj` | TikTok Kickstart Mastermind Presentation Order | 0 | 0 | — |
| `ueaxp7yw` | TikTok Live | 0 | 0 | — |
| `IMeLyKa8` | TikTok Mastermind Presentation Order | 0 | 0 | — |
| `sT22vxbe` | Tuthi Ambassador  NEW 4/21/22 | 0 | 0 | — |
| `sT22vxbe` | Tuthi Ambassador  NEW 4/21/22 | 0 | 0 | — |
| `PFDcRZr1` | Under 30 Verification Form | 0 | 0 | — |
| `PFDcRZr1` | Under 30 Verification Form | 0 | 0 | — |
| `CY3Qw9B8` | Vote for ValueAdd Topics - SoCal Boardroom Meetup | 0 | 0 | — |
| `CY3Qw9B8` | Vote for ValueAdd Topics - SoCal Boardroom Meetup | 0 | 0 | — |
| `MiCP2BHr` | WMDS Mentorship Program Application | 0 | 0 | — |
| `MiCP2BHr` | WMDS Mentorship Program Application | 0 | 0 | — |
| `LxorXR12` | ZZZ TEST - API Partial Capture (delete me) | 0 | 0 | — |
| `GeNIHxK0` | email sign up form (copy) | 0 | 0 | — |
| `GeNIHxK0` | email sign up form (copy) | 0 | 0 | — |
