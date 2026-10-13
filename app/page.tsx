"use client";

import { type FormEvent, useState } from "react";
import { getAttribution, trackWaitlistSignup } from "../lib/analytics";

const HATCH_ODDS = {
  7: [60, 28, 10, 2],
  14: [45, 32, 18, 5],
  30: [30, 32, 26, 12],
};

export default function Page() {
  const [days, setDays] = useState<7 | 14 | 30>(14);
  const odds = HATCH_ODDS[days];
  const [email, setEmail] = useState("");
  const [waitlistState, setWaitlistState] = useState<
    "idle" | "loading" | "joined" | "error"
  >("idle");
  function goToJoin() {
    document.getElementById("join")?.scrollIntoView({ behavior: "smooth" });
  }
  async function joinWaitlist(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (waitlistState === "loading") return;
    setWaitlistState("loading");
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
      setWaitlistState(response.ok ? "joined" : "error");
      if (response.ok) {
        setEmail("");
        trackWaitlistSignup();
      }
    } catch {
      setWaitlistState("error");
    }
  }
  return (
    <>
      <header className="design-1">
        <a className="design-2" href="#top">
          <img
            src="/pact-pals-egg-logo.svg"
            width="37"
            height="44"
            alt=""
            aria-hidden="true"
          />
          <span className="design-3">
            Pact<span className="design-4">Pals</span>
          </span>
        </a>
        <a className="design-5" href="#how-it-works">
          How it works
        </a>
        <a className="design-5" href="#pets">
          The pets
        </a>
        <a className="design-6" href="#join">
          ▶ Join the waitlist
        </a>
      </header>

      <main id="top">
        <section className="design-7">
          <div className="design-8">
            <h1 className="design-9">
              <span className="design-10">Make fitness</span>
              <span className="design-11">your side</span>
              <span className="design-10">
                quest.<span className="design-12"></span>
              </span>
            </h1>
            <p className="design-13">
              Pick a mystery egg, shake on a shared goal, and show up together.
              Every walk, run, and workout helps your egg hatch into a fully
              formed pet you can keep forever.
            </p>
            <div className="design-14">
              <span className="design-15">♡</span>
              <span className="design-16">
                <strong className="design-17">NURTURE AN EGG</strong>
                <span className="design-18">
                  One shared goal · one surprise hatch
                </span>
              </span>
              <span className="design-19">✔</span>
            </div>
            <div className="design-20">
              <button onClick={goToJoin} className="design-21" type="button">
                <span>▶ Start a pact</span>
              </button>
              <a className="design-22" href="#how-it-works">
                View the quest ▼
              </a>
            </div>
          </div>
        </section>
        <div className="design-23"></div>
        <section className="design-24" id="how-it-works">
          <div className="design-25">
            <div className="design-26">
              <div>
                <span className="design-27">THE EGG IS YOUR SAVE FILE</span>
                <h2 className="design-28">
                  Make a pact.
                  <br />
                  <span className="design-29">Raise a pal.</span>
                </h2>
              </div>
              <p className="design-30">
                Choose a goal, pick a finish line, and seal it with a handshake.
                Each day your team contributes, the shell cracks a little
                further. Miss a day and your egg starts to fade.
              </p>
            </div>
            <div className="design-31">
              <div className="design-32">
                <span className="design-33">01</span>
                <span className="design-34">Choose a goal</span>
                <span className="design-35">
                  Walks, runs, workouts — pick what your team will do together.
                </span>
              </div>
              <div className="design-32">
                <span className="design-33">02</span>
                <span className="design-34">Pick a finish line</span>
                <span className="design-35">
                  Decide how long the pact lasts. Longer pacts, better odds of a
                  rare hatch.
                </span>
              </div>
              <div className="design-32">
                <span className="design-33">03</span>
                <span className="design-34">Seal it with a handshake</span>
                <span className="design-35">
                  Everyone commits. One shared egg, one shared goal.
                </span>
              </div>
              <div className="design-36">
                <span className="design-37">04</span>
                <span className="design-34">Show up together</span>
                <span className="design-35">
                  Each day your team contributes, the shell cracks a little
                  further.
                </span>
              </div>
            </div>
          </div>
        </section>
        <div className="design-38"></div>
        <section className="design-39" id="pets">
          <div className="design-40">
            <span className="design-41">THE HATCH IS A SURPRISE</span>
            <h2 className="design-42">
              Same pact.
              <br />
              <span className="design-43">New pet.</span>
            </h2>
            <p className="design-44">
              When the shell finally cracks, a fully formed mystery pal joins
              your collection. Longer pacts give you better odds of a rare
              hatch. Keep every creature in your library and start the next
              quest.
            </p>
            <div className="design-45">
              <span className="design-46">My pact is</span>
              <button
                onClick={() => setDays(7)}
                aria-pressed={days === 7}
                className="design-47 duration-button"
                type="button"
              >
                <span>7 days</span>
              </button>
              <button
                onClick={() => setDays(14)}
                aria-pressed={days === 14}
                className="design-48 duration-button"
                type="button"
              >
                <span>14 days</span>
              </button>
              <button
                onClick={() => setDays(30)}
                aria-pressed={days === 30}
                className="design-47 duration-button"
                type="button"
              >
                <span>30 days</span>
              </button>
            </div>
            <div className="design-49">
              <span className="design-50">HATCH ODDS</span>
              <div className="design-51">
                <span>
                  <span>Common</span>
                </span>
                <span className="design-52">
                  <span
                    className="design-53"
                    style={{ width: `${odds[0]}%` }}
                  ></span>
                </span>
                <span className="design-54">
                  <span>{odds[0]}</span>%
                </span>
              </div>
              <div className="design-51">
                <span>
                  <span>Uncommon</span>
                </span>
                <span className="design-52">
                  <span
                    className="design-55"
                    style={{ width: `${odds[1]}%` }}
                  ></span>
                </span>
                <span className="design-54">
                  <span>{odds[1]}</span>%
                </span>
              </div>
              <div className="design-51">
                <span>
                  <span>Rare</span>
                </span>
                <span className="design-52">
                  <span
                    className="design-56"
                    style={{ width: `${odds[2]}%` }}
                  ></span>
                </span>
                <span className="design-54">
                  <span>{odds[2]}</span>%
                </span>
              </div>
              <div className="design-51">
                <span>
                  <span>Legendary</span>
                </span>
                <span className="design-52">
                  <span
                    className="design-57"
                    style={{ width: `${odds[3]}%` }}
                  ></span>
                </span>
                <span className="design-54">
                  <span>{odds[3]}</span>%
                </span>
              </div>
            </div>
          </div>
          <div className="design-58">
            <div className="design-59">
              <div className="design-60">
                <span>PET LIBRARY</span>
                <span>
                  <span>3</span>/ 4 FOUND
                </span>
              </div>
              <div className="design-61">
                <div className="design-62">
                  <div className="design-63"></div>
                  <span className="design-64">
                    <span>Sprout</span>
                  </span>
                </div>
                <div className="design-62">
                  <div className="design-65"></div>
                  <span className="design-64">
                    <span>Puff</span>
                  </span>
                </div>
                <div className="design-62">
                  <div className="design-66"></div>
                  <span className="design-64">
                    <span>Pebble</span>
                  </span>
                </div>
                <div className="design-62">
                  <div className="design-67"></div>
                  <span className="design-64">
                    <span>???</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section className="design-68" id="join">
          <div className="design-69">
            <span className="design-41">EARLY ACCESS IS OPEN</span>
            <h2 className="design-70">
              Fitness for gamers.
              <br />
              <span className="design-43">Fun for your kids.</span>
            </h2>
            <p className="design-44">
              Join the first Pact Pals players and help shape a healthy,
              accessible fitness game: co-op fitness for friends, fitness for
              gamers, and a playful way to gamify fitness for your kids without
              pressure or exhaustion.
            </p>
            <form onSubmit={joinWaitlist} className="design-71 waitlist-form">
              <input
                required
                maxLength={254}
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value);
                  setWaitlistState("idle");
                }}
                className="design-72 waitlist-input"
                type="email"
                aria-label="Email address"
                placeholder="your@email.com"
              />
              <button
                disabled={waitlistState === "loading"}
                className="design-73"
                type="submit"
              >
                {waitlistState === "joined"
                  ? "✓ You’re on the list"
                  : waitlistState === "loading"
                    ? "Joining…"
                    : "▶ Join the waitlist"}
              </button>
            </form>
            <span className="design-74" role="status" aria-live="polite">
              {waitlistState === "error"
                ? "Something went wrong. Please try again."
                : waitlistState === "joined"
                  ? "You’re on the list! We’ll be in touch."
                  : "No spam. Just launch news, beta invites, and hatch-day updates."}
            </span>
            <div className="design-75">
              <span className="design-76">iOS</span>
              <span className="design-76">Android</span>
              <span className="design-76">Smartwatches</span>
            </div>
          </div>
          <figure className="design-77">
            <div className="design-78">
              <span>PACT PALS // COMING SOON</span>
              <span className="design-29">⌚</span>
            </div>
            <img
              className="design-79"
              src="/pact-watch-reference.png"
              alt="An early Pact Pals watch prototype showing a shared step goal"
            />
            <figcaption className="design-80">
              <strong className="design-34">The Pact Watch</strong>
              <span className="design-81">
                Your shared egg, your streak, and your pal's progress — right on
                your wrist.
              </span>
            </figcaption>
          </figure>
        </section>
        <div className="design-82"></div>
        <footer className="design-83">
          <div className="design-84">
            <span className="design-85">
              Insert good
              <br />
              habit here.
            </span>
            <div className="design-86">
              <span>© 2026 Pact Pals</span>
              <span>♥ Built together</span>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
