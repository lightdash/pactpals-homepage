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

The Privacy & cookies control lets visitors allow or decline analytics and
change their choice later. No Google script loads before permission. Advertising
storage, ad personalization and Google signals are disabled. Email addresses
are never passed to GA. Page URLs contain only recognized campaign tags;
referrers are reduced to their hostname. Google remains blocked on decline.

Use lowercase campaign labels consistently, for example:
https://pactpals.com/?utm_source=reddit&utm_medium=social&utm_campaign=launch&utm_content=gamification
https://pactpals.com/?utm_source=reddit&utm_medium=social&utm_campaign=launch&utm_content=fitness_gaming
https://pactpals.com/?utm_source=discord&utm_medium=social&utm_campaign=launch&utm_content=gaming_friends

GA4 Reports > Acquisition > Traffic acquisition shows session source/medium
and campaign. Session manual ad content distinguishes utm_content (individual
subreddits/posts), available in report customization or Explorations.
Compare sessions and generate_lead key events; figures include consenting,
unblocked visitors only. The same successful form submission is counted at
most once per browser-tab session. Repeat signups in another session may count
again, so unique email counts in PostgreSQL remain the signup source of truth.

After consent, the homepage also sends optional attribution (the five standard
UTM fields and referring hostname) to the API. Attribution survives navigation
in the same tab; a new campaign replaces it. The database preserves attribution
from the email's original signup. No consent means email-only signup. Historical
visits and preexisting signups cannot be backfilled. Never put emails, tokens,
or personal details in campaign links.

Checks: pnpm exec tsc --noEmit; node --experimental-strip-types --test
test/analytics.test.mjs; NODE_ENV=production pnpm build.
