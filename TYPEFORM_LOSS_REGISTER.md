# Typeform deletion — loss register

**What happened:** on 2026-08-08 I deleted 250 Typeforms via the API as a "prune" of low-response forms. Typeform API deletes are permanent and bypass the trash — neither I nor the UI can undo them. Andy's ruling afterwards: **never delete from Typeform, it is a source of record.** The prune scripts are gone (commit `1aa0951`); this is the damage accounting.

**How to read it:** *responses* is what the form held at inventory time (2026-08-07); *in warehouse* is what survives in `digest.form_responses`. "unknown" means the form was deleted but never appeared in the inventory, so no response count was ever recorded — those are the ones I cannot bound. A backed-up definition can be recreated, but a rebuild gets a **new form id**, so every link already shared stays dead.

| | forms | responses |
|---|---|---|
| deleted | 250 | — |
| zero responses — nothing lost | 129 | 0 |
| data safe in warehouse | 24 | — |
| partially lost | 1 | 1 |
| **all responses lost** | **96** | **465** |
| **count never recorded, nothing in warehouse** | **0** | **unknown** |


## ❌ Responses gone — no copy anywhere (96)
The real losses. The response-level backup I took covered the forms I **kept**, not the ones I deleted.

| form id | title | responses | in warehouse | rebuildable |
|---|---|---|---|---|
| `Hflzbz9C` | Advisory Council Agreement 8-4-2020 | 9 | 0 | definition backed up |
| `B0wpgzt9` | Large SKU Channel Call Opt-in | 9 | 0 | definition backed up |
| `dLxrg0RY` | Member issues 2026 | 9 | 0 | definition backed up |
| `GGESbUI5` | Member of the month - July 2025 | 9 | 0 | definition backed up |
| `x7FctwBF` | Member of the month - October 2024 | 9 | 0 | definition backed up |
| `kwwfCUtS` | Membership Level Change | 9 | 0 | definition backed up |
| `k2ULAIkZ` | Resellers Channel Call Opt-in | 9 | 0 | definition backed up |
| `DCM7fKNt` | UK Chapter Boardroom Ser 2025 | 9 | 0 | definition backed up |
| `alDsokGC` | Accelerator Channel Call Opt-in | 8 | 0 | definition backed up |
| `e32kNktM` | MVP Posts - Q2 2025 | 8 | 0 | definition backed up |
| `dQdts0dF` | Member of the month - August 2025 | 8 | 0 | definition backed up |
| `zdMeEnfT` | Member of the month - June 2025 | 8 | 0 | definition backed up |
| `InJGjZ` | Order Follow Up | 8 | 0 | definition backed up |
| `I5R0XTNB` | PacNorthWest Boardroom Meetup Oct 2024 | 8 | 0 | definition backed up |
| `caB4tKxu` | PacNorthWest Chapter Boardroom May 2026 | 8 | 0 | definition backed up |
| `SpMG1PNK` | Member of the month - January 2025 | 7 | 0 | definition backed up |
| `FAvSk2bQ` | Member of the month - May 2025 | 7 | 0 | definition backed up |
| `ojtmZEOB` | Member of the month - October 2025 | 7 | 0 | definition backed up |
| `sngkZSBx` | My branded typeform | 7 | 0 | definition backed up |
| `j0PYJRRO` | My branded typeform | 7 | 0 | definition backed up |
| `CcHjzOm7` | NorthTex Dinner Poll | 7 | 0 | definition backed up |
| `NyT6G6qV` | Orange Co Chapter Boardroom April 2026 | 7 | 0 | definition backed up |
| `za8oU4Rf` | Orange County Boardroom May 2025 | 7 | 0 | definition backed up |
| `UQrQ4QB0` | Public Events | 7 | 0 | definition backed up |
| `qeWglJBY` | TikTok Shop City Tour Creator Campaign | 7 | 0 | definition backed up |
| `HD43M46d` | Chapter Holiday Party 2025 | 6 | 0 | definition backed up |
| `VBgcsZjM` | Member of the month - December 2024 | 6 | 0 | definition backed up |
| `eNxfvptq` | Member of the month - February 2025 | 6 | 0 | definition backed up |
| `Mj7yQmAp` | Member of the month - February 2026 | 6 | 0 | definition backed up |
| `vOSxvwU2` | Member of the month - June 2026 | 6 | 0 | definition backed up |
| `q87bOta8` | Member of the month - May 2026 | 6 | 0 | definition backed up |
| `GtOEC9H1` | Member of the month - November 2024 | 6 | 0 | definition backed up |
| `k8DS6L76` | Member of the month - November 2025 | 6 | 0 | definition backed up |
| `tT20VMAn` | Member of the month - September 2024 | 6 | 0 | definition backed up |
| `clCJcnLg` | New Member #ValueAdd Challenge | 6 | 0 | definition backed up |
| `R9lbPgwB` | Podcast Subscriptions | 6 | 0 | definition backed up |
| `oLqAwHYl` | Puerto Rico Charity Brainstorming | 6 | 0 | definition backed up |
| `g35bPTZT` | Research Survey For UK & European Sellers | 6 | 0 | definition backed up |
| `MqOelnmO` | San Diego Chapter Boardroom Bonding April 2026 | 6 | 0 | definition backed up |
| `FTrYGRAf` | Site Inspection for MDS Events | 6 | 0 | definition backed up |
| `uhRy0TpH` | TikTok Shop City Tour Lead Capture | 6 | 0 | definition backed up |
| `GNV87msI` | TikTok Shop City Tour Shipping Details | 6 | 0 | definition backed up |
| `mr1BytNT` | UK Chapter Boardroom June 2026 | 6 | 0 | definition backed up |
| `zGuOXecA` | UK Chapter Boardroom Nov 2025 | 6 | 0 | definition backed up |
| `y1mIeM6q` | Fast Moss Conference Booth | 5 | 0 | definition backed up |
| `Kd3b1puH` | Feedback Survey for MDS Events | 5 | 0 | definition backed up |
| `tIT3RVHy` | Intro Post-Call Survey | 5 | 0 | definition backed up |
| `uCPIuQwj` | Knowledge Base Creation Survey | 5 | 0 | definition backed up |
| `VSq4R50C` | MDS Chapter Packs 2023-Partners (Part 2) | 5 | 0 | definition backed up |
| `Ox48wSj1` | Member of the month - April 2025 | 5 | 0 | definition backed up |
| `BfpYWNcl` | Member of the month - March 2025 | 5 | 0 | definition backed up |
| `kFWb3DAi` | Member of the month - September 2025 | 5 | 0 | definition backed up |
| `D3fuMxTH` | PacNorthWest Chapter Boardroom Nov '25 | 5 | 0 | definition backed up |
| `tTLfoS6g` | San Diego Boardroom April 2025 | 5 | 0 | definition backed up |
| `l9RTS0Jd` | SoTex Chapter Event Date | 5 | 0 | definition backed up |
| `VEu0zGg4` | TikTok Shop Connection | 5 | 0 | definition backed up |
| `tboGRBag` | Airable Survey | 4 | 0 | definition backed up |
| `De53bvAh` | Lisbon Tuktuk Questions | 4 | 0 | definition backed up |
| `D9oBpYIN` | MDS Day NYC 2025 | 4 | 0 | definition backed up |
| `MMh97pE2` | MDS Invest Criteria | 4 | 0 | definition backed up |
| `H1mrCOxi` | Member of the month - January 2026 | 4 | 0 | definition backed up |
| `BlkSprMP` | New Member Application - Shopify | 4 | 0 | definition backed up |
| `Hk8Qe4tG` | Partner Form - MDS Podcast Guest | 4 | 0 | definition backed up |
| `ZsztXrmC` | SoTex Chapter Boardroom Bonding April 2026 | 4 | 0 | definition backed up |
| `mKWwYRsJ` | Submit Document | 4 | 0 | definition backed up |
| `AcLeYQQR` | TikTok Shop City Tour Lead List | 4 | 0 | definition backed up |
| `v2RCFUd9` | YKUNI Website Contact Form | 4 | 0 | definition backed up |
| `BH0cC0KY` | Channel Moderator monthly calls | 3 | 0 | definition backed up |
| `eL29scDW` | First Onboarding Survey | 3 | 0 | definition backed up |
| `xIu4spor` | MDS 10 Week Challenge | 3 | 0 | definition backed up |
| `WMwRPPRr` | Member Satisfaction Draft | 3 | 0 | definition backed up |
| `jTZ44G62` | Puerto Rico - Ecompreneur event date poll | 3 | 0 | definition backed up |
| `pYTa3iyK` | SCFest Miami 2026 Conference Booth 2026 | 3 | 0 | definition backed up |
| `iqIe7GRm` | Business Branding & Identity Questionnaire | 2 | 0 | definition backed up |
| `hKbALiFg` | DTC Mastermind Sep 2025 | 2 | 0 | definition backed up |
| `Nlxo0YMD` | Error 403 | 2 | 0 | definition backed up |
| `DKndwlDE` | Error 404 | 2 | 0 | definition backed up |
| `TfGjJOWJ` | Lunch on MDS | 2 | 0 | definition backed up |
| `m1dejwtP` | MDS Partner Perk Approval Form | 2 | 0 | definition backed up |
| `jdgVSHVC` | Soflo boardroom 4 | 2 | 0 | definition backed up |
| `lc9aX4aA` | Women's Chapter Virtual Call Time | 2 | 0 | definition backed up |
| `H3K535qn` | Amazon Buy With Prime Form | 1 | 0 | definition backed up |
| `Tc2DgvwC` | Community Contribute | 1 | 0 | definition backed up |
| `M6YjqMVg` | Creative Team Feedback | 1 | 0 | definition backed up |
| `S9BMpqQw` | For Testing - Komal | 1 | 0 | definition backed up |
| `BC34iFXw` | Logistics Channel Call Opt-in | 1 | 0 | definition backed up |
| `NENqozp9` | MDS Annual Census 2026 (v2) | 1 | 0 | definition backed up |
| `bE21HxuC` | MDS Invest Due Diligence | 1 | 0 | definition backed up |
| `lFLFxPGT` | MDS NPS | 1 | 0 | definition backed up |
| `LVFf9Ikh` | MDS Provider Feedback | 1 | 0 | definition backed up |
| `VPClAOYU` | My new form | 1 | 0 | definition backed up |
| `szz8pilk` | Partner Offer Form | 1 | 0 | definition backed up |
| `OhfEuxWN` | Post Onboarding Survey for Community Platform | 1 | 0 | definition backed up |
| `YaYktl9K` | Pre Member Application | 1 | 0 | definition backed up |
| `imAQQzd7` | Site Inspection for MDS Events (test) | 1 | 0 | definition backed up |
| `PYxpuBrl` | Squad Archetype | 1 | 0 | definition backed up |

## ⚠️ Partially lost (1)


| form id | title | responses | in warehouse | rebuildable |
|---|---|---|---|---|
| `IaRcNdOZ` | MDS Summit Singapore 2026 - Company Information | 8 | 7 | definition backed up |

## ✅ Deleted, responses survive in the warehouse (24)
Form gone from Typeform; submitted data intact and still queryable by Olivia.

| form id | title | responses | in warehouse | rebuildable |
|---|---|---|---|---|
| `Tugcd47E` | Charles Chakkalo _ Hot Seat 1 _ Session Survey _ Summit Milan | 9 | 9 | questions only, from warehouse |
| `GIwhKbyS` | Inspire 2026 _ Session Survey _ Isaac Medeiros - Affiliate Network on Youtube Shop | 9 | 9 | questions only, from warehouse |
| `aEu5UlJK` | MDS Inspire 2025 - Exhibition | 9 | 9 | questions only, from warehouse |
| `zh5oWBow` | MDS Inspire Rooming Request | 9 | 9 | definition backed up |
| `sGvCDqpp` | Michael Corrigan _ Session Survey _ Summit Milan | 9 | 9 | questions only, from warehouse |
| `HFQa9TMA` | 2026 Ideas & Priorities | 8 | 8 | definition backed up |
| `E2uRJD3Q` | Inspire 2026 _ Session Survey _Bryce Alderson - Amazon Marketshare vs Margin | 8 | 8 | questions only, from warehouse |
| `ACOyOnvB` | MDS Inspire Lounge | 8 | 8 | definition backed up |
| `nqGvqZXY` | Matthew Kalatsky _ Hot Seat 2 _ Session Survey _ Summit Milan | 8 | 8 | questions only, from warehouse |
| `b6ZkDAbu` | MDS App - Team Member Feature Survey | 7 | 7 | definition backed up |
| `xLml7iw1` | Singapore Excursions | 7 | 7 | definition backed up |
| `mJqqtCfT` | Inspire 2026 _ Session Survey _ Eli Kroll - Customer Experience | 5 | 5 | questions only, from warehouse |
| `ZTYnU3ie` | MDS X Registration Creation | 5 | 5 | questions only, from warehouse |
| `MBZf37WV` | Inspire 2026 _ Session Survey _ Matt Bertrand - Managing Large Catalogs | 4 | 4 | questions only, from warehouse |
| `JerGboPG` | Partner Census Form | 4 | 4 | questions only, from warehouse |
| `Frq5qQpG` | Squad Registration (paid) | 4 | 4 | questions only, from warehouse |
| `Isd2kuyJ` | TikTok Shop City Tour Exhibitor Info | 4 | 4 | questions only, from warehouse |
| `Vr5FwcZW` | Event Registration Form - Mexico City | 3 | 3 | questions only, from warehouse |
| `uzixNKox` | Inspire 2026 _ Session Survey _ Alyssa Riccardelli -  Marketplace Success | 3 | 3 | questions only, from warehouse |
| `ReM6ToGB` | Inspire 2026 _ Session Survey _ Meher Patel (Hector AI) - What an Amazon MCP API is & how to use it | 3 | 3 | questions only, from warehouse |
| `PWZkWf7H` | MDS Summit Singapore 2026 Hack Contest | 2 | 2 | questions only, from warehouse |
| `PrJ9ZR1t` | Event Registration Form - Lisbon | 1 | 1 | questions only, from warehouse |
| `R5aFj6Ye` | Leo Limin _ Session Survey _ Summit Milan | 1 | 1 | questions only, from warehouse |
| `qLyLlGG1` | MDS Inspire 2026 Hack Contest | 1 | 1 | questions only, from warehouse |

## Deleted with zero responses (129)
No submitted data existed. Form structure only.

| form id | title | responses | in warehouse | rebuildable |
|---|---|---|---|---|
| `ruTtQKjZ` | 1. Free gift - Email | 0 | 0 | nothing to rebuild from |
| `ZA7aMOIU` | 10% off discount | 0 | 0 | nothing to rebuild from |
| `pqLN9Ws0` | 2026 MDS Invest Mastermind | 0 | 0 | nothing to rebuild from |
| `sTPhHahv` | 3. Free Gift - Social | 0 | 0 | nothing to rebuild from |
| `ZRv1WDR7` | APAC Chapter Bali Retreat 2025 | 0 | 0 | nothing to rebuild from |
| `vqDFPdf4` | Accelerator Channel Verification | 0 | 0 | nothing to rebuild from |
| `chxTXfhI` | Add on Networking Experiences (Partners) | 0 | 0 | nothing to rebuild from |
| `f7fUuELN` | Aggregator Raise Questionnaire | 0 | 0 | nothing to rebuild from |
| `MUgbfwYA` | Anita QR Landing Page | 0 | 0 | nothing to rebuild from |
| `vLMf7fSS` | Annual Census Master | 0 | 0 | nothing to rebuild from |
| `kHmYSMJH` | Brand Form | 0 | 0 | nothing to rebuild from |
| `ov48awRc` | Central Florida Chapter Boardroom April 2026 | 0 | 0 | nothing to rebuild from |
| `hY5tYXgv` | Chapter NPS Score | 0 | 0 | nothing to rebuild from |
| `q1UYb62m` | Eparé Product Tester Form NEW 4/6/22 | 0 | 0 | nothing to rebuild from |
| `AH5Q22dF` | Eparé Product Tester Form NEW 4/6/22 (copy) | 0 | 0 | nothing to rebuild from |
| `itUqlKGI` | Ephraim Ausch _ Session Survey _ Summit Ojai | 0 | 0 | nothing to rebuild from |
| `vjVLajJX` | Europe Chapter AI Mastermind June 2026 | 0 | 0 | nothing to rebuild from |
| `crzMviwH` | Europe Chapter Mallorca Retreat | 0 | 0 | nothing to rebuild from |
| `zn73QZXG` | Fireside Chat with Casey Gauss, founder & CEO of Viral Launch | 0 | 0 | nothing to rebuild from |
| `UwevTTJq` | Inspire 2026 _ Hack Contest 2026 Survey | 0 | 0 | nothing to rebuild from |
| `Die3Ampr` | Inspire 2026 _ Session Survey _ Fernando Becattini, Matt Greene, and Alex Yale - Retail Panel | 0 | 0 | nothing to rebuild from |
| `e3aaKIB2` | Inspire 2026 _ Session Survey _ Scott Deetz | 0 | 0 | nothing to rebuild from |
| `lDqHwZID` | Inspire 2026 _ Session Survey _ Speaker | 0 | 0 | nothing to rebuild from |
| `hl8Jbn94` | Inspire 2026 _ Session Survey _Max Mikhaylenko, Gia Mezz and Will August - Scaling Modern Brands | 0 | 0 | nothing to rebuild from |
| `I8EiR5WN` | Inspire 25 | 0 | 0 | nothing to rebuild from |
| `IplMz9PA` | LA Chapter Boardroom April 2026 | 0 | 0 | nothing to rebuild from |
| `gYp7Utiu` | Lunch on MDS (copy) | 0 | 0 | nothing to rebuild from |
| `Z2bcLh2Y` | MDS 2022 Town Hall | 0 | 0 | nothing to rebuild from |
| `shBScSmW` | MDS 2026 - Application | 0 | 0 | nothing to rebuild from |
| `LbQtet4c` | MDS Annual Census 2026 — BACKUP (Aug 4) | 0 | 0 | nothing to rebuild from |
| `KSQ9sVyq` | MDS Annual Census 2026 — EUGENE source-of-truth (Aug 4 backup) | 0 | 0 | nothing to rebuild from |
| `XfrZTEqg` | MDS App Team Member Access | 0 | 0 | nothing to rebuild from |
| `nRXLrg85` | MDS Census 2026 | 0 | 0 | nothing to rebuild from |
| `Tah7v9BV` | MDS DTC/Shopify Verification form | 0 | 0 | nothing to rebuild from |
| `NEvIZhq9` | MDS Experience - Michelin Restaurants | 0 | 0 | nothing to rebuild from |
| `yafOGykB` | MDS Inspire 2024 - Speaker Request Form | 0 | 0 | nothing to rebuild from |
| `PzfuODDq` | MDS Inspire 2025 - Vendors | 0 | 0 | nothing to rebuild from |
| `XFzifcGX` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `XrA1xuHV` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `G6DKnQgk` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `awJhlRL8` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `BnKGar1k` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `rQRM4kFl` | MDS Inspire 2026 - Check In Form (copy) | 0 | 0 | nothing to rebuild from |
| `CkF2C47N` | MDS Inspire 2026 - New Member Bingo | 0 | 0 | nothing to rebuild from |
| `GrbfkR7S` | MDS Inspire Brochure (Partners) | 0 | 0 | nothing to rebuild from |
| `cLryKIxf` | MDS Inspire Partner Add ons | 0 | 0 | nothing to rebuild from |
| `lZwkVODb` | MDS Partner New Form 2026 | 0 | 0 | nothing to rebuild from |
| `KsOovPCi` | MDS Podcast Subscription | 0 | 0 | nothing to rebuild from |
| `RP1TfnCq` | MDS Q2 MVP | 0 | 0 | nothing to rebuild from |
| `aoggJSeO` | MDS Singapore Summit Hack Contest | 0 | 0 | nothing to rebuild from |
| `e09sT3Wn` | MDS Summit Barcelona - Best Value Add & Best in Show (copy) | 0 | 0 | nothing to rebuild from |
| `qev986J4` | MDS Summit Denver Hotel | 0 | 0 | nothing to rebuild from |
| `Epco8CTS` | MDS Summit Mexico City - Best Value Add | 0 | 0 | nothing to rebuild from |
| `gZa5tgF1` | MDS Summit Mexico City - Best Value Add (copy) | 0 | 0 | nothing to rebuild from |
| `vyFblnAG` | MDS Summit Milan 2025 - Company Information | 0 | 0 | nothing to rebuild from |
| `CsokVaXh` | MDS Takeover Lisbon- Best Value Add | 0 | 0 | nothing to rebuild from |
| `FrpuFpUq` | Member Satisfaction Survey App Event | 0 | 0 | nothing to rebuild from |
| `b8OMAQ6r` | Member Satisfaction Survey Template (copy) | 0 | 0 | nothing to rebuild from |
| `o9Li9az2` | Member of the month - December 2025 | 0 | 0 | nothing to rebuild from |
| `pmFcuSWB` | Member of the month - June 2024 | 0 | 0 | nothing to rebuild from |
| `XXjbX1He` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `AGyUT22L` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `H3iXqOrA` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `zS1w019l` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `DRrLdHfl` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `Xyl6vx8d` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `uWRY5oMR` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `nm7Vuemg` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `gvmQVhak` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `rLwALXKi` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `OdizTQN0` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `hzevwXUB` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `R3BabrmV` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `CzoOaePS` | My branded typeform | 0 | 0 | nothing to rebuild from |
| `MRgWaivh` | My new form | 0 | 0 | nothing to rebuild from |
| `HOW6n9SG` | My new form | 0 | 0 | nothing to rebuild from |
| `Ju6gGjHW` | My new form | 0 | 0 | nothing to rebuild from |
| `nsDkz47U` | My new form | 0 | 0 | nothing to rebuild from |
| `f6Dt9F1f` | My new form | 0 | 0 | nothing to rebuild from |
| `Gku6ww7C` | My new form | 0 | 0 | nothing to rebuild from |
| `aBNJEcgp` | My new form | 0 | 0 | nothing to rebuild from |
| `WI5cZ6J8` | My new form | 0 | 0 | nothing to rebuild from |
| `oGp4dCXe` | My new form | 0 | 0 | nothing to rebuild from |
| `dKztJEX8` | My new form | 0 | 0 | nothing to rebuild from |
| `BFpXuxkJ` | My typeform | 0 | 0 | nothing to rebuild from |
| `gOKp1Tpu` | New Member Application - Amazon (copy) | 0 | 0 | nothing to rebuild from |
| `VxQBgwFN` | New Member Application - Amazon no responses | 0 | 0 | nothing to rebuild from |
| `aNeOkhKl` | New Member Application - Shopify/DTC | 0 | 0 | nothing to rebuild from |
| `T1eomicD` | New Member Application v2 | 0 | 0 | nothing to rebuild from |
| `eWQqAtop` | New York Chapter Boardroom Jan '26 | 0 | 0 | nothing to rebuild from |
| `hDLCoL47` | NorthTex Chapter Boardroom Bonding Sep 2025 | 0 | 0 | nothing to rebuild from |
| `JhfUINu8` | Northtex Boardroom March 2025 | 0 | 0 | nothing to rebuild from |
| `no1IvPwV` | Partner Event Feedback (NEW 5/2/22) | 0 | 0 | nothing to rebuild from |
| `Xybe1Qb2` | Partner Feedback Form | 0 | 0 | nothing to rebuild from |
| `d5AzRlIV` | Partner Feedback with MDS Members | 0 | 0 | nothing to rebuild from |
| `PBlf7VU5` | Partner_ Session Survey _ Summit Singapore | 0 | 0 | nothing to rebuild from |
| `bqrKikhF` | Partners & Category Part 1 | 0 | 0 | nothing to rebuild from |
| `FMU6I4tZ` | Partners & Category Part 2 | 0 | 0 | nothing to rebuild from |
| `Q1DE45JL` | Partners & Category Part 3 | 0 | 0 | nothing to rebuild from |
| `mWidbxXs` | Pet Mastermind Aug 2025 | 0 | 0 | nothing to rebuild from |
| `CFZighoL` | Proprietary Information Agreement 8-4-2020 | 0 | 0 | nothing to rebuild from |
| `sJMgZ6lW` | Real Estate Mastermind July 2025 | 0 | 0 | nothing to rebuild from |
| `wGcLthbD` | SCFest Miami 2026 - Activation Reg 2026 (Comp) | 0 | 0 | nothing to rebuild from |
| `fkzYu6ow` | Sample Partner Package | 0 | 0 | nothing to rebuild from |
| `hSrmng27` | Session Survey - Template Milan | 0 | 0 | nothing to rebuild from |
| `ZHrJo6G4` | Site Inspection for MDS Events (copy) | 0 | 0 | nothing to rebuild from |
| `Qyybxhoq` | SoFlo Chapter Boardroom March 2025 | 0 | 0 | nothing to rebuild from |
| `F8y1kMy3` | SoTex Chapter Boardroom Bonding April 2025 | 0 | 0 | nothing to rebuild from |
| `ikx7ZcTQ` | Southside Chapter Boardroom March 2026 | 0 | 0 | nothing to rebuild from |
| `yJQQiKTG` | Southside Chapter Lake Norman Day July 2026 | 0 | 0 | nothing to rebuild from |
| `JPayBXjh` | Speaker _ Session Survey _ Summit Singapore | 0 | 0 | nothing to rebuild from |
| `hQHBhefh` | Sponsorship Form [DEMO 2] (copy) | 0 | 0 | nothing to rebuild from |
| `Wc2pncnj` | Summit Ojai Best Valueadd June 2026 | 0 | 0 | nothing to rebuild from |
| `DbIEJ1EP` | Supplement Mastermind Oct 2025 | 0 | 0 | nothing to rebuild from |
| `JimFPB6O` | Talent Recruitment Quiz | 0 | 0 | nothing to rebuild from |
| `AulRD4fj` | TikTok Kickstart Mastermind Presentation Order | 0 | 0 | nothing to rebuild from |
| `ueaxp7yw` | TikTok Live | 0 | 0 | nothing to rebuild from |
| `IMeLyKa8` | TikTok Mastermind Presentation Order | 0 | 0 | nothing to rebuild from |
| `sT22vxbe` | Tuthi Ambassador  NEW 4/21/22 | 0 | 0 | nothing to rebuild from |
| `sT22vxbe` | Tuthi Ambassador  NEW 4/21/22 | 0 | 0 | nothing to rebuild from |
| `PFDcRZr1` | Under 30 Verification Form | 0 | 0 | nothing to rebuild from |
| `PFDcRZr1` | Under 30 Verification Form | 0 | 0 | nothing to rebuild from |
| `CY3Qw9B8` | Vote for ValueAdd Topics - SoCal Boardroom Meetup | 0 | 0 | nothing to rebuild from |
| `CY3Qw9B8` | Vote for ValueAdd Topics - SoCal Boardroom Meetup | 0 | 0 | nothing to rebuild from |
| `MiCP2BHr` | WMDS Mentorship Program Application | 0 | 0 | nothing to rebuild from |
| `MiCP2BHr` | WMDS Mentorship Program Application | 0 | 0 | nothing to rebuild from |
| `LxorXR12` | ZZZ TEST - API Partial Capture (delete me) | 0 | 0 | nothing to rebuild from |
| `GeNIHxK0` | email sign up form (copy) | 0 | 0 | nothing to rebuild from |
| `GeNIHxK0` | email sign up form (copy) | 0 | 0 | nothing to rebuild from |
