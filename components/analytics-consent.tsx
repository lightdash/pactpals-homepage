"use client";

import { useEffect, useState } from "react";
import { applyConsent, MEASUREMENT_ID, readConsent, type Consent } from "../lib/analytics";

export default function AnalyticsConsent() {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!MEASUREMENT_ID) return;
    const saved = readConsent();
    if (saved) applyConsent(saved);
    else setOpen(true);
  }, []);

  function choose(consent: Consent) {
    applyConsent(consent);
    setOpen(false);
  }
  if (!MEASUREMENT_ID) return null;
  return (
    <>
      <button className="analytics-settings" onClick={() => setOpen(true)}>Privacy & cookies</button>
      {open && (
        <section className="analytics-consent" aria-label="Analytics preferences">
          <strong>A little help finding our pals?</strong>
          <p>With your permission, Google Analytics uses cookies to measure visits, where people find us, and waitlist signups. We also save campaign tags with your signup. Your email is never sent to Google Analytics. You can change your choice below anytime.</p>
          <div>
            <button onClick={() => choose("denied")}>No thanks</button>
            <button onClick={() => choose("granted")}>Allow analytics</button>
          </div>
        </section>
      )}
    </>
  );
}
