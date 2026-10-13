Pact Pals homepage
=================

Public site: https://pactpals.com/
Deploys automatically through GitHub Actions on pushes to v0/pact-pals-homepage.

Build with Node 24 and pnpm 12.3.4:
  pnpm install --frozen-lockfile
  NODE_ENV=production pnpm build
  pnpm exec tsc --noEmit

GitHub Pages serves the static out/ directory. The waitlist submits to
https://fit-buds-api.onrender.com/public/waitlist. That service validates and
normalizes addresses and stores them in its private PostgreSQL waitlist_signups
table. The browser needs no credentials. Duplicate signups succeed without
adding another row. No emails are automatically sent. See lightdash/pactpals
API.txt for the endpoint contract. Vercel-only analytics are not loaded here.

Homepage design and backup
--------------------------
The current homepage reproduces the supplied reference:
https://claude.ai/artifact/LpwBLEa9jKfL2FP2JnBjsG
Typography is hosted locally in public/fonts. Pet artwork and the watch photograph
are the existing repository assets. The duration selector is a design demo;
its displayed hatch odds are not a server-side game mechanic.

The previous homepage is preserved at Git tag:
backup/homepage-before-claude-design-2026-10-13 (commit 5177847).
A zip can be downloaded from that tag in GitHub.

The custom domain is pactpals.com, with HTTPS enabled. Production builds use an
empty base path. To restore the old design, restore app/page.tsx, app/globals.css,
and app/layout.tsx from the backup tag, then push to the deployment branch.

Google Analytics and traffic sources
------------------------------------
GA4 is enabled only when NEXT_PUBLIC_GA_MEASUREMENT_ID is set at build time.
Set that GitHub Actions repository variable to the web stream's G-... ID, then
run the Deploy homepage to GitHub Pages workflow. This ID is public, not a secret.
Create the web stream for https://pactpals.com with Europe/Lisbon reporting time.
Disable enhanced form-interaction measurement: our custom generate_lead event
fires only after the API accepts a waitlist signup. Mark generate_lead as a key
event in GA4 so acquisition reports can show signup conversion by source.

Analytics starts automatically on page load; there is no cookie banner or
consent control. Advertising storage, ad personalization and Google signals
remain disabled. Email addresses are never passed to GA. Page URLs contain
only recognized campaign tags; referrers are reduced to their hostname.

Use lowercase campaign labels consistently, for example:
https://pactpals.com/?utm_source=reddit&utm_medium=social&utm_campaign=launch&utm_content=gamification
https://pactpals.com/?utm_source=reddit&utm_medium=social&utm_campaign=launch&utm_content=fitness_gaming
https://pactpals.com/?utm_source=discord&utm_medium=social&utm_campaign=launch&utm_content=gaming_friends

GA4 Reports > Acquisition > Traffic acquisition shows session source/medium
and campaign. Session manual ad content distinguishes utm_content (individual
subreddits/posts), available in report customization or Explorations.
Compare sessions and generate_lead key events; figures include visitors whose browsers load
the Google tag (ad blockers can prevent measurement). The same successful form submission is counted at
most once per browser-tab session. Repeat signups in another session may count
again, so unique email counts in PostgreSQL remain the signup source of truth.

The homepage also sends optional attribution (the five standard
UTM fields and referring hostname) to the API. Attribution survives navigation
in the same tab; a new campaign replaces it. The database preserves attribution
from the email's original signup. Historical
visits and preexisting signups cannot be backfilled. Never put emails, tokens,
or personal details in campaign links.

Checks: pnpm exec tsc --noEmit; node --experimental-strip-types --test
test/analytics.test.mjs; NODE_ENV=production pnpm build.

Independent homepage view counter
---------------------------------
POST /public/pageviews (no token) accepts JSON:
{"eventId":"9e3b822d-4526-4bfa-aead-57a4cb1136a0","path":"/","attribution":{"utm_source":"reddit"}}
The Origin header must be https://pactpals.com or https://www.pactpals.com.
OPTIONS preflight is supported. This restriction is not authentication: a
non-browser client can spoof Origin. Never embed a private API token here.

204 means the event is stored (or its UUID was already stored); retries with the
same UUID never add another view. 400 invalid input, 403 disallowed/missing origin,
413 body over 2048 bytes, 429 over 600 POST attempts/minute per server instance,
503 storage unavailable. Fields are strict; only path / is currently accepted.
Attribution optionally contains the five utm_* tags and referrer_host, with the
same character/length limits as waitlist attribution. No arbitrary URL, IP,
user-agent, email, geolocation, session ID or fitness-account linkage is stored
in website_pageviews. The server supplies received_at. Hosting-provider request
logs are separate from this table.

A new UUID is sent once per homepage document load, including reloads. React
remounts do not add views. Local previews and the embedded hatch demo are excluded.
The request is independent of Google Analytics, omits credentials and suppresses
its Referer header. Failure never blocks the page or signup. It is best-effort,
without automatic retry, and cannot recover historical views. JavaScript blockers,
network failures and rate limits can undercount; bots/spoofed events can inflate it.

Read totals privately from the API repository in Render > fit-buds-api > Shell:
  npm run traffic
  npm run traffic -- 2026-10-13 2026-10-13
The default is the last seven Lisbon calendar dates including today. Explicit
start/end dates are inclusive, in Europe/Lisbon. Output includes total views,
daily totals, first/last timestamps and source breakdown (UTM source, otherwise
referring hostname, otherwise direct/unknown). No public read endpoint exists.
Compare to GA4 Views/page_view for the homepage using the same dates/timezone,
not GA Sessions or Users. On launch day compare only after collection started;
the rest of that day's GA views predate this counter. Sources here are event-level,
not GA session attribution. Rows persist until explicitly removed; no automatic
expiry is configured for this prototype.
