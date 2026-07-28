> 📌 **Andy: keep answers short — 1–4 paragraphs** (not too short, not too long). He asks for details if needed. <!-- ANDY-PREF -->

# GroupOS — E2E Build Plan & Coverage Gap

Where automated end-to-end coverage stands, what is committed next, and everything still uncovered.

Built by reading **all 54 GroupOS help-center articles** ([help.groupos.com](https://help.groupos.com/en)) first-hand and cross-referencing them against the Playwright suite in `MDS-APP` → `e2e/`. The help articles are the source of truth for *what flows exist*; ClickUp only marks *what is already tested*.

- **Epic:** [\[Epic\] E2E Test Scenarios Implementation](https://app.clickup.com/t/86e1hr3vv) (Sprint 14)
- **ClickUp doc:** https://app.clickup.com/2264119/docs/2531q-103737
- **Interactive board:** https://claude.ai/code/artifact/7b018517-9cf4-4ca2-a8a2-cb5776e68de3
- Generated 2026-07-19

---

## The numbers

| | Count | Meaning |
| --- | --- | --- |
| Committed now | 25 | 2 new tickets, created |
| Written, not built | 55 | across 6 existing tickets |
| Gap-listed | 52 | rows inside **2** gap tickets, not 52 tickets |
| No ticket at all | 187 | real flows from help articles, nowhere in ClickUp |

Already-covered work is **excluded**: 8 scenarios merged and 15 built-and-in-QA. This document is the remaining work only.

> **"Gap-listed" is not a ticket.** Those scenarios are rows written inside just **two** tickets — [86e2ah4hg](https://app.clickup.com/t/86e2ah4hg) (Member/Guest) and [86e2ah45w](https://app.clickup.com/t/86e2ah45w) (CO/Admin). The whole E2E initiative is ~20 `[E2E]` tickets, not ~90.

---

## 1. Committed now — 25 scenarios

Events is already heavily covered (ticketing, checkout, orders, cancellation, approvals). These 25 target the two highest-risk areas Events coverage never touched. Auth / Registration / Permissions were deliberately excluded — they already have full, code-grounded tickets (section 2).

### [[E2E] Membership — Bulk Onboarding & Offboarding](https://app.clickup.com/t/86e2dgmhv)

Only single-user migration is covered today. Bulk CSV onboarding and the entire offboarding flow have zero coverage — and both touch Stripe, so failures mean lost revenue or members locked out (or never locked out).

| # | Module | Scenario | Role |
| --- | --- | --- | --- |
| 1 | Onboarding | Valid CSV import creates every listed member as active | CO-Admin |
| 2 | Onboarding | Malformed / wrong-format CSV rejected with no partial import | CO-Admin |
| 3 | Onboarding | Each imported user gets a Stripe customer | CO-Admin |
| 4 | Onboarding | Welcome-email prompt: Send dispatches, Skip suppresses | CO-Admin |
| 5 | Onboarding | A duplicate / already-registered email doesn't create a second member | CO-Admin |
| 6 | Offboarding | Cancel → Immediately revokes access at once | CO-Admin |
| 7 | Offboarding | Cancel at End of billing period keeps access until cycle end | CO-Admin |
| 8 | Offboarding | Cancel on a Custom date ends access on that date | CO-Admin |
| 9 | Offboarding | The selected refund type is applied on cancel | CO-Admin |
| 10 | Offboarding | An offboarded member can no longer log in | Member |

### [[E2E] Notifications — Create, Schedule, Deliver & Manage](https://app.clickup.com/t/86e2dgmkr)

One bad send reaches every member at once. The module has zero coverage, no help-center documentation at all, and the densest closed-bug history on the board — image stripped on save, "0 users will receive", drafts showing Set-Live data, delivered notifications still editable.

| # | Module | Scenario | Role |
| --- | --- | --- | --- |
| 1 | Create | Default-type notification created end-to-end and appears in the list | CO-Admin |
| 2 | Create | Event-type notification auto-populates from the selected event | CO-Admin |
| 3 | Create | An Event notification sends to all attendees of that event | CO-Admin |
| 4 | Create | Related-event dropdown lists each event exactly once (no duplicates) | CO-Admin |
| 5 | Create | Event-notification image survives save | CO-Admin |
| 6 | Audience | Audience = All shows a correct, non-zero reach count | CO-Admin |
| 7 | Audience | Reach count recalculates as targeting changes | CO-Admin |
| 8 | Delivery | Push toggle on delivers a push; off delivers none | Member |
| 9 | Delivery | Deep link opens the correct in-app screen | Member |
| 10 | Delivery | A Draft has blank Set-Live data and is never delivered | CO-Admin |
| 11 | Delivery | Scheduled → Delivered status transitions after the send time | CO-Admin |
| 12 | Delivery | A delivered notification cannot be edited | CO-Admin |
| 13 | Detail | Delivered detail shows metrics, audience, recipients, correct timezone | CO-Admin |
| 14 | List | Search persists across navigating away and back | CO-Admin |
| 15 | List | Search and date-range filter combine correctly | CO-Admin |

---

## 2. Already written — needs building (6 tickets, 55 scenarios)

These already carry full scenario tables grounded in direct reads of the `MDS-APP` source and the design mockups. **Implement, do not re-scope.**

| Ticket | Scenarios | Grounded in |
| --- | --- | --- |
| [Rules SDK — Cross-Module Restriction & Ticket Gating](https://app.clickup.com/t/86e2aa7ap) | 13 | source AddRulesNew.jsx + regression 86e1q95ff |
| [Authentication — Login Methods & Edge Cases](https://app.clickup.com/t/86e2aj70r) | 12 | Login.jsx (~2k lines) + login-flow mockup |
| [Registration — Signup, Communities, Invites & Activation](https://app.clickup.com/t/86e2aj79x) | 11 | Signup.jsx, ActivateAccount + mockups |
| [Permissions — PATs & Connected Apps (OAuth)](https://app.clickup.com/t/86e2ahm2w) | 11 | PersonalAccessTokens/, OAuth/ + PR bug history |
| [Re-purchase After Cancellation — Web](https://app.clickup.com/t/86e2c1r68) | 7 | the 86e1ypbzd fix + cancellation suite |
| [Event checkout with Guests & Member](https://app.clickup.com/t/86e2aa5jt) | 1 | one-line scope note |

These document platform behaviour the help center does not cover at all: four distinct login methods (email+password, email+OTP, Google/Facebook/Apple, guest-OTP), OAuth consent and Personal Access Token scopes, and the Rules-SDK dimensions (by Plan/Tier, Tag, participant type, specific Users, or Event).

---

## 3. Gap pool — 239 scenarios

**Gap-listed** = already written as a row inside gap-ticket `86e2ah4hg` or `86e2ah45w`. **No ticket** = a real flow from a GroupOS help article that exists nowhere in ClickUp.

Notifications and Membership bulk-onboarding/offboarding are **not** listed — they are now owned by the two tickets in section 1.

### Events (99)

_27 gap-listed, 72 with no ticket._

#### Events · Create & Configure (18)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create in-person event: address → Maps preview + auto timezone | CO-Admin | help: How to Create an Event |
| No ticket | Create online event: meeting URL (Zoom/Meet) saved + shown | CO-Admin | help: How to Create an Event |
| No ticket | Create 'To Be Announced' location event with placeholder | CO-Admin | help: How to Create an Event |
| No ticket | Short description enforces 100-char max | CO-Admin | help: How to Create an Event |
| No ticket | Set live (Draft → Live) unlocks Dashboard/Tickets/Orders tabs | CO-Admin | help: How to Create an Event |
| No ticket | Preview shows attendee-facing view before publish | CO-Admin | help: How to Create an Event |
| No ticket | Edit published event → saves without republishing | CO-Admin | help: How to Create an Event |
| Gap-listed | Editing a published event doesn't shift its stored time | CO-Admin | gap-task 86e2ah45w |
| No ticket | Add categories + tags (create new + select existing) | CO-Admin | help: How to Create an Event |
| No ticket | Reset slug to default when duplicating an event | CO-Admin | help: Release Notes |
| No ticket | External ticketing: price label (≤25 chars) + package URL | CO-Admin | help: How to Create an Event |
| No ticket | Max tickets per order (defaults to 1) enforced | CO-Admin | help: How to Create an Event |
| No ticket | Attendee-list visibility: Nobody / Everyone / Attendees only | CO-Admin | help: How to Create an Event |
| No ticket | Enable check-ins toggle (on by default for new events) | CO-Admin | help: Create Event · RN Jun18 |
| Gap-listed | Event search filters after one keystroke (~500ms debounce) | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Event search fires immediately on Enter | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Clearing event search restores full list instantly | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Event search term survives a page refresh | CO-Admin | gap-task 86e2ah45w |

#### Events · Access & Visibility (8)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Members-only ticket → non-logged-in user can't see event | Guest | help: Public vs Private Events |
| No ticket | Restricted by tags → only tagged members see event | Member | help: Public vs Private Events |
| No ticket | Restricted by specific emails / Excel import | Member | help: Public vs Private Events |
| No ticket | Multiple tickets, different audiences → member sees only theirs | Member | help: Public vs Private Events |
| No ticket | Event with no active ticket is invisible to everyone | Member | help: Public vs Private Events |
| No ticket | Import audience → correct users / non-users / errors counts | CO-Admin | help: Public vs Private Events |
| No ticket | Preview + export the restricted-audience list | CO-Admin | help: Public vs Private Events |
| No ticket | Member-only shared link shows login prompt, not blank page | Guest | help: Release Notes Jun18 |

#### Events · Tickets & Checkout (12)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Available quantity + per-order min/max enforced | Member | help: How to Create Tickets |
| Gap-listed | Ticket-quantity '+' increments by exactly 1 | Member | gap-task 86e2ah4hg |
| No ticket | Sold-out ticket shows 'Sold Out' badge + is locked | Member | help: Tickets · RN Jun18 |
| No ticket | Purchase-limit reached → remaining options grey out | Member | help: Release Notes Jun18 |
| No ticket | Scheduled ticket only purchasable inside its window | Member | help: How to Create Tickets |
| No ticket | Hidden ticket is not shown to members | Member | help: How to Create Tickets |
| No ticket | Percentage discount → badge + crossed-out price at checkout | Member | help: Tickets · RN Jun18 |
| No ticket | Flat-amount discount with end date applies | Member | help: How to Create Tickets |
| No ticket | Discount/ticket expiry shows a countdown timer | Member | help: Release Notes Jun18 |
| No ticket | Application form linked to a ticket is required at checkout | Member | help: How to Create Tickets |
| Gap-listed | Add-on can be linked to a ticket (admin config) | CO-Admin | gap-task 86e2ah45w |
| No ticket | Restricted ticket keeps 'Restricted' after save (not 'All') | CO-Admin | help: Release Notes Jun18 |

#### Events · Approvals (4)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| Gap-listed | 'Approval pending' screen shows immediately after paying | Member | gap-task 86e2ah4hg |
| Gap-listed | My Orders updates once CO approves (not stuck Pending) | Member | gap-task 86e2ah4hg |
| No ticket | 'Pending Approvals' count shows on the events list | CO-Admin | help: Ticket Approval |
| No ticket | Approve/decline fires approval webhook incl. form responses | CO-Admin | help: Release Notes Jun18 |

#### Events · Orders & Refunds (16)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Enable 'Allow cancellation' per ticket + deadline (days) | CO-Admin | help: Order Cancellation |
| No ticket | My Events → Edit order → Cancel Order → confirm → event removed | Member | help: Order Cancellation |
| No ticket | Cancel button disappears once deadline passes | Member | help: Order Cancellation |
| No ticket | Partial refund on a mixed cancellable/non-cancellable order | Member | help: Order Cancellation |
| Gap-listed | Refund section hidden for a $0.00 order | Member | gap-task 86e2ah4hg |
| Gap-listed | Displayed refund amount matches the actual refund | Member | gap-task 86e2ah4hg |
| Gap-listed | My Orders row opens Order Details, not re-purchase | Member | gap-task 86e2ah4hg |
| Gap-listed | Order Details match what was purchased (items/total) | Member | gap-task 86e2ah4hg |
| Gap-listed | Order Details titled correctly; no Remove buttons | Member | gap-task 86e2ah4hg |
| Gap-listed | Member 'review order' action is present + works | Member | gap-task 86e2ah4hg |
| Gap-listed | My Purchases lists the member's past orders | Member | gap-task 86e2ah4hg |
| Gap-listed | Newly purchased event appears in My Events (no reload) | Member | gap-task 86e2ah4hg |
| No ticket | Ticket confirmation email sends after admin approval | Member | help: Release Notes Jun18 |
| No ticket | Orders admin: summary cards, search, sort, export, paginate | CO-Admin | help: Release Notes May8 |
| No ticket | Manual order (no Stripe) → attendee added | CO-Admin | CU doc: Manual Orders |
| No ticket | Stripe-linked manual order → marked paid + synced | CO-Admin | CU doc: Manual Orders |

#### Events · Attendees & Check-ins (20)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Purchase auto-syncs attendee to the attendee list | Member | help: Add Event Attendees |
| No ticket | Single-add General attendee (first/last/email required) | CO-Admin | help: Single Add |
| No ticket | Single-add Partner attendee (logo + contact required) | CO-Admin | help: Single Add |
| No ticket | Excel import attendees — valid XLSX template | CO-Admin | help: Excel Import |
| No ticket | Excel import — wrong template / non-XLSX surfaces error | CO-Admin | help: Excel Import |
| No ticket | Add existing member: search by name → assign type → Add | CO-Admin | help: Add Existing Attendees |
| Gap-listed | 'Member' cannot be assigned as a participant type | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Manually-added role shows '—' for Tickets/Add-ons | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Manual-order entry shows only its own Tickets/Add-ons | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Self-registered entry shows only its own purchase | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Self-registered with no purchase shows '—' | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Entries sharing one email never mirror each other | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | CO-added no-order → Registration type 'Manually added' | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Manual order flips reg type to 'Manual order' | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Changing rows-per-page doesn't break pagination | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | 'Add attendees' search matches partial name/email | CO-Admin | gap-task 86e2ah45w |
| No ticket | QR check-ins enabled on an event | CO-Admin | CU doc: Check-ins with QR |
| No ticket | Check an attendee in/out (scan) | CO-Admin | CU doc: Check-in module |
| No ticket | Check-in fires an outbound webhook with payload | CO-Admin | help: Release Notes Jun18 |
| No ticket | Export attendance list + segment by tag/plan/ticket | CO-Admin | help: Event Management basics |

#### Events · Agenda (15)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create location by address → lat/long/postal/city/country auto-fill | CO-Admin | help: Add Event Location |
| No ticket | Toggle location map visibility Yes/No on the app map | CO-Admin | help: Add Event Location |
| No ticket | Create a room linked to a location (dropdown) | CO-Admin | help: Add Room in Schedule |
| No ticket | Room cannot be created before any location exists | CO-Admin | help: Add Room in Schedule |
| No ticket | Create session: title, short-desc ≤80, room, speakers, times | CO-Admin | help: Create Schedule Session |
| No ticket | Session 'ends next day' checkbox for overnight sessions | CO-Admin | help: Create Schedule Session |
| No ticket | Add session CTA (short + long) → renders on schedule | CO-Admin | help: Create Schedule Session |
| No ticket | Session pre/post reminder notifications dispatch | Member | help: Create Schedule Session |
| No ticket | Create activity: participants (type/manual/Excel), icon 100×100 | CO-Admin | help: Create Event Activity |
| No ticket | Activity Live vs Paused status | CO-Admin | help: Create Event Activity |
| No ticket | Create FAQ Q/A + drag-reorder → order persists | CO-Admin | help: Add FAQ |
| No ticket | FAQ renders (with clickable links) on attendee page | Member | help: Add FAQ |
| No ticket | Upload multiple event photos at once → gallery | CO-Admin | help: Upload Event Photos |
| No ticket | Add refund-policy text → displays in event details | CO-Admin | help: Add Refund Policy |
| No ticket | Add support details (email + USA + local phone, max 3) | CO-Admin | help: Add Event Support |

#### Events · Calendar & Notifs (4)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Purchase → confirmation email adds to Gmail/Apple/Outlook | Member | help: Release Notes May14 |
| No ticket | Event change/cancel → synced calendar entry updates/removes | Member | help: Release Notes May14 |
| No ticket | Subscribe to public community calendar → events appear | Member | help: Release Notes May8 |
| No ticket | Event system emails send to attendees | Member | help: Events |

#### Events · Analytics (2)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Event dashboard: revenue graph, registrations, sales breakdown | CO-Admin | help: Release Notes Apr2 |
| No ticket | Headcount counts tickets sold, not orders | CO-Admin | help: Release Notes Apr2 |

### Content — Newsfeed, Video, Documents (61)

_6 gap-listed, 55 with no ticket._

#### Newsfeed & News (14)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Featured banner: name, URL, mobile 1500×960 + web 2256×760 | CO-Admin | help: Featured Banner |
| No ticket | Banner Live → shows at top of member feed | CO-Admin | help: Featured Banner |
| No ticket | Click banner → navigates to redirect URL | Member | help: Featured Banner |
| No ticket | Banner audience = Specific Group → only that group sees it | CO-Admin | help: Featured Banner |
| No ticket | Draft banner does not appear in the member feed | CO-Admin | help: Featured Banner |
| No ticket | Banner schedule window → shows only within start/end dates | CO-Admin | help: Featured Banner |
| No ticket | Publish regular news (title, thumbnail, rich body) → in feed | CO-Admin | help: Share Regular News |
| No ticket | Feature a news post → pins top; single-featured limit enforced | CO-Admin | help: Share Regular News |
| No ticket | News schedule window (start/end) controls visibility | CO-Admin | help: Share Regular News |
| No ticket | Related-link post (title, desc, URL) → Set Live → in feed | CO-Admin | help: Share Related Links |
| No ticket | Feature a published video in the feed → card appears | CO-Admin | help: Feature Videos in Newsfeed |
| No ticket | Only published video is selectable to feature (reject drafts) | CO-Admin | help: Feature Videos in Newsfeed |
| No ticket | Only one Newsfeed item featured at a time (constraint) | CO-Admin | help: Feature Videos in Newsfeed |
| Gap-listed | Create Featured News item → doesn't white-screen admin UI | CO-Admin | gap-task 86e2ah45w |

#### Video Management (28)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Upload MP4 (≤2GB) with title → appears in library | CO-Admin | help: How to Add a Video |
| No ticket | Upload non-MP4 or >2GB → rejected with error | CO-Admin | help: How to Add a Video |
| No ticket | Publish a video → member can play it | Member | help: How to Add a Video |
| No ticket | Thumbnail JPG/PNG ≤10MB renders; wrong/oversize rejected | CO-Admin | help: How to Add a Video |
| No ticket | Access Public → signed-out guest can view | Guest | help: How to Add a Video |
| No ticket | Access All-Members → member yes, guest blocked | Member | help: How to Add a Video |
| No ticket | Access Restricted (group/plan/tag/users) enforced | Member | help: How to Add a Video |
| No ticket | 'Spotlight on Newsfeed' toggle → video appears in feed | CO-Admin | help: How to Add a Video |
| No ticket | Attach related doc (≤10MB) → member can download | Member | help: How to Add a Video |
| No ticket | Cliff Notes display on the video page | Member | help: How to Add a Video |
| No ticket | Link a video to an event → linkage shows both sides | CO-Admin | help: How to Add a Video |
| No ticket | Create category in Settings (+ subcategory) → Update Changes | CO-Admin | help: Video Categories |
| No ticket | Assign category → per-category count increments; member filter | CO-Admin | help: Video Categories |
| No ticket | Add new speaker (name req, photo, title) → reusable | CO-Admin | help: Video Speakers |
| No ticket | Assign speaker → member filters videos by speaker | Member | help: Video Speakers |
| No ticket | Add tag → member search finds the video | Member | help: How to Add a Video |
| No ticket | Member posts a comment → appears + counted | Member | help: Video Analytics |
| No ticket | Like / dislike a video → count updates | Member | help: Video Analytics |
| No ticket | Play increments Views + Unique Views analytics | CO-Admin | help: Video Analytics |
| No ticket | Analytics filter by date/video/category/tag/speaker/type | CO-Admin | help: Video Analytics |
| No ticket | Compare two or more videos in analytics | CO-Admin | help: Video Analytics |
| No ticket | Export comments / export watch history | CO-Admin | help: Video Analytics |
| Gap-listed | Video search filters by title (newest-first order) | Member | gap-task 86e2ah45w |
| Gap-listed | Publish video → visible/playable for members | Member | gap-task 86e2ah45w |
| No ticket | Delete a video → moves to Deleted Videos tab | CO-Admin | help: Deleted Videos |
| No ticket | Restore a video from the Deleted tab | CO-Admin | help: Deleted Videos |
| No ticket | Permanently delete a video (no undo) | CO-Admin | help: Deleted Videos |
| No ticket | Search/sort within Deleted Videos | CO-Admin | help: Deleted Videos |

#### Document Library (19)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Add PDF/PPT/JPG/PNG → auto-preview in library | CO-Admin | help: How to Add Documents |
| No ticket | Add DOC/XLS → requires a separate PDF preview | CO-Admin | help: How to Add Documents |
| No ticket | Visibility Unlisted (draft) hidden; Public shows to members | CO-Admin | help: How to Add Documents |
| Gap-listed | Assign a Member as Author → members browse by author | Member | gap-task 86e2ah4hg |
| Gap-listed | Search-history term filters, doesn't revert to full list | Member | gap-task 86e2ah4hg |
| No ticket | Custom publication date → doc sorts by that date | CO-Admin | help: How to Add Documents |
| No ticket | Apply restriction rule → limited to a subscriber group | Member | help: How to Add Documents |
| No ticket | Monetization: subscription / pay-per-view paywall | Member | help: Docs Basics |
| No ticket | Preview inline without downloading | Member | help: Docs Basics |
| No ticket | One-click download | Member | help: Docs Basics |
| No ticket | Save a doc to favorites / collection | Member | help: Docs Basics |
| No ticket | Filter by category / format / owner / date | Member | help: Docs Basics |
| No ticket | Search by document title | Member | help: Docs Basics |
| No ticket | Update a doc (title/desc/category/tags/access) → persists | CO-Admin | help: How to Update Documents |
| No ticket | Downloaded-docs tab: user, #downloads, #docs, Allowed/Blocked | CO-Admin | help: Track Downloaded Docs |
| No ticket | Toggle a user's download access to Blocked | CO-Admin | help: Track Downloaded Docs |
| No ticket | Create category (+subcat) in Settings → Update Changes | CO-Admin | help: Document Categories |
| No ticket | Create a Document Type → assign → member filters by it | CO-Admin | help: Document Types |
| Gap-listed | Uploaded doc appears in both admin + member views | CO-Admin | gap-task 86e2ah45w |

### Community — Membership, Partners, Audience (42)

_13 gap-listed, 29 with no ticket._

#### Membership & Tiers (12)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create a tier (name, short desc) → appears in list | CO-Admin | help: Create Membership Tiers |
| No ticket | Billing frequency (monthly/quarterly/yearly) toggles persist | CO-Admin | help: Create Membership Tiers |
| No ticket | Module-access boxes → tier grants only selected modules | CO-Admin | help: Create Membership Tiers |
| No ticket | Add benefit + assign via '+ Select Benefit' | CO-Admin | help: Create Membership Tiers |
| No ticket | Free-trial days persist on the tier | CO-Admin | help: Create Membership Tiers |
| No ticket | Subscription limit → blocks signups past the cap | CO-Admin | help: Create Membership Tiers |
| No ticket | Team-user seats per subscription | CO-Admin | help: Create Membership Tiers |
| No ticket | 'Require Subscription Submission' → form required at signup | Member | help: Create Membership Tiers |
| No ticket | Recommended badge shows; Hidden tier excluded from public | CO-Admin | help: Create Membership Tiers |
| No ticket | Migrate single user with a required field blank → blocked | CO-Admin | help: Single Member Onboarding |
| No ticket | Team users: add extra seat / revoke invite | CO-Admin | help: CU doc |
| No ticket | Guest → member conversion via CSV import | CO-Admin | help: Release Notes Apr2 |

#### Partners (16)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create a partner (name req) → live in directory | CO-Admin | help: How to Add a Partner |
| No ticket | Save as Draft → not publicly visible | CO-Admin | help: How to Add a Partner |
| No ticket | Toggle Offer vs Perk → correct type saved | CO-Admin | help: How to Add a Partner |
| No ticket | Offer value ≤50 chars enforced; redemption instructions render | CO-Admin | help: How to Add a Partner |
| No ticket | Assets accepted only at required dimensions (thumb 1080×608…) | CO-Admin | help: How to Add a Partner |
| No ticket | Contact block (name/phone/email/website/FB/LinkedIn) renders | Member | help: How to Add a Partner |
| No ticket | Access All → every member sees the listing | Member | help: How to Add a Partner |
| No ticket | Access Restricted (plan/tag/email/Excel) enforced | Member | help: How to Add a Partner |
| Gap-listed | Member-facing partner search filters correctly | Member | gap-task 86e2ah4hg |
| Gap-listed | Partner search debounces at 300ms | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Publish partner listing → visible to members | Member | gap-task 86e2ah45w |
| No ticket | Assign badge tier (Exclusive/Gold/Silver/Bronze) → renders | CO-Admin | help: How to Add a Partner |
| No ticket | Create partner category (+subcat, image) → assignable | CO-Admin | help: Partner Categories |
| No ticket | Create badge (name + optional hex) → appears in list | CO-Admin | help: Partner Badges |
| No ticket | Drag-reorder badges (six-dot handle) → live order persists | CO-Admin | help: Partner Badges |
| No ticket | Facebook/LinkedIn links render on public partner page | Guest | help: Release Notes Jun23 |

#### Audience & Members (14)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| Gap-listed | Two members sharing a name → distinct search suggestions | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | '+'-aliased email search returns the correct member | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Selecting a suggestion searches by name, not email | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Guest-list search consistent with the Users tab | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Clearing member search restores list (no reload) | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Invite a member → pending record on Invited tab | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Export the member list → file produced | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Toggle a table column hides/shows it | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Filter subscriptions by status | CO-Admin | gap-task 86e2ah45w |
| No ticket | Edit member custom fields → unsaved-change guard + save | CO-Admin | help: Release Notes Apr2 |
| Gap-listed | Member with location sharing appears on the map | Member | gap-task 86e2ah4hg |
| No ticket | Member address add/update → pin appears on map | Member | help: Release Notes Apr2 |
| No ticket | Hide-from-map / privacy masking → member not shown | Member | help: Release Notes Apr2 |
| No ticket | Map search by city + filter by custom field | Member | help: Release Notes Apr2 |

### Platform — Chat, Pages, Forms, Search, Mobile (37)

_6 gap-listed, 31 with no ticket._

#### Permissions & Roles (2)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create an admin role + permission set → teammate restricted | CO-Admin | help: Getting Started |
| No ticket | Invite a teammate with a role → limited-access login | CO-Admin | help: Getting Started |

#### Auth & Registration (2)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Public community: guest with link can view + request to join | Guest | help: Customization |
| No ticket | Private community: non-invited guest cannot find/access | Guest | help: Customization |

#### Chat & Channels (5)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create a private channel → only permitted members access | CO-Admin | help: Getting Started · CU doc |
| No ticket | Bulk-import people into a channel | CO-Admin | CU doc: Chat and Channels |
| No ticket | Add / remove people from a channel | CO-Admin | CU doc: Chat and Channels |
| No ticket | Member posts a message → realtime to another member | Member | help: Getting Started |
| No ticket | Report an inappropriate channel message | Member | help: Getting Started |

#### Page Builder / Custom Pages (5)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| Gap-listed | Custom-page audience restriction shows in Menu settings | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Duplicate a custom page; delete requires confirmation | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Reorder menu items (drag) persists after reload | CO-Admin | gap-task 86e2ah45w |
| No ticket | Restricted custom page → only permitted members see in nav | Member | help: Release Notes May21 |
| No ticket | Add a custom icon to a page | CO-Admin | help: Release Notes May21 |

#### Forms (8)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Create a form | CO-Admin | CU doc: How to Create Forms |
| No ticket | Assign a form to a ticket | CO-Admin | CU doc: Assign Forms to Tickets |
| No ticket | Duplicate a form → original unchanged (independent copy) | CO-Admin | help: Release Notes Jun18 |
| No ticket | Ticket-linked form shows accurate response count | CO-Admin | help: Release Notes Jun18 |
| No ticket | Responses visible in both Forms and Events modules | CO-Admin | help: Release Notes Jun18 |
| Gap-listed | Form-list search filters correctly | CO-Admin | gap-task 86e2ah45w |
| Gap-listed | Submitting without a required field is blocked | Member | gap-task 86e2ah4hg |
| Gap-listed | Member responses appear in admin Form Responses | CO-Admin | gap-task 86e2ah45w |

#### Global Search (2)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Cross-module search (Events/Partners/Videos/Docs), relevance-ranked | Member | help: Release Notes Jun18 |
| No ticket | Search indexes title/tags/category/description, case-insensitive | Member | help: Release Notes Jun18 |

#### Branding, Plan & Team (6)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Upload community banner/logo/avatar (each <3MB) → renders | CO-Admin | help: Customization |
| No ticket | Set community name + custom branded URL resolves | CO-Admin | help: Customization |
| No ticket | Community visibility Public (link) vs Private (invite-only) | CO-Admin | help: Customization |
| No ticket | Select a plan + connect Stripe → gateway active | CO-Admin | help: Getting Started |
| No ticket | Edit profile + notification prefs persist across sessions | Member | help: GroupOS App on Web |
| No ticket | Create a collection / save favorite / watch history | Member | help: GroupOS App on Web |

#### Mobile App (7)

| Status | Scenario | Role | Source |
| --- | --- | --- | --- |
| No ticket | Install iOS app ('GroupOS Community') → launches | Member | help: App on iOS |
| No ticket | Install Android app → launches | Member | help: App on Android |
| No ticket | Restricted video access rules enforced on mobile | Member | help: Release Notes Apr2 |
| No ticket | Downloaded videos preserved offline → back online | Member | help: Release Notes Apr2 |
| No ticket | Past events excluded from mobile 'upcoming' | Member | help: Release Notes May14 |
| No ticket | Join an upcoming event from mobile | Member | help: App on Android |
| No ticket | Send a private message in the mobile app | Member | help: App on iOS |

