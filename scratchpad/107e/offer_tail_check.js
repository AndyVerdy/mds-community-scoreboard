
const OFFER_TAIL = /(want (a|the) quick summary|want me to|want the (link|details|rest)|would you like me to|shall i (send|pull|share)|should i (send|pull|share))[^?]{0,80}\?\s*$/i;
const cases = {
  lead: "Here are the Summit attendees I've recommended to you that I can reach for an intro. Pick one and I'll ask them for their ok \u2014 they see your name and the topic, nothing else. I'll message you the moment they respond; if there's no answer in 7 days I'll let you know and we can try someone else.",
  fallback: "None of the attendees I've recommended to you can take an intro request right now. Want other names?",
};
for (const [name, text] of Object.entries(cases)) {
  const t = text.trim();
  const offerTail = OFFER_TAIL.test(t);
  const replyYes = /reply\s+YES\b/i.test(t);
  const ticketPhrase = t.toLowerCase().indexOf('open a ticket with the mds team') !== -1;
  const introOfferTail = /would you like me to connect you with one of them\?\s*$/i.test(t);
  console.log(`${name} | len=${t.length} | OFFER_TAIL=${offerTail} | replyYES=${replyYes} | ticketPhrase=${ticketPhrase} | INTRO_OFFER_TAIL=${introOfferTail}`);
}
