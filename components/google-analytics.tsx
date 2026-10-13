"use client";

import { useEffect } from "react";
import { initializeAnalytics, recordPageview } from "../lib/analytics";

export default function GoogleAnalytics() {
  useEffect(() => {
    recordPageview();
    initializeAnalytics();
  }, []);
  return null;
}
