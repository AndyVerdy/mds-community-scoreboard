const r = $input.first().json;
const to = $('Answer Parse').isExecuted ? $('Answer Parse').first().json.to : $('Build Prompt').first().json.to;
const sourcesUsed = $('Answer Parse').isExecuted ? ($('Answer Parse').first().json.sources_used || null) : null;
let text = '';
try {
  text = (r.content || []).map(function (c) { return (c && c.text) ? c.text : ''; }).join('').trim();
} catch (e) { text = ''; }
if (!text) { text = 'Sorry — I could not generate an answer just now.'; }
// [SEND_IMAGE: <post_id>] — the answer asks to attach that FB post's screenshot(s) (Layer 3).
let imagePostId = '';
const im = text.match(/\[SEND_IMAGE:\s*([0-9]{6,25})\s*\]/i);
if (im) { imagePostId = im[1]; }
text = text.replace(/\s*\[SEND_IMAGE:[^\]]*\]/gi, '').trim();
// Three prompt rules failed to make the model emit [SEND_IMAGE] reliably, so
// stop asking it. If the answer LINKS a Facebook post, that post's picture
// belongs with the answer — an award graphic or agenda is the artefact, and
// describing it to somebody who can see the link is the wrong output. Safe by
// construction: Fetch Post Images returns nothing for a post without images,
// so a text-only post still sends text only.
if (!imagePostId) {
  // ...but ONLY when this turn was a single-post lookup. A catch-up or search
  // answer CITES threads — deriving an image from a cited link attached a
  // context-free warehouse photo to a weekly recap twice (Andy, 2026-08-19).
  let singlePost = false;
  try { singlePost = ($('Plan Request').first().json.op === 'content_lookup'); } catch (e) {}
  const links = text.match(/facebook\.com\/groups\/\d+\/posts\/(\d{6,25})/gi) || [];
  if (singlePost && links.length === 1) {
    const fb = text.match(/facebook\.com\/groups\/\d+\/posts\/(\d{6,25})/i);
    if (fb) { imagePostId = fb[1]; }
  }
}
// [SEND_FILE: <file_key>] — attach a deck/cliff-notes PDF from the video library. The key is
// NEVER trusted here: digest.video_file_for_send() re-validates it server-side (public video,
// allowed kind, in our bucket) so a hallucinated or coaxed key for a RESTRICTED deck cannot send.
let sendFileKey = '';
const fm = text.match(/\[SEND_FILE:\s*([0-9a-fA-F]{12,40}:[0-9]{1,3})\s*\]/);
if (fm) { sendFileKey = fm[1]; }
text = text.replace(/\s*\[SEND_FILE:[^\]]*\]/gi, '').trim();
// WhatsApp formatting: markdown **bold** renders as literal stars on WA — convert to *bold*.
text = text.replace(/\*\*(.+?)\*\*/g, '*$1*');
// The empty-answer guard above runs BEFORE the markers are stripped. Olivia can reply with ONLY
// a [SEND_FILE:]/[SEND_IMAGE:] marker and no prose — then stripping leaves '' and Meta rejects
// the whole message (400 'text.body is required'), so the member gets NOTHING, file included.
// Re-check after stripping and supply a caption instead of failing the send.
if (!text) { text = sendFileKey ? 'Here you go 👇' : (imagePostId ? 'Here you go 👇' : 'Sorry — I could not generate an answer just now.'); }
if (text.length > 3800) { text = text.slice(0, 3800) + '...'; }
// #24: a first-contact QUESTION was answered above — the beta intro rides along after the
// answer instead of replacing it, and this turn marks the member welcomed.
// #107: the PS must not land AFTER an end-of-message offer, or the offer no longer ends the
// text and OFFER_TAIL below stops matching — buttons silently vanish (Aaron Biner's real
// reply, 2026-08-22). So on a button-eligible answer the PS goes FIRST (PS + blank line +
// answer), leaving the offer last; eligibility mirrors the OFFER_TAIL/1024 check below, and
// the 1024 cap is enforced on the FINAL (PS+answer) text — if the PS would push it over, the
// PS is dropped for THIS turn rather than the buttons (the member is still marked welcomed
// either way). A non-eligible answer keeps the original append-at-end.
let markPhone = '';
try {
  const pl = $('Plan Request').first().json;
  if (pl && pl.first_contact) {
    markPhone = to;
    const psLine = '_PS: I am Millie, the MDS assistant (beta). Ask me about the chats, the Facebook group, members, events, partner deals or the video library - anytime._';
    const OFFER_TAIL_PS = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\?\s*$/i;
    const baseHasOffer = /reply\s+YES\b/i.test(text) || text.toLowerCase().indexOf('open a ticket with the mds team') !== -1 || OFFER_TAIL_PS.test(text.trim());
    if (baseHasOffer) {
      // #107c2: Andy 2026-08-22 (closing concern 1) - the PS must go FIRST whenever the
      // answer ends in an offer, REGARDLESS of length. Ruling A made who-to-meet answers
      // uncapped, so "does PS+answer still fit under 1024" is no longer the right test - a
      // first-contact member asking who-to-meet at the Summit WILL get a long rich answer,
      // and the old drop-the-PS-if-it-does-not-fit fallback also silently dropped the offer
      // off the tail (the #38/#107c button logic below both key off wherever `text` ends).
      // The #38 inline-button block and the #107c follow-up-split block below both already
      // handle ANY length correctly from whatever `text` is at this point - keeping the
      // offer as the tail here is all that is needed: PS+answer <=1024 -> inline buttons on
      // the combined text; PS+answer >1024 -> the follow-up split strips the offer off the
      // combined text and the PS still leads the plain-text message. The 1024/3800 guards
      // are unchanged - the 1024 check lives in #38/#107c below, and the bare answer is
      // already <=3800 from the hard cap earlier in this node, so PS+answer stays <=3800+PS
      // (~3960), comfortably under WhatsApp's plain-text ceiling.
      text = psLine + String.fromCharCode(10) + String.fromCharCode(10) + text;
    } else {
      const intro = String.fromCharCode(10) + String.fromCharCode(10) + psLine;
      if (text.length + intro.length <= 3800) { text = text + intro; }
    }
  }
} catch (e) {}
// #57 remainder: a CONFIRMED report stops clean. The seed rule ("confirm in one warm
// line and STOP") kept losing to a trailing soft offer ("if you tell me which event...").
// Same remedy as the rest of #57 - take it out of the model's hands. Only when
// report_create actually fired, so a failed filing is never claimed as a success.
try {
  const _rp = $('Plan Request').first().json;
  if (_rp && _rp.period === 'report_file'
      && (sourcesUsed || []).indexOf('report_create') !== -1) {
    text = 'Sent to the MDS team \uD83D\uDC4D They will see it in their portal.';
  }
} catch (e) {}
// #38: offer-shaped replies become TAP BUTTONS; the billing-portal link becomes a
// CTA-URL button. WA caps interactive bodies at 1024 chars - longer replies stay text.
let interactive = null;
try {
  const PORTAL = 'https://checkout.mds.co/p/login/8wM5l70XvaBC6Ji000';
    // #70c: buttons were never broken - they only ever fired on "reply YES" or the
  // ticket phrase. New offer shapes ("Want a quick summary?") matched neither, so a
  // 540-char reply well under the 1024 cap went out as plain text. Widened to a SMALL,
  // explicit set of offers anchored at the END of the message, where offers sit -
  // deliberately NOT "ends with a question mark", which would button half her replies.
  const OFFER_TAIL = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\?\s*$/i;
  const hasOffer = /reply\s+YES\b/i.test(text) || text.toLowerCase().indexOf('open a ticket with the mds team') !== -1 || OFFER_TAIL.test(text.trim());
  if (hasOffer && text.length <= 1024 && !imagePostId && !sendFileKey) {
    interactive = { type: 'button', body: { text: text },
      action: { buttons: [
        { type: 'reply', reply: { id: 'txt:Yes', title: 'Yes' } },
        { type: 'reply', reply: { id: 'txt:No thanks', title: 'No thanks' } } ] } };
  } else if (text.indexOf(PORTAL) !== -1 && !imagePostId && !sendFileKey) {
    const stripped = text.split(PORTAL).join('').replace(/[ \t]*\n[ \t]*\n[ \t]*\n+/g, String.fromCharCode(10)+String.fromCharCode(10)).trim();
    if (stripped.length <= 1024 && stripped.length > 0) {
      interactive = { type: 'cta_url', body: { text: stripped },
        action: { name: 'cta_url', parameters: { display_text: 'Open billing portal', url: PORTAL } } };
    }
  }
} catch (e) { interactive = null; }
// #107b: WHO-TO-MEET picker -> WhatsApp interactive LIST (POC shape). member_intro with no target returns {pick:[...]}; row ids/titles/descriptions come straight from that HTTP response (Answer Tool's own run this turn), never from the LLM's text, so a picker turn's rows are always exactly what the route offered.
try {
  if ((sourcesUsed || []).indexOf('member_intro') !== -1) {
    let toolItems = [];
    try { toolItems = $('Answer Tool').all().map(function (i) { return i.json; }); } catch (e2) { toolItems = []; }
    let pickBody = null;
    for (const it of toolItems) {
      let b = it;
      if (b && typeof b === 'object' && 'body' in b && ('statusCode' in b || 'headers' in b)) b = b.body;
      if (b && Array.isArray(b.pick)) { pickBody = b; break; }
    }
    if (pickBody) {
      if (pickBody.pick.length > 0) {
        text = "Here are the Summit attendees I've recommended to you that I can reach for an intro. Pick one and I'll ask them for their ok — they see your name and the topic, nothing else. I'll message you the moment they respond; if there's no answer in 7 days I'll let you know and we can try someone else.";
        interactive = { type: 'list',
          body: { text: text },
          footer: { text: 'MDS member introductions' },
          action: { button: 'Pick a member', sections: [ { title: 'Summit attendees',
            rows: pickBody.pick.slice(0, 10).map(function (p) { return { id: p.id, title: p.title, description: p.description }; }) } ] } };
      } else {
        text = "None of the attendees I've recommended to you can take an intro request right now. Want other names?";
        interactive = null;
      }
    }
  }
} catch (e3) {}
// #107c: Andy 2026-08-22 - ruling A removed the who-to-meet length cap, so a rich answer can
// exceed WhatsApp's 1024-char interactive-body limit and the #38 block above leaves `interactive`
// null (buttons silently vanish). Buttons must ALWAYS appear on this offer: split into a plain-text
// main message (offer sentence stripped off the end) + a SECOND interactive-button message carrying
// just the offer, sent by the new "Followup Interactive?" branch off Send Reply (Meta) (mirrors the
// Image/File attachment branches - same $('Format Reply').isExecuted idiom). `reply` below stays the
// STRIPPED text (what actually goes out as the plain-text message); Save Conversation appends the
// offer sentence back onto the LOGGED olivia turn so Plan Request's introOfferPending / Prep
// Context's last_olivia_intro_offer still see it ending in the offer - "Yes" still routes right.
let followupInteractive = null;
try {
  const INTRO_OFFER_TAIL = /would you like me to connect you with one of them\?\s*$/i;
  if (!interactive && !imagePostId && !sendFileKey && text.length > 1024 && INTRO_OFFER_TAIL.test(text.trim())) {
    const OFFER_SENTENCE = 'Would you like me to connect you with one of them?';
    text = text.replace(INTRO_OFFER_TAIL, '').trim();
    followupInteractive = { type: 'button', body: { text: OFFER_SENTENCE },
      action: { buttons: [
        { type: 'reply', reply: { id: 'txt:Yes', title: 'Yes' } },
        { type: 'reply', reply: { id: 'txt:No thanks', title: 'No thanks' } } ] } };
  }
} catch (e4) { followupInteractive = null; }
return [{ json: { to: to, reply: text, interactive: interactive, followup_interactive: followupInteractive, image_post_id: imagePostId, send_file_key: sendFileKey, mark_welcome_phone: markPhone, sources_used: sourcesUsed } }];