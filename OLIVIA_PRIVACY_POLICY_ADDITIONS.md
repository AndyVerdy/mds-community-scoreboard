# MDS Privacy Policy — required additions for the MDS Assistant
### Drafted 2026-08-03 against the live policy (effective June 3, 2025) and the systems as actually built. For legal counsel review before publishing; keyed to the existing section headings for a paste-in amendment.

The live policy at mds.co/privacy-policy contains **no mention of AI, automated processing,
community-content processing, or activity analytics**. All four are now in production. Six
additions below; draft language included for each.

---

## 1. Add to "Information We Collect" — new categories

> **Community content.** When you participate in MDS community spaces — including MDS WhatsApp
> groups, the MDS Facebook group, MDS events, and the MDS app — we collect and store the content
> you post there: messages, posts, comments, images, and event registrations. This content is
> retained in our systems to power member services, including search, digests, and the MDS
> Assistant.
>
> **Assistant conversations.** When you message the MDS Assistant, we collect and store the full
> conversation — your messages, the Assistant's replies, delivery status, and your feedback
> reactions.
>
> **Usage and activity data.** We collect information about how you use MDS services — such as
> portal logins, pages viewed, features used, event registrations, and interactions with the
> Assistant — associated with your member record.
>
> **Derived information.** We generate information from the data above, such as engagement
> measures, areas of expertise, topic interests, and connections to other members (for example,
> shared events or group participation), used to improve recommendations and member matching.

## 2. New section — "AI-Assisted Services" (the core legal gap)

> MDS uses artificial-intelligence technology to provide member services, including the MDS
> Assistant. When you use these services, or when your community content is processed to power
> them:
>
> - Your messages to the Assistant, and relevant member and community content, are processed by
>   third-party AI service providers acting on our behalf (currently including Anthropic and
>   Voyage AI). These providers are contractually limited to processing the data to provide the
>   service to us, and do not use your data to train their models.
> - AI-generated responses may be inaccurate. The Assistant's answers are informational and are
>   not professional, financial, or legal advice.
> - We use automated processing to personalize what the Assistant and MDS services show you
>   (for example, recommending members, events, or content). We do not use automated processing
>   to make decisions with legal or similarly significant effects about you.
> - Community content you have shared in member spaces (for example, posts in the MDS Facebook
>   group or messages in MDS WhatsApp groups) may be surfaced to other members through the
>   Assistant, consistent with the visibility of the space where you shared it. Content from a
>   group you are in is never shown to members outside that group.

## 3. Add to "How We Disclose Your Information" — processor list update

Add to the service-provider examples: *hosting and database providers (e.g., Supabase),
AI service providers (e.g., Anthropic, Voyage AI), workflow-automation providers (e.g., n8n),
messaging providers (e.g., Meta's WhatsApp Business Platform), and internal business tools
(e.g., Airtable, Slack).* Note that WhatsApp messages are also subject to WhatsApp's own terms
and privacy policy.

## 4. Amend "Retention of Your Information" — state the actual position

Current text is the generic "no longer than necessary." State the real practice:

> Assistant conversations and community content are retained for as long as you are a member,
> and for up to [X months] after membership ends, unless you request earlier deletion. [X = the
> number MDS chooses — it must be a stated number, not left open.]

## 5. Amend "Your Rights and Choices" — deletion requests + assistant opt-out

The rights list and the appsupport@ email already exist. Add:

> **Assistant and community data.** You may request a copy or deletion of your Assistant
> conversation history and other personal information by emailing
> appsupport@milliondollarsellers.com. We will verify and honor verified requests within 30
> days. You can stop the Assistant from messaging you at any time by replying STOP; reply START
> to resume. Note that deletion of content you posted in shared community spaces may be limited
> where it is part of another member's conversation or a shared record.

## 6. New short section — "International Data Transfers" (currently absent)

MDS has members in the EU/UK (Europe Chapter) and processes data on U.S.-based infrastructure.

> Your information is processed and stored in the United States and other countries where our
> service providers operate, which may not provide the same level of data protection as your
> home jurisdiction. Where required, we rely on appropriate safeguards such as standard
> contractual clauses.

---

## Notes for counsel (not for publication)

- **What is true in the systems today**, so the policy matches reality: conversations stored
  indefinitely; FB group content (posts, comments, image text extracted by AI vision) and WA
  group messages archived and searchable by members via the Assistant; activity events logged
  (portal + assistant; app events planned); engagement scores, expertise profiles and a member
  connection graph computed nightly; retrieval is permission-scoped per member (a member can
  only surface chats they belong to — enforced in the database).
- **Deliberately NOT collected/inferred** (can be stated as a plus): religion, sexual
  orientation, political views, ethnicity — not tracked, not inferred, not filterable. Exact
  member revenue is never disclosed by the Assistant (bands only); private contact details are
  never shared.
- Anthropic API data is not used for model training by default per their commercial terms —
  the "do not train" line above reflects that; counsel should confirm current terms (and
  Voyage's) at publication time.
- The deletion right needs an internal runbook to be honorable ("honoured and verifiable" —
  backlog #19): delete across olivia_messages, content_items, member_events, embeddings, and
  document what shared-space content is retained and why.
- Effective-date bump + member notification of material changes (the policy's own §12 requires
  notice).
