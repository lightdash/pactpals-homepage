"use client";

import { HatchDemo } from "@/components/hatch-demo";
import { type FormEvent, type ReactNode, useState } from "react";
import { getAttribution, trackWaitlistSignup } from "../lib/analytics";

const HATCH_ODDS = {
  7: [60, 28, 10, 2],
  14: [45, 32, 18, 5],
  30: [30, 32, 26, 12],
};
const RARITIES = ["Common", "Uncommon", "Rare", "Legendary"];

const STEPS = [
  ["Choose a goal", "Walks, runs, workouts. Pick what your team will do together."],
  ["Pick a finish line", "Decide how long the pact lasts. Longer pacts, better odds of a rare hatch."],
  ["Seal it with a handshake", "Everyone commits. One shared egg, one shared goal."],
  ["Show up together", "Each day your team contributes, the shell cracks a little further."],
];

const HABIT_POINTS = [
  [
    "Cheer each other on",
    "Your party shares one goal and can see each other’s steps. A little encouragement from friends can help you keep going.",
  ],
  [
    "Progress you can see",
    "Every active day cracks the shell a little further. Watch your streak grow as small steps add up.",
  ],
  [
    "A pace that fits",
    "Choose a 7, 14, or 30 day pact and a goal that suits your starting point. Build a habit without pressure or exhaustion.",
  ],
  [
    "Make a pact together",
    "Start a pact with a friend and make time to move together. A walk after work counts.",
  ],
];

type Pal = {
  name: string;
  you?: boolean;
  steps: number;
  source: string;
  bpm: number;
  move: string;
  streak: string;
  hair: string;
  skin: string;
  shirt: string;
  tile: string;
};

// Sample party for the app and watch mockups.
const PARTY: Pal[] = [
  { name: "Maya", steps: 3524, source: "Health Connect", bpm: 82, move: "41m", streak: "6d", hair: "#3b2416", skin: "#f1c7a0", shirt: "#4cdaf0", tile: "#c6ecf8" },
  { name: "Javi", you: true, steps: 2532, source: "Health Connect", bpm: 74, move: "26m", streak: "3d", hair: "#111a35", skin: "#d9a77c", shirt: "#3ccf6e", tile: "#4cdaf0" },
  { name: "Ines", steps: 2292, source: "Apple Health", bpm: 70, move: "22m", streak: "3d", hair: "#ff7aa0", skin: "#f6d3b3", shirt: "#4cdaf0", tile: "#d9ff2f" },
  { name: "Leo", steps: 1114, source: "Apple Health", bpm: 66, move: "12m", streak: "1d", hair: "#2a1a10", skin: "#b07a52", shirt: "#c9a6ff", tile: "#ffd3df" },
  { name: "Sam", steps: 277, source: "Health Connect", bpm: 61, move: "4m", streak: "0d", hair: "#ffd23f", skin: "#8a5a3a", shirt: "#3ccf6e", tile: "#ffd23f" },
];

// Pixel avatar: H hair, S skin, E eyes, M mouth, T shirt.
const AVATAR = [
  "..HHHHHH..",
  ".HHHHHHHH.",
  ".HSSSSSSH.",
  ".SSESSESS.",
  ".SSSSSSSS.",
  "..SSMMSS..",
  "...SSSS...",
  ".TTTTTTTT.",
  "TTTTTTTTTT",
  "TTTTTTTTTT",
];

function Avatar({ pal, className }: { pal: Pal; className?: string }) {
  const colors: Record<string, string> = {
    H: pal.hair,
    S: pal.skin,
    E: "#111a35",
    M: "#c2264f",
    T: pal.shirt,
  };
  return (
    <svg
      className={className}
      viewBox="0 0 10 10"
      shapeRendering="crispEdges"
      aria-hidden="true"
      style={{ ["--tile" as string]: pal.tile }}
    >
      {AVATAR.flatMap((row, y) =>
        [...row].map((cell, x) =>
          cell === "." ? null : (
            <rect
              key={`${x}-${y}`}
              x={x}
              y={y}
              width="1"
              height="1"
              fill={colors[cell]}
            />
          ),
        ),
      )}
    </svg>
  );
}

const PETS = [
  { name: "Sprout", src: "/pets/pet-sprout.svg" },
  { name: "Puff", src: "/pets/pet-puff.svg" },
  { name: "Pebble", src: "/pets/pet-pebble.svg" },
  { name: "???", src: "/pets/pet-mystery.svg", hidden: true },
];

const FAQ = [
  [
    "What is Pact Pals?",
    "A co-op fitness game. You and your friends shake on a shared goal, and every walk, run, and workout helps a mystery egg hatch into a pet you keep forever.",
  ],
  [
    "Who can I make a pact with?",
    "Friends, adult family members, or your gaming group. The first beta is for adults aged 18 and over, at any fitness level.",
  ],
  [
    "What happens if I miss a day?",
    "Your egg starts to fade. Get back to it with your team and the shell keeps cracking.",
  ],
  [
    "Does a longer pact matter?",
    "Yes. Longer pacts give you better odds of a rare hatch.",
  ],
  [
    "Which devices will it work on?",
    "The Android app is out now, and you can download it from this page. The iOS app is coming soon: sign up and we’ll email you the day it’s released. We’re building for smartwatches too.",
  ],
  [
    "How do I become a founding member?",
    "Join the waitlist now. Founding members get the first beta invites, plus launch news and hatch-day updates. No spam.",
  ],
];

// Pixel cloud: # = body, % = shade.
const CLOUD = [
  "..........####..........",
  "......#########.........",
  "....###########..####...",
  "...################%###.",
  ".######################.",
  "########################",
  "#######################%",
  "%%%#####%%%%%######%%%%%",
  "..%%%%%%%..%%%%%%%%%....",
];

function Cloud({ className }: { className?: string }) {
  return (
    <svg
      className={`cloud ${className ?? ""}`}
      viewBox="0 0 24 9"
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      {CLOUD.flatMap((row, y) =>
        [...row].map((cell, x) =>
          cell === "." ? null : (
            <rect
              key={`${x}-${y}`}
              x={x}
              y={y}
              width="1"
              height="1"
              fill={cell === "#" ? "#fffdf6" : "#d8ccb2"}
            />
          ),
        ),
      )}
    </svg>
  );
}

function Window({
  title,
  icon,
  className,
  children,
}: {
  title: string;
  icon?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={`window ${className ?? ""}`}>
      <div className="window-bar">
        <span className="window-icon" aria-hidden="true">
          {icon ?? "◆"}
        </span>
        <span className="window-title">{title}</span>
        <span className="window-controls" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
      </div>
      <div className="window-body">{children}</div>
    </div>
  );
}

const DISCORD_URL = "https://discord.gg/BYZVmV2y9";
const ANDROID_APK_URL = "https://fit-buds-api.onrender.com/downloads/PactPals.apk";

// Pixel icons on a 9x9 grid.
const ICON_DOWNLOAD = [
  "...###...",
  "...###...",
  "...###...",
  "#########",
  ".#######.",
  "..#####..",
  "...###...",
  "....#....",
  "#########",
];
function PixelIcon({ map, className }: { map: string[]; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 9 9"
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      {map.flatMap((row, y) =>
        [...row].map((cell, x) =>
          cell === "#" ? (
            <rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill="currentColor" />
          ) : null,
        ),
      )}
    </svg>
  );
}

function GetTheApp() {
  return (
    <div className="get-app">
      <a className="store-btn store-android" href={ANDROID_APK_URL}>
        <span className="store-icon">
          <PixelIcon map={ICON_DOWNLOAD} />
        </span>
        <span>
          <small>Android · out now</small>
          Download the app
        </span>
      </a>
      <a className="ios-link" href="#get-app">
        On iPhone? Get notified when it’s out →
      </a>
    </div>
  );
}

const FEATURES = [
  ["See who’s ahead", "Your party, ranked by today’s steps."],
  ["Syncs your steps", "Works with Apple Health and Health Connect."],
  ["Watch a friend", "Flick the watch to any pal in your party."],
  ["Add pals with a code", "Share your friend code to team up."],
];

type WaitlistState = "idle" | "loading" | "joined" | "error";

function WaitlistForm({ id, cta }: { id: string; cta: string }) {
  const [email, setEmail] = useState("");
  const [state, setState] = useState<WaitlistState>("idle");
  async function joinWaitlist(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (state === "loading") return;
    setState("loading");
    try {
      const response = await fetch(
        "https://fit-buds-api.onrender.com/public/waitlist",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, attribution: getAttribution() }),
          signal: AbortSignal.timeout(15000),
        },
      );
      setState(response.ok ? "joined" : "error");
      if (response.ok) {
        setEmail("");
        trackWaitlistSignup();
      }
    } catch {
      setState("error");
    }
  }
  return (
    <div className="waitlist">
      <form onSubmit={joinWaitlist} className="waitlist-form">
        <label className="sr-only" htmlFor={id}>
          Email address
        </label>
        <span className="prompt-mark" aria-hidden="true">
          &gt;
        </span>
        <input
          id={id}
          required
          maxLength={254}
          value={email}
          onChange={(event) => {
            setEmail(event.target.value);
            setState("idle");
          }}
          className="waitlist-input"
          type="email"
          autoComplete="email"
          placeholder="your@email.com"
        />
        <button disabled={state === "loading"} className="btn" type="submit">
          {state === "joined"
            ? "✓ You’re in"
            : state === "loading"
              ? "Joining…"
              : cta}
        </button>
      </form>
      <p className="form-status" role="status" aria-live="polite">
        {state === "error"
          ? "That didn’t go through. Check your email address and try again."
          : state === "joined"
            ? "You’re a founding member. Watch your inbox for your beta invite."
            : "No spam. Just beta invites, launch news, and hatch-day updates."}
      </p>
    </div>
  );
}

function Phone({
  selected,
  onSelect,
}: {
  selected: number;
  onSelect: (index: number) => void;
}) {
  return (
    <div className="phone">
      <div className="phone-screen">
        <div className="status-bar" aria-hidden="true">
          <span>9:41</span>
          <span className="status-icons">
            <i className="signal" />
            <i className="battery" />
          </span>
        </div>
        <p className="app-kicker">Your party</p>
        <p className="app-title">
          Same goal.
          <br />
          <span>Who’s ahead?</span>
        </p>
        <ol className="party">
          {PARTY.map((pal, i) => (
            <li key={pal.name}>
              <button
                type="button"
                className={`party-row${pal.you ? " is-you" : ""}`}
                aria-pressed={selected === i}
                aria-label={`Show ${pal.you ? "your" : `${pal.name}’s`} stats on the watch`}
                onClick={() => onSelect(i)}
              >
                <span className="party-rank">0{i + 1}</span>
                <Avatar pal={pal} className="party-avatar" />
                <span className="party-name">
                  {pal.you ? "You" : pal.name}
                  <small>Today · {pal.source}</small>
                </span>
                <span className="party-steps">
                  {pal.steps.toLocaleString("en-US")}
                  <small>steps</small>
                </span>
              </button>
            </li>
          ))}
        </ol>
        <div className="friend-code">
          <span>Your friend code</span>
          <strong>PAL-7K2Q</strong>
          <span className="friend-share">Share</span>
        </div>
        <div className="app-tabs" aria-hidden="true">
          <span>
            <i className="tab-icon tab-today" />
            Today
          </span>
          <span className="is-active">
            <img src="/pact-logo-1.svg" width="21" height="17" alt="" />
            Pals
          </span>
          <span>
            <i className="tab-icon tab-pacts" />
            Pacts
          </span>
          <span>
            <i className="tab-icon tab-profile" />
            Profile
          </span>
        </div>
        <span className="home-bar" aria-hidden="true" />
      </div>
    </div>
  );
}

function Watch({ pal }: { pal: Pal }) {
  const progress = Math.min(100, pal.steps / 100);
  return (
    <div className="watch" aria-live="polite">
      <span className="strap strap-top" aria-hidden="true" />
      <div className="watch-case">
        <span className="crown" aria-hidden="true" />
        <div className="watch-face">
          <span className="watch-ring" aria-hidden="true" />
          <span className="watch-nav watch-prev" aria-hidden="true">
            ‹
          </span>
          <span className="watch-nav watch-next" aria-hidden="true">
            ›
          </span>
          <span className="watch-heart" aria-hidden="true">
            ♥
          </span>
          <span className="watch-link">Bluetooth linked</span>
          <span className="watch-who">
            {pal.name} / {pal.you ? "You" : "Friend"}
          </span>
          <span className="watch-tile" style={{ background: pal.tile }}>
            <Avatar pal={pal} className="watch-avatar" />
          </span>
          <span className="watch-steps">
            {pal.steps.toLocaleString("en-US")}
          </span>
          <span className="watch-goal">Steps / 10,000</span>
          <span className="watch-bar" aria-hidden="true">
            <span style={{ width: `${progress}%` }} />
          </span>
          <span className="watch-stats">
            <span>
              {pal.bpm}
              <small>BPM</small>
            </span>
            <span>
              {pal.move}
              <small>Move</small>
            </span>
            <span>
              {pal.streak}
              <small>Streak</small>
            </span>
          </span>
        </div>
      </div>
      <span className="strap strap-bottom" aria-hidden="true" />
    </div>
  );
}

export default function Page() {
  const [days, setDays] = useState<7 | 14 | 30>(14);
  const [selected, setSelected] = useState(1);
  const odds = HATCH_ODDS[days];
  return (
    <>
      <div className="app-bar">
        <p className="app-bar-text">
          <span className="app-bar-dot" aria-hidden="true" />
          <strong>Pact Pals is out now on Android.</strong>
          <span className="app-bar-ios">iPhone coming soon.</span>
        </p>
        <div className="app-bar-actions">
          <a className="app-bar-btn" href={ANDROID_APK_URL}>
            <PixelIcon map={ICON_DOWNLOAD} className="btn-icon" />
            Download for Android
          </a>
          <a className="app-bar-link" href="#get-app">
            Get notified for iPhone →
          </a>
        </div>
      </div>
      <header className="nav">
        <a className="brand" href="#top">
          <img
            src="/pact-logo-1.svg"
            width="42"
            height="34"
            alt=""
            aria-hidden="true"
          />
          <span>
            Pact<span className="brand-pals">Pals</span>
          </span>
        </a>
        <nav className="nav-links" aria-label="Sections">
          <a href="#how-it-works">How it works</a>
          <a href="#pets">The pets</a>
          <a href="#habits">Build a habit</a>
          <a href="#faq">FAQ</a>
          <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer">
            Discord ↗
          </a>
        </nav>
        <a className="btn btn-small" href="#get-app">
          Get the app
        </a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-sky" aria-hidden="true">
            <Cloud className="cloud-a" />
            <Cloud className="cloud-b" />
            <Cloud className="cloud-c" />
            <Cloud className="cloud-d" />
            <Cloud className="cloud-e" />
          </div>
          <div className="hero-inner">
            <div className="hero-copy">
              <h1 className="hero-title">
                Make fitness your <span className="hl-pink">side quest.</span>
              </h1>
              <p className="hero-sub">
                Shake on a shared goal with your friends, track every step on
                your phone and watch, and hatch a pet you keep forever.
              </p>
              <GetTheApp />
            </div>
            <div className="hero-devices">
              <div className="devices">
                <img
                  className="device-pet hop-1"
                  src="/pets/pet-sprout.svg"
                  alt=""
                  aria-hidden="true"
                />
                <Phone selected={selected} onSelect={setSelected} />
                <div className="watch-col">
                  <Watch pal={PARTY[selected]} />
                  <p className="device-hint">Tap a pal to see them here</p>
                </div>
              </div>
            </div>
          </div>
          <div className="ground" aria-hidden="true" />
        </section>

        <section className="section get-app-section" id="get-app">
          <div className="center-head">
            <p className="kicker">Get the app</p>
            <h2 className="h2">
              Android is here. <span className="hl-lime">iPhone is next.</span>
            </h2>
          </div>
          <div className="platform-grid">
            <Window title="pact_pals.apk" icon="▼" className="platform platform-android">
              <span className="platform-status is-live">
                <i aria-hidden="true" /> Out now
              </span>
              <h3>Android</h3>
              <p>
                Download Pact Pals for Android, start a pact, and add your pals
                with a friend code.
              </p>
              <a className="btn btn-big" href={ANDROID_APK_URL}>
                <PixelIcon map={ICON_DOWNLOAD} className="btn-icon" />
                Download for Android
              </a>
              <p className="platform-fine">
                Free download, straight from us. Android may ask you to allow
                installs from your browser the first time.
              </p>
            </Window>
            <Window title="pact_pals_ios" icon="◷" className="platform platform-ios">
              <span className="platform-status is-soon">
                <i aria-hidden="true" /> Coming soon
              </span>
              <h3>iPhone</h3>
              <p>
                The iOS app is on its way. Leave your email and we’ll tell you
                the day it’s released.
              </p>
              <WaitlistForm id="ios-email" cta="Notify me" />
            </Window>
          </div>
        </section>

        <section className="features" id="app" aria-label="In the app">
          {FEATURES.map(([title, body]) => (
            <p key={title}>
              <span className="feature-mark">[+]</span>
              <strong>{title}</strong>
              <span>{body}</span>
            </p>
          ))}
        </section>
        <section className="section" id="how-it-works">
          <div className="split">
            <div>
              <p className="kicker">How it works</p>
              <h2 className="h2">
                Make a pact.
                <br />
                <span className="hl-lime">Raise a pal.</span>
              </h2>
              <p className="lede">
                The egg is your save file. Each day your team contributes, the
                shell cracks a little further. Miss a day and your egg starts
                to fade.
              </p>
            </div>
            <ol className="steps">
              {STEPS.map(([title, body], i) => (
                <li key={title}>
                  <span className="step-num">[0{i + 1}]</span>
                  <span className="step-title">{title}</span>
                  <span className="step-body">{body}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="section" id="try">
          <div className="center-head">
            <p className="kicker">Try a pact</p>
            <h2 className="h2">
              Tap to <span className="hl-lime">hatch.</span>
            </h2>
            <p className="lede">
              Everyone hits their steps, every day. Miss one and the egg
              fades.
            </p>
          </div>
          <HatchDemo />
        </section>

        <section className="section" id="pets">
          <div className="center-head">
            <p className="kicker">The hatch is a surprise</p>
            <h2 className="h2">
              Same pact. <span className="hl-lime">New pet.</span>
            </h2>
            <p className="lede">
              When the shell finally cracks, a mystery pal joins your
              collection. Keep every creature in your library and start the
              next quest.
            </p>
          </div>
          <div className="pets-grid">
            <Window title="Hatch odds" icon="%">
              <div className="tabs" role="group" aria-label="Pact length">
                {([7, 14, 30] as const).map((d) => (
                  <button
                    key={d}
                    type="button"
                    className="tab"
                    aria-pressed={days === d}
                    onClick={() => setDays(d)}
                  >
                    {d} days
                  </button>
                ))}
              </div>
              <div className="odds">
                {RARITIES.map((label, i) => (
                  <div className="odds-row" key={label}>
                    <span>{label}</span>
                    <span className="odds-track">
                      <span
                        className={`odds-fill rarity-${i}`}
                        style={{ width: `${odds[i]}%` }}
                      />
                    </span>
                    <span className="odds-value">{odds[i]}%</span>
                  </div>
                ))}
              </div>
              <p className="window-note">
                Longer pacts, better odds of a rare hatch.
              </p>
            </Window>
            <Window title="Pet library: 3 / 4 found" icon="▦">
              <div className="library">
                {PETS.map((pet, i) => (
                  <figure key={pet.name} className="library-slot">
                    <img
                      src={pet.src}
                      alt={pet.hidden ? "Undiscovered pet" : pet.name}
                      className={pet.hidden ? "is-hidden" : `hop-${(i % 3) + 1}`}
                    />
                    <figcaption>{pet.name}</figcaption>
                  </figure>
                ))}
              </div>
            </Window>
          </div>
        </section>

        <section className="section" id="habits">
          <div className="split">
            <div>
              <p className="kicker">For everyday people</p>
              <h2 className="h2">
                Healthy habits,
                <br />
                <span className="hl-lime">at your pace.</span>
              </h2>
              <p className="lede">
                You don’t need to be fit to start. Pick a manageable goal,
                invite a friend, and give each other a reason to get moving.
                The first beta is for adults aged 18 and over.
              </p>
            </div>
            <Window title="everyday_pact" icon="♥">
              <ul className="checklist">
                {HABIT_POINTS.map(([title, body]) => (
                  <li key={title}>
                    <span className="check" aria-hidden="true">
                      [✓]
                    </span>
                    <span className="step-title">{title}</span>
                    <span className="step-body">{body}</span>
                  </li>
                ))}
              </ul>
            </Window>
          </div>
        </section>

        <section className="section join" id="join">
          <Cloud className="join-cloud join-cloud-l" />
          <Cloud className="join-cloud join-cloud-r" />
          <Window title="founding_members" icon="✦" className="join-window">
            <div className="join-body">
              <p className="live-badge">
                <span className="live-dot" aria-hidden="true" />
                Early access is open now
              </p>
              <h2 className="h2">
                Become a <span className="hl-lime">founding member.</span>
              </h2>
              <p className="lede">
                Don’t wait for launch day. Founding members get in first,
                play before everyone else, and help shape the game for friends,
                gamers, and anyone starting a new habit. Beta access is for ages 18+.
              </p>
              <ul className="perks">
                <li>
                  <span aria-hidden="true">[✓]</span> First in line for beta
                  invites
                </li>
                <li>
                  <span aria-hidden="true">[✓]</span> A say in what we build
                  next
                </li>
                <li>
                  <span aria-hidden="true">[✓]</span> Launch news and hatch-day
                  updates
                </li>
              </ul>
              <WaitlistForm id="join-email" cta="Claim my spot" />
              <div className="discord-card">
                <span>
                  <strong>Meet the other founding members</strong>
                  Chat with the team, share ideas, and find pals for your
                  first pact.
                </span>
                <a
                  className="btn btn-dark"
                  href={DISCORD_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Join our Discord ↗
                </a>
              </div>
            </div>
          </Window>
        </section>

        <section className="section" id="faq">
          <div className="split">
            <h2 className="h2">FAQ</h2>
            <div className="faq">
              {FAQ.map(([q, a]) => (
                <details key={q}>
                  <summary>{q}</summary>
                  <p>{a}</p>
                </details>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-sky" aria-hidden="true">
          <Cloud className="cloud-f1" />
          <Cloud className="cloud-f2" />
        </div>
        <div className="footer-inner">
          <p className="footer-line">
            Insert good
            <br />
            habit here.
          </p>
          <div className="footer-cols">
            <div>
              <span className="footer-head">Pact Pals</span>
              <a href="#how-it-works">How it works</a>
              <a href="#pets">The pets</a>
              <a href="#habits">Build a habit</a>
              <a href="#faq">FAQ</a>
            </div>
            <div>
              <span className="footer-head">Early access</span>
              <a href="#join">Become a founding member</a>
            </div>
            <div>
              <span className="footer-head">Get the app</span>
              <a href={ANDROID_APK_URL}>Download for Android</a>
              <a href="#join">iOS: coming soon</a>
            </div>
            <div>
              <span className="footer-head">Privacy & support</span>
              <a href="https://fit-buds-api.onrender.com/privacy">Privacy policy</a>
              <a href="https://fit-buds-api.onrender.com/delete-account">Delete account</a>
              <a href="mailto:rephus@gmail.com">Contact Coconauts</a>
            </div>
            <div>
              <span className="footer-head">Community</span>
              <a href={DISCORD_URL} target="_blank" rel="noopener noreferrer">
                Discord ↗
              </a>
            </div>
          </div>
        </div>
        <div className="footer-base">
          <span>© 2026 Pact Pals</span>
          <span>♥ Built together</span>
        </div>
      </footer>
    </>
  );
}
