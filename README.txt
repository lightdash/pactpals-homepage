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
