import { Actor } from 'apify';
import { PlaywrightCrawler, Dataset } from '@crawlee/playwright';

await Actor.init();

const input = await Actor.getInput() || {};
const {
    cookies = [],
    groupUrl = 'https://www.facebook.com/groups/milliondollarsellers',
} = input;
let targetMembers = input.targetMembers || []; // if empty → discover ALL group members
const DISCOVER = targetMembers.length === 0;

const GROUP_ID = '699138040189700';

console.log(`Photo batch scraper: ${targetMembers.length} members to process`);
console.log(`Members: ${targetMembers.map(m => m.name).join(', ')}`);

let results = [];
let dataPushed = false;

// Graceful shutdown
Actor.on('aborting', async () => {
    console.log('ABORTING — pushing partial photo results...');
    if (!dataPushed && results.length > 0) {
        await Dataset.pushData(results);
        dataPushed = true;
    }
});

const proxyConfiguration = input.useResidentialProxy
    ? await Actor.createProxyConfiguration({ groups: ['RESIDENTIAL'], countryCode: input.proxyCountry || 'US' })
    : (input.useProxy ? await Actor.createProxyConfiguration() : undefined);
if (proxyConfiguration) console.log('Using proxy: ' + (input.useResidentialProxy ? 'RESIDENTIAL' : 'datacenter'));

const crawler = new PlaywrightCrawler({
    proxyConfiguration,
    launchContext: { launchOptions: { headless: false } },
    requestHandlerTimeoutSecs: 10800,
    navigationTimeoutSecs: 90,
    async requestHandler({ page }) {
        // Set cookies
        if (cookies.length > 0) {
            const mappedCookies = cookies.map(c => ({
                name: c.name, value: c.value,
                domain: c.domain || '.facebook.com',
                path: c.path || '/',
                httpOnly: c.httpOnly !== undefined ? c.httpOnly : false,
                secure: true,
                sameSite: c.sameSite === 'no_restriction' ? 'None' :
                          c.sameSite === 'lax' ? 'Lax' :
                          c.sameSite === 'strict' ? 'Strict' : 'None',
            }));
            await page.context().addCookies(mappedCookies);
            await page.goto('https://www.facebook.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
            await page.waitForTimeout(2000);
            await page.context().addCookies(mappedCookies);

            const loggedIn = await page.evaluate(() => {
                return !!(document.querySelector('[aria-label="Your profile"]') ||
                    document.querySelector('[aria-label="Account"]') ||
                    document.querySelector('[role="banner"] [role="navigation"]'));
            });
            console.log(`Session: loggedIn=${loggedIn}`);
            if (!loggedIn) {
                console.log('WARNING: May not be logged in. Trying anyway...');
            }
        }

        // Phase 0: discover ALL group members (when no targetMembers given)
        if (DISCOVER) {
            console.log('Phase 0: discovering group members...');
            await page.goto(`https://www.facebook.com/groups/${GROUP_ID}/members`, { waitUntil: 'domcontentloaded', timeout: 40000 });
            await page.waitForTimeout(3500);
            const seen = new Map();
            let stale = 0;
            for (let s = 0; s < 1000 && stale < 25; s++) {
                const batch = await page.evaluate((GID) => {
                    const out = [];
                    document.querySelectorAll('a[href*="/user/"]').forEach((a) => {
                        const m = (a.href || '').match(new RegExp('/groups/' + GID + '/user/(\\d+)'));
                        if (m) out.push({ userId: m[1], name: (a.textContent || '').trim().slice(0, 80) });
                    });
                    return out;
                }, GROUP_ID);
                const before = seen.size;
                for (const b of batch) { if (!seen.has(b.userId) && b.name) seen.set(b.userId, b.name); }
                if (seen.size === before) stale++; else stale = 0;
                if (s % 10 === 0) console.log(`  members scroll ${s}: ${seen.size} found (stale ${stale})`);
                await page.evaluate(() => window.scrollBy(0, 2200));
                await page.waitForTimeout(2000);
            }
            targetMembers = [...seen.entries()].map(([userId, name]) => ({ userId, name }));
            if (input.maxMembers) targetMembers = targetMembers.slice(0, input.maxMembers);
            console.log(`Phase 0 done: ${targetMembers.length} members discovered`);
            if (!targetMembers.length) { await Dataset.pushData([{ error: 'NO_MEMBERS_DISCOVERED' }]); return; }
        }

        let photosFound = 0;
        let loginErrors = 0;

        for (let i = 0; i < targetMembers.length; i++) {
            const member = targetMembers[i];
            try {
                const profileUrl = `https://www.facebook.com/groups/${GROUP_ID}/user/${member.userId}/`;
                await page.goto(profileUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

                // Wait for content to load
                let waited = 0;
                while (waited < 8000) {
                    await page.waitForTimeout(1000);
                    waited += 1000;
                    const hasContent = await page.evaluate(() => {
                        const text = document.body?.innerText || '';
                        return text.length > 500;
                    });
                    if (hasContent) break;
                }

                // Login redirect check
                if (page.url().includes('login') || page.url().includes('checkpoint')) {
                    loginErrors++;
                    console.log(`  [${i+1}/${targetMembers.length}] ${member.name}: LOGIN REDIRECT`);
                    results.push({ name: member.name, userId: member.userId, profilePhoto: null, photoStrategy: 'login-error', photoDiag: [] });
                    if (loginErrors >= 3) {
                        console.log('ERROR: 3 login redirects. Session expired. Stopping.');
                        break;
                    }
                    continue;
                }

                // Extract photo using all strategies
                const photoResult = await page.evaluate(() => {
                    let bestPhoto = null;
                    let photoStrategy = 'none';
                    const photoDiag = [];
                    const memberName = document.querySelector('h1, [role="heading"]')?.textContent?.trim() || '';
                    photoDiag.push('name=' + (memberName || '(empty)'));

                    const isInNav = (el) => {
                        let p = el;
                        for (let i = 0; i < 20 && p; i++) {
                            if (p.getAttribute && (
                                p.getAttribute('role') === 'banner' ||
                                p.getAttribute('role') === 'navigation' ||
                                p.getAttribute('aria-label') === 'Facebook' ||
                                p.getAttribute('data-pagelet') === 'ProfileActions'
                            )) return true;
                            p = p.parentElement;
                        }
                        return false;
                    };

                    const isValidPhoto = (src) => {
                        return src && src.includes('fbcdn.net') &&
                            !src.includes('static.xx.fbcdn.net/rsrc.php') &&
                            !src.includes('emoji');
                    };

                    const mainEl = document.querySelector('[role="main"]');
                    photoDiag.push('hasMain=' + !!mainEl);

                    // Strategy 1: aria-label with member's name
                    if (memberName) {
                        const allImgEls = [...document.querySelectorAll('img[aria-label]')];
                        for (const img of allImgEls) {
                            const label = img.getAttribute('aria-label') || '';
                            if (label.includes(memberName) && isValidPhoto(img.src) && !isInNav(img)) {
                                bestPhoto = img.src;
                                photoStrategy = 'S1-aria-name';
                                photoDiag.push('S1:MATCH');
                                break;
                            }
                        }
                    }

                    // Strategy 2: aria-label "profile picture" NOT in nav
                    if (!bestPhoto) {
                        const profilePicImgs = [...document.querySelectorAll('img[aria-label*="profile picture" i], img[aria-label*="profile photo" i]')];
                        for (const img of profilePicImgs) {
                            if (isValidPhoto(img.src) && !isInNav(img)) {
                                bestPhoto = img.src;
                                photoStrategy = 'S2-profile-pic';
                                photoDiag.push('S2:MATCH');
                                break;
                            }
                        }
                    }

                    // Strategy 3: SVG in main
                    if (!bestPhoto && mainEl) {
                        const svgImgs = [...mainEl.querySelectorAll('svg image, image')];
                        for (const img of svgImgs) {
                            const src = img.getAttribute('xlink:href') || img.getAttribute('href') || '';
                            const svg = img.closest('svg');
                            const w = svg ? (parseInt(svg.getAttribute('width')) || svg.getBoundingClientRect().width) : 0;
                            if (isValidPhoto(src) && w >= 80) {
                                bestPhoto = src;
                                photoStrategy = 'S3-svg-main';
                                photoDiag.push('S3:MATCH w=' + w);
                                break;
                            }
                        }
                    }

                    // Strategy 4: img in main, profile-sized
                    if (!bestPhoto && mainEl) {
                        const imgs = [...mainEl.querySelectorAll('img')];
                        for (const img of imgs) {
                            if (!isValidPhoto(img.src)) continue;
                            const rect = img.getBoundingClientRect();
                            const w = img.naturalWidth || img.width || rect.width || 0;
                            const h = img.naturalHeight || img.height || rect.height || 0;
                            const ratio = Math.max(w, h) > 0 ? Math.abs(w - h) / Math.max(w, h) : 99;
                            if (w >= 80 && h >= 80 && w <= 500 && h <= 500 && ratio < 0.3 && rect.top < 600) {
                                bestPhoto = img.src;
                                photoStrategy = 'S4-img-main';
                                photoDiag.push('S4:MATCH ' + w + 'x' + h);
                                break;
                            }
                        }
                    }

                    // Strategy 5 (FALLBACK): scan ALL page images
                    if (!bestPhoto) {
                        const allImgs = [...document.querySelectorAll('img')];
                        const candidates = [];
                        for (const img of allImgs) {
                            const src = img.src || '';
                            if (!src.includes('fbcdn.net') || src.includes('static.xx.fbcdn.net/rsrc.php') || src.includes('emoji')) continue;
                            const rect = img.getBoundingClientRect();
                            const w = img.naturalWidth || img.width || rect.width || 0;
                            const h = img.naturalHeight || img.height || rect.height || 0;
                            const isProfilePath = src.includes('/t1.6435-1/') || src.includes('/t1.6435-9/');
                            candidates.push({ src, w, h, top: rect.top, isProfilePath });
                        }
                        photoDiag.push('S5:candidates=' + candidates.length);

                        // Also check SVG images
                        const svgCandidates = [];
                        const allSvg = [...document.querySelectorAll('svg image, image')];
                        for (const img of allSvg) {
                            const src = img.getAttribute('xlink:href') || img.getAttribute('href') || '';
                            if (!src.includes('fbcdn.net') || src.includes('static.xx.fbcdn.net/rsrc.php')) continue;
                            const svg = img.closest('svg');
                            const w = svg ? (parseInt(svg.getAttribute('width')) || svg.getBoundingClientRect().width) : 0;
                            const isProfilePath = src.includes('/t1.6435-1/') || src.includes('/t1.6435-9/');
                            svgCandidates.push({ src, w, isProfilePath });
                        }

                        // 5a: squarish profile-path images
                        for (const c of candidates) {
                            const ratio = Math.max(c.w, c.h) > 0 ? Math.abs(c.w - c.h) / Math.max(c.w, c.h) : 99;
                            if (c.isProfilePath && c.w >= 80 && c.h >= 80 && ratio < 0.4) {
                                bestPhoto = c.src;
                                photoStrategy = 'S5-profile-path-square';
                                photoDiag.push('S5a:MATCH ' + c.w + 'x' + c.h);
                                break;
                            }
                        }

                        // 5b: any profile-path >= 80px
                        if (!bestPhoto) {
                            for (const c of candidates) {
                                if (c.isProfilePath && Math.max(c.w, c.h) >= 80) {
                                    bestPhoto = c.src;
                                    photoStrategy = 'S5-profile-path-any';
                                    photoDiag.push('S5b:MATCH ' + c.w + 'x' + c.h);
                                    break;
                                }
                            }
                        }

                        // 5c: SVG profile-path >= 80px
                        if (!bestPhoto) {
                            for (const c of svgCandidates) {
                                if (c.isProfilePath && c.w >= 80) {
                                    bestPhoto = c.src;
                                    photoStrategy = 'S5-svg-profile-path';
                                    photoDiag.push('S5c:MATCH w=' + c.w);
                                    break;
                                }
                            }
                        }

                        // 5d: largest squarish image on page
                        if (!bestPhoto) {
                            const sorted = candidates
                                .filter(c => c.w >= 40 && c.h >= 40 && Math.abs(c.w - c.h) / Math.max(c.w, c.h) < 0.3)
                                .sort((a, b) => (b.w * b.h) - (a.w * a.h));
                            if (sorted.length > 0) {
                                bestPhoto = sorted[0].src;
                                photoStrategy = 'S5-largest-square';
                                photoDiag.push('S5d:MATCH ' + sorted[0].w + 'x' + sorted[0].h);
                            }
                        }

                        // Log first 5 candidates for debugging
                        for (let ci = 0; ci < Math.min(5, candidates.length); ci++) {
                            const c = candidates[ci];
                            photoDiag.push('S5:cand[' + ci + '] ' + c.w + 'x' + c.h + ' prof=' + c.isProfilePath + ' ' + c.src.substring(0, 80));
                        }
                    }

                    // Strategy 6 (NEW): Try clicking the profile photo area to get a larger version
                    // Look for a clickable element near the top of the page that might open the profile pic
                    if (!bestPhoto) {
                        photoDiag.push('S6:skipped(no-click-approach-yet)');
                    }

                    // Upgrade to 720px resolution
                    if (bestPhoto) {
                        bestPhoto = bestPhoto
                            .replace(/\/s\d+x\d+\//, '/s720x720/')
                            .replace(/\/p\d+x\d+\//, '/p720x720/')
                            .replace(/\/c\d+\.\d+\.\d+\.\d+a\//, '/')
                            .replace(/\/cp\d+x\d+\//, '/');
                    }

                    return { profilePhoto: bestPhoto, photoStrategy, photoDiag };
                });

                if (photoResult.profilePhoto) photosFound++;

                // Participation probe: discover the "last 30 days" posts/comments widget
                await page.evaluate(() => window.scrollBy(0, 700));
                await page.waitForTimeout(900);
                const participation = await page.evaluate(() => {
                    const main = document.querySelector('[role="main"]') || document.body;
                    const text = (main.innerText || '');
                    const probe = [];
                    for (const raw of text.split('\n')) {
                        const l = raw.trim();
                        if (l && l.length < 80 && /(\d+|\bno\b)\s*(post|comment)|participation|last 30 days|contribut/i.test(l)) {
                            probe.push(l);
                        }
                    }
                    const pm = text.match(/([\d,]+)\s+posts?\b/i);
                    const cm = text.match(/([\d,]+)\s+comments?\b/i);
                    return {
                        posts30: pm ? parseInt(pm[1].replace(/,/g, '')) : null,
                        comments30: cm ? parseInt(cm[1].replace(/,/g, '')) : null,
                        probe: probe.slice(0, 12),
                    };
                });

                results.push({
                    name: member.name,
                    userId: member.userId,
                    posts30: participation.posts30,
                    comments30: participation.comments30,
                    partProbe: participation.probe,
                    profilePhoto: photoResult.profilePhoto,
                    photoStrategy: photoResult.photoStrategy,
                    photoDiag: photoResult.photoDiag,
                });

                const icon = photoResult.profilePhoto ? '📷' : '❌';
                console.log(`  [${i+1}/${targetMembers.length}] ${member.name}: ${icon} posts=${participation.posts30} comments=${participation.comments30}`);
                if (i < 6) {
                    console.log(`    PART-PROBE: ${participation.probe.join(' || ')}`);
                }

                // Small delay every 5 members
                if (i % 5 === 4) {
                    await page.waitForTimeout(1500);
                }
            } catch (e) {
                console.log(`  [${i+1}/${targetMembers.length}] ${member.name}: ERROR - ${e.message?.substring(0, 80)}`);
                results.push({
                    name: member.name, userId: member.userId,
                    profilePhoto: null, photoStrategy: 'error',
                    photoDiag: [e.message?.substring(0, 100)],
                });
            }
        }

        console.log(`\nDone: ${photosFound}/${targetMembers.length} photos found`);

        if (!dataPushed) {
            await Dataset.pushData(results);
            dataPushed = true;
        }
    },
});

await crawler.run([groupUrl]);
if (!dataPushed && results.length > 0) {
    await Dataset.pushData(results);
    dataPushed = true;
}
await Actor.exit();

