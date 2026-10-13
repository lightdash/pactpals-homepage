"use client";

import { useEffect } from "react";
import { initializeAnalytics } from "../lib/analytics";

export default function GoogleAnalytics() {
  useEffect(() => {
    initializeAnalytics();
  }, []);
  return null;
}
