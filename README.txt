Pact Pals homepage
=================

Public site: https://lightdash.github.io/pactpals-homepage/
Deploys automatically through GitHub Actions on pushes to v0/pact-pals-homepage.

Build with Node 24 and pnpm 12.3.4:
  pnpm install --frozen-lockfile
  NODE_ENV=production NEXT_PUBLIC_BASE_PATH=/pactpals-homepage pnpm build
  pnpm exec tsc --noEmit

GitHub Pages serves the static out/ directory. The waitlist submits to
https://fit-buds-api.onrender.com/public/waitlist. That service validates and
normalizes addresses and stores them in its private PostgreSQL waitlist_signups
table. The browser needs no credentials. Duplicate signups succeed without
adding another row. No emails are automatically sent. See lightdash/pactpals
API.txt for the endpoint contract. Vercel-only analytics are not loaded here.

Connect pactpals.com later
-------------------------
DNS has intentionally not been changed yet.
1. In this repo's Settings > Pages, set the custom domain to pactpals.com.
2. In Namecheap Advanced DNS, replace only conflicting web/parking records at
   @ and www. Preserve mail and unrelated records. Add these records:
   A      @      185.199.108.153
   A      @      185.199.109.153
   A      @      185.199.110.153
   A      @      185.199.111.153
   CNAME  www    lightdash.github.io
3. Set NEXT_PUBLIC_BASE_PATH to an empty string in .github/workflows/pages.yml
   and redeploy. Root assets must no longer use /pactpals-homepage.
4. Wait for GitHub's DNS check and HTTPS certificate, then enable Enforce HTTPS.
5. Check the homepage, images, and waitlist at https://pactpals.com.

Official DNS guidance:
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
