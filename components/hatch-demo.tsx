"use client";

import { useEffect, useRef, useState } from "react";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";

function contentHeight(frame: HTMLIFrameElement | null) {
  const body = frame?.contentDocument?.body;
  if (!body) return 0;
  const cs = getComputedStyle(body);
  return (
    body.getBoundingClientRect().height +
    parseFloat(cs.marginTop) +
    parseFloat(cs.marginBottom)
  );
}

export function HatchDemo() {
  const ref = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(760);
  function update(h: number) {
    if (h > 200) setHeight(Math.ceil(h));
  }
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const h = event.data?.ppHatchHeight;
      if (typeof h === "number") update(h);
    }
    window.addEventListener("message", onMessage);
    // The iframe may finish loading (and post its height) before this runs.
    update(contentHeight(ref.current));
    return () => window.removeEventListener("message", onMessage);
  }, []);
  return (
    <iframe
      ref={ref}
      className="hatch-frame"
      src={`${BASE}/hatch-demo/index.html`}
      title="Try a Daily 5K Steps Pact"
      style={{ height }}
      loading="lazy"
      onLoad={() => update(contentHeight(ref.current))}
    />
  );
}
