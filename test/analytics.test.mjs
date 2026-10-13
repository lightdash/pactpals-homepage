import { test } from 'node:test';
import assert from 'node:assert/strict';
process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID = 'G-TEST123';
const analytics = await import('../lib/analytics.ts');

test('campaign extraction keeps only bounded tags and the referring hostname', () => {
  assert.deepEqual(analytics.extractAttribution('https://pactpals.com/?utm_source=reddit&utm_medium=social&utm_content=gamification&email=private@example.com', 'https://www.reddit.com/r/gamification/?secret=hidden'), {
    utm_source: 'reddit', utm_medium: 'social', utm_content: 'gamification', referrer_host: 'www.reddit.com',
  });
  assert.deepEqual(analytics.extractAttribution('https://pactpals.com/?utm_source=private@example.com&utm_content=' + 'a'.repeat(101), 'https://pactpals.com/'), {});
});

test('analytics starts immediately once; signup has no email and repeats only once per session', () => {
  const makeStorage = () => {
    const values = new Map();
    return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value), removeItem: key => values.delete(key) };
  };
  globalThis.sessionStorage = makeStorage();
  globalThis.location = new URL('https://pactpals.com/?utm_source=reddit&utm_campaign=launch&email=private@example.com');
  globalThis.window = { location };
  const scripts = [];
  globalThis.document = { referrer: 'https://www.reddit.com/private?token=secret', cookie: '', createElement: () => ({}), head: { appendChild: script => scripts.push(script) } };
  analytics.initializeAnalytics();
  assert.equal(scripts.length, 1);
  assert.equal(scripts[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-TEST123');
  analytics.initializeAnalytics();
  assert.equal(scripts.length, 1);
  const originalGtag = window.gtag;
  window.gtag = () => { throw Error('blocked'); };
  assert.doesNotThrow(() => analytics.trackWaitlistSignup());
  window.gtag = originalGtag;
  globalThis.sessionStorage = { getItem: () => { throw Error('storage blocked'); }, setItem: () => { throw Error('storage blocked'); } };
  assert.deepEqual(analytics.getAttribution(), { utm_source: 'reddit', utm_campaign: 'launch', referrer_host: 'www.reddit.com' });
  analytics.trackWaitlistSignup();
  analytics.trackWaitlistSignup();
  const calls = window.dataLayer.map(args => [...args]);
  assert.equal(calls.filter(args => args[0] === 'event').length, 1);
  assert.deepEqual(calls.find(args => args[0] === 'event'), ['event', 'generate_lead', { method: 'waitlist' }]);
  assert.ok(!JSON.stringify(calls).includes('private@example.com'));
  assert.ok(!JSON.stringify(calls).includes('secret'));
});
