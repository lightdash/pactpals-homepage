export const MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID || "";
const ATTRIBUTION_KEY = "pactpals-attribution";
const LEAD_KEY = "pactpals-waitlist-recorded";
const TAGS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"] as const;
export type Attribution = Partial<Record<(typeof TAGS)[number] | "referrer_host", string>>;

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function extractAttribution(href: string, referrer: string): Attribution {
  const result: Attribution = {};
  try {
    const url = new URL(href);
    for (const key of TAGS) {
      const value = url.searchParams.get(key);
      if (value && /^[a-z0-9][a-z0-9 _.-]{0,99}$/i.test(value)) result[key] = value;
    }
    if (referrer) {
      const host = new URL(referrer).hostname;
      if (host !== url.hostname && !["pactpals.com", "www.pactpals.com"].includes(host)
        && /^[a-z0-9.-]{1,253}$/i.test(host)) result.referrer_host = host;
    }
  } catch { /* Invalid URLs are not campaign data. */ }
  return result;
}

export function getAttribution(): Attribution | undefined {
  const current = extractAttribution(window.location.href, document.referrer);
  try {
    if (Object.keys(current).length) {
      sessionStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(current));
      return current;
    }
    const saved = sessionStorage.getItem(ATTRIBUTION_KEY);
    return saved ? JSON.parse(saved) : undefined;
  } catch { return Object.keys(current).length ? current : undefined; }
}

let initialized = false;
let leadRecorded = false;
export function initializeAnalytics() {
  if (initialized || !/^G-[A-Z0-9]+$/.test(MEASUREMENT_ID)) return;
  initialized = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer!.push(arguments); };
  window.gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied", ad_personalization: "denied",
  });
  window.gtag("js", new Date());
  // Send only recognized campaign parameters, never arbitrary query data.
  const cleanUrl = new URL(location.origin + location.pathname);
  const attribution = getAttribution();
  for (const key of TAGS) if (attribution?.[key]) cleanUrl.searchParams.set(key, attribution[key]);
  window.gtag("config", MEASUREMENT_ID, {
    page_location: cleanUrl.href,
    page_referrer: attribution?.referrer_host ? `https://${attribution.referrer_host}/` : "",
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
  });
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
  document.head.appendChild(script);
}

export function trackWaitlistSignup() {
  try {
    if (!initialized || leadRecorded) return;
    try { if (sessionStorage.getItem(LEAD_KEY)) return; } catch { /* Use in-memory deduplication if storage is unavailable. */ }
    window.gtag?.("event", "generate_lead", { method: "waitlist" });
    leadRecorded = true;
    sessionStorage.setItem(LEAD_KEY, "1");
  } catch { /* Analytics must never interfere with signup success. */ }
}
