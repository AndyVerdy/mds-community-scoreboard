// #138 — every item she names carries its OWN link. RED first: this file is the
// spec for repairLinks(), which lives in link_repair.js and gets inlined into
// the Gate Verdict node once it passes an audit on real evidence.
//
// Why repair and not regenerate: an audit of all 602 bank C answers showed every
// count-based rule ("names N items, carries <=1 link") fires on MORE correct
// answers than wrong ones — 65 false alarms against 51 real ones at its best
// setting — because she legitimately lists members, chapters and chat names that
// have no URL to give. The signal is not how many links are missing; it is that
// THIS item's own evidence row carried a url and the draft dropped it.
//
// Run: node scripts/olivia_loop/test_138_link_repair.js
const { repairLinks } = require("./link_repair.js");

let pass = 0;
let fail = 0;
const eq = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; console.log("  PASS  " + name); }
  else { fail++; console.log("  FAIL  " + name + "\n        got:  " + JSON.stringify(got) + "\n        want: " + JSON.stringify(want)); }
};
const has = (name, hay, needle) => eq(name, String(hay).includes(needle), true);
const hasNot = (name, hay, needle) => eq(name, String(hay).includes(needle), false);

const NL = String.fromCharCode(10);

// Evidence in the shape the loop actually hands over: JSON tool rows. (The
// suite used invented pipe-delimited lines until 2026-09-02; real evidence is
// JSON, and pretending otherwise hid a defect — see the prose-url case below.)
const EVIDENCE = JSON.stringify([
  { source: "video", title: "Scaling a Subreddit as a Launch & AEO Asset", speaker_names: "Jared Mortensen", published_at: "2026-08-26", video_url: "https://app.mds.co/videos/6a8866c0b6eea7310359279e" },
  { source: "video", title: "The Leadership Layer", speaker_names: "Khalid Abdulla", published_at: "2026-08-26", video_url: "https://app.mds.co/videos/6a8866c0b6eea7310359280f" },
  { source: "video", title: "TikTok Shop Playbooks from Top 7 Brands", speaker_names: "Tamar Yaniv", published_at: "2026-08-26", video_url: "https://app.mds.co/videos/6a8866c0b6eea7310359281a" },
  { source: "member", full_name: "Alex Lushington", chapter: "SoTex Chapter", city: "Austin, Texas" },
]);

console.log("repairLinks — attaches the link the evidence already had");
{
  const draft = [
    "Three worth watching:",
    "• *Scaling a Subreddit as a Launch & AEO Asset* — Jared Mortensen on launch assets",
    "• *The Leadership Layer* — Khalid Abdulla on hiring senior people",
    "• *TikTok Shop Playbooks from Top 7 Brands* — Tamar Yaniv",
  ].join(NL);
  const out = repairLinks(draft, EVIDENCE);
  has("subreddit item gets its own link", out.text, "6a8866c0b6eea7310359279e");
  has("leadership item gets its own link", out.text, "6a8866c0b6eea7310359280f");
  has("tiktok item gets its own link", out.text, "6a8866c0b6eea7310359281a");
  eq("three repairs reported", out.repaired, 3);

  // the right link on the right line — not three links dumped at the end
  const line = out.text.split(NL).find((l) => l.includes("Leadership Layer"));
  has("link sits on the item's own line", line, "6a8866c0b6eea7310359280f");
  hasNot("and not another item's link", line, "6a8866c0b6eea7310359279e");
}

console.log("repairLinks — never invents, never guesses");
{
  const draft = ["• *Alex Lushington* — Austin, SoTex Chapter"].join(NL);
  const out = repairLinks(draft, EVIDENCE);
  eq("an item whose evidence row has no url is left alone", out.repaired, 0);
  eq("text unchanged", out.text, draft);
}
{
  const draft = ["• *Some Session Nobody Retrieved* — not in the evidence at all"].join(NL);
  const out = repairLinks(draft, EVIDENCE);
  eq("an item absent from the evidence is left alone", out.repaired, 0);
}
{
  // two evidence rows match this item equally well — silence beats a wrong link
  const ambiguous = JSON.stringify([
    { source: "video", title: "Summit Session", published_at: "2026-08-26", video_url: "https://app.mds.co/videos/aaaaaaaaaaaaaaaaaaaaaaaa" },
    { source: "video", title: "Summit Session", published_at: "2026-08-27", video_url: "https://app.mds.co/videos/bbbbbbbbbbbbbbbbbbbbbbbb" },
  ]);
  const out = repairLinks("• *Summit Session* — which one?", ambiguous);
  eq("an ambiguous match is left alone", out.repaired, 0);
}
{
  const draft = "• *The Leadership Layer* — https://app.mds.co/videos/6a8866c0b6eea7310359280f";
  const out = repairLinks(draft, EVIDENCE);
  eq("an item that already carries its link is untouched", out.repaired, 0);
  eq("no duplicate link", (out.text.match(/6a8866c0b6eea7310359280f/g) || []).length, 1);
}
{
  const out = repairLinks("Prose with no list at all, just an answer about hiring.", EVIDENCE);
  eq("prose is never touched", out.repaired, 0);
}

console.log("repairLinks — every url it adds came from the evidence verbatim");
{
  const draft = [
    "• *Scaling a Subreddit as a Launch & AEO Asset* — launch assets",
    "• *The Leadership Layer* — hiring",
  ].join(NL);
  const out = repairLinks(draft, EVIDENCE);
  const added = (out.text.match(/https?:\/\/\S+/g) || []);
  eq("all added urls exist in the evidence", added.every((u) => EVIDENCE.includes(u)), true);
}

console.log("repairLinks — the date rides with the link when the item has neither");
{
  const draft = "• *The Leadership Layer* — Khalid Abdulla on hiring senior people";
  const out = repairLinks(draft, EVIDENCE, { withDate: true });
  has("the evidence row's date is attached too", out.text, "2026-08-26");
}

console.log("repairLinks — real evidence is JSON, not tidy lines");
{
  // The loop hands the gate a JSON blob of tool rows. A url must be cut at the
  // quote, or the repair pastes `...","matched_rank":0.03` into the answer —
  // both real, both from the prod audit (execs 126991, 126957).
  const jsonEv = JSON.stringify([
    { title: "TikTok or Die", speakers: "Alex Bonilla, Jonathan Jewett, Brandon Himmel", video_url: "https://app.mds.co/videos/6a908525d5013ff117efaadd", matched_rank: 0.0317 },
    { title: "Live Launch Teardown", speakers: "Nathan Ross, Eva Maxfield, John Spektor", video_url: "https://app.mds.co/videos/6a908525d5013ff117efbbbb", matched_rank: 0.0299 },
  ]);
  const draft = [
    "• *TikTok or Die* — Alex Bonilla, Jonathan Jewett & Brandon Himmel on cold-start growth",
    "• Nathan Ross's live launch teardown with Eva Maxfield & John Spektor",
  ].join(NL);
  const out = repairLinks(draft, jsonEv);
  const tiktok = out.text.split(NL).find((l) => l.includes("TikTok or Die"));
  const teardown = out.text.split(NL).find((l) => l.includes("Nathan Ross"));
  has("tiktok line gets the tiktok video", tiktok, "6a908525d5013ff117efaadd");
  has("teardown line gets the teardown video", teardown, "6a908525d5013ff117efbbbb");
  hasNot("no JSON tail is pasted in", out.text, "matched_rank");
  hasNot("no trailing quote is pasted in", out.text, '"');
}

console.log("repairLinks — a weak or near-tied match is not a match");
{
  const ev = JSON.stringify([
    { title: "Summit Recap Session", url: "https://app.mds.co/videos/1111111111111111aaaa" },
    { title: "Summit Recap Panel", url: "https://app.mds.co/videos/2222222222222222bbbb" },
  ]);
  // shares "Summit" and "Recap" with BOTH rows — one word of daylight is not enough
  const out = repairLinks("• *Summit Recap Session* — the wrap-up", ev);
  eq("a one-token margin is treated as ambiguous", out.repaired, 0);
}
{
  const ev = JSON.stringify([{ chat: "MDS AI & Automations", note: "Joseph Cowling on repricing", url: "https://facebook.com/groups/699138040189700/posts/12345678901" }]);
  const out = repairLinks("• Christian Verhoeven started a discussion on why AI-written text feels lazy", ev);
  eq("an item sharing only a generic word is left alone", out.repaired, 0);
}

console.log("repairLinks — a row is matched on WHAT IT IS, never on its body text");
{
  // Both wrong repairs found in the prod audit (exec 126957) came from one
  // long announcement post whose BODY listed the whole Summit line-up. A
  // 400-char window around a neighbouring url swept those names in, so
  // "Brandon Himmel shared…" collected a video url and "Nathan Ross's
  // teardown" collected an unrelated FB post. Identity fields only.
  const ev = JSON.stringify([
    {
      source: "fb_post",
      title: "Summit line-up announcement",
      url: "https://www.facebook.com/groups/699138040189700/posts/27046939001649578/",
      body: "TikTok Panel - Brandon Himmel, Jon Jewett, Alex Bonilla. Launching Hotseat - Nathan Ross will get grilled by Jon Spektor and Eva Maxfield about his failed launches.",
      meta: { author_name: "Eugene Khayman" },
    },
    { source: "video", title: "TikTok or Die", speakers: "Brandon Himmel, Jonathan Jewett, Alex Bonilla", url: "https://app.mds.co/videos/6a908525d5013ff117efaadd" },
  ]);
  const out = repairLinks("• Nathan Ross's live launch teardown with Eva Maxfield & John Spektor", ev);
  eq("a name that appears only in a body is not a match", out.repaired, 0);

  const out2 = repairLinks("• *TikTok or Die* — Brandon Himmel, Jonathan Jewett & Alex Bonilla", ev);
  has("but a title match still lands", out2.text, "6a908525d5013ff117efaadd");
  hasNot("and never the announcement post", out2.text, "27046939001649578");
}

console.log("repairLinks — who WROTE a row is not what the row IS");
{
  // The wrong link that reached prod (exec 127539, promoted and rolled back
  // 2026-09-02). The row is a WhatsApp message with title:null whose only
  // identity-ish text was author_name + post_author, both "Brandon Himmel" —
  // two tokens, no runner-up, so it won. A Brandon Himmel quote about SQP
  // reports collected the permalink of his message about units damaged in the
  // rain. For a post, comment or message, the author is not the subject.
  const ev = JSON.stringify([
    {
      source: "wa_message",
      kind: "text",
      title: null,
      body: "There was not insurance but this is a DDP shipment and I told them someone needs to eat the cost of these units.",
      url: "https://www.facebook.com/groups/699138040189700/posts/25723134034030088/?comment_id=25731926246484200",
      meta: { author_name: "Brandon Himmel", post_author: "Brandon Himmel" },
    },
  ]);
  const out = repairLinks('• Brandon Himmel: "I pull the SQP report and then do a target search in ads console" — competitor unit estimates', ev);
  eq("an authored row never matches on its author's name", out.repaired, 0);
}
{
  // But a person IS the identity of a member row, and that link is the point.
  const ev = JSON.stringify([
    { source: "member", full_name: "Alex Lushington", chapter: "SoTex", profile_url: "https://app.mds.co/members/rec123456789" },
  ]);
  const out = repairLinks("• *Alex Lushington* — Austin, SoTex Chapter", ev);
  has("a member row still lends its profile link", out.text, "rec123456789");
}

console.log("repairLinks — a url inside a row's PROSE is not that row's link");
{
  // The second wrong link, from the re-audit (exec 127638). Partner rows in that
  // evidence carry NO link field at all — the only url in the blob sat inside
  // Zenon Labs' own description ("Featured work: https://kos.com …"). With no
  // structured link to find, the answer must simply keep no link. A row lends a
  // link only from an explicit link FIELD; there is no window fallback.
  const partners = JSON.stringify([
    { name: "Some Partner", offer_value: "10% OFF", description_snippet: "Amazon PPC and ads." },
    { name: "Zenon Labs", offer_value: "15% OFF", description_snippet: "Shopify CRO and UI/UX experts. Featured work: https://kos.com presents our design work." },
  ]);
  const out = repairLinks("• Zenon Labs — CRO-focused Shopify UI/UX design/dev team, 15% off for members", partners);
  eq("a url in prose never becomes the item's link", out.repaired, 0);
  hasNot("kos.com is not attached", out.text, "kos.com");
}

console.log(NL + (fail === 0 ? "ALL " + pass + " PASS" : pass + " pass, " + fail + " FAIL"));
process.exit(fail === 0 ? 0 : 1);
