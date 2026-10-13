"use client";

import { useEffect, useState } from "react";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";

export function HatchDemo() {
  const [height, setHeight] = useState(760);
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const h = event.data?.ppHatchHeight;
      if (typeof h === "number" && h > 200) setHeight(Math.ceil(h));
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);
  return (
    <iframe
      className="hatch-frame"
      src={`${BASE}/hatch-demo/index.html`}
      title="Try a Daily 5K Steps Pact"
      style={{ height }}
      loading="lazy"
    />
  );
}
