'use client'

import { FormEvent, useState } from 'react'
import { ArrowRight, Check, ChevronRight, Heart, Lock, Users, Watch } from 'lucide-react'

type PactMode = 'nurture'

const hatchStages = [
  { label: 'Egg mode', copy: 'Show up to warm it up', icon: '◒' },
  { label: 'Crack mode', copy: 'Your pact powers the hatch', icon: '✦' },
  { label: 'Pal mode', copy: 'A new teammate is born', icon: '★' },
]

export default function Page() {
  const [joined, setJoined] = useState(false)
  const [stage, setStage] = useState(0)
  const [hatchClicks, setHatchClicks] = useState(0)
  const [eggPulse, setEggPulse] = useState(false)
  const mode: PactMode = 'nurture'

  function tapEgg() {
    const nextClicks = hatchClicks + 1
    setEggPulse(true)
    window.setTimeout(() => setEggPulse(false), 280)
    setHatchClicks(nextClicks)
    if (nextClicks >= 6) setStage(2)
    else if (nextClicks >= 2) setStage(1)
    else setStage(0)
  }
  const [email, setEmail] = useState('')
  const [waitlistState, setWaitlistState] = useState<'idle' | 'loading' | 'joined' | 'error'>('idle')
  const isNurture = mode === 'nurture'

  async function joinWaitlist(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setWaitlistState('loading')
    try {
      const response = await fetch('https://fit-buds-api.onrender.com/public/waitlist', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }), signal: AbortSignal.timeout(15000) })
      setWaitlistState(response.ok ? 'joined' : 'error')
      if (response.ok) setEmail('')
    } catch {
      setWaitlistState('error')
    }
  }

  return (
    <main className={`pact-shell ${isNurture ? 'mode-nurture' : 'mode-conquer'}`}>
      <nav className="topbar" aria-label="Main navigation">
        <a className="brand" href="#top" aria-label="Pact Pals home"><span className="brand-mark"><Heart size={15} fill="currentColor" strokeWidth={2.5} /></span><span>PACT<span className="brand-accent">PALS</span></span></a>
        <div className="nav-pill"><span className="live-dot" /> FITNESS FOR GAMERS</div>
        <button className="nav-link" type="button" onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}>HOW IT WORKS <ChevronRight size={15} /></button>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-line" /> CO-OP FITNESS FOR FRIENDS</p>
          <h1>Make fitness<br /><em>your side quest.</em></h1>
          <p className="hero-description">Pick a mystery egg, shake on a shared goal, and show up together. Every walk, run, and workout helps your egg hatch into a fully formed pet you can keep forever.</p>
          <div className="mode-picker" aria-label="Your pact type"><div className="mode-choice selected"><span className="mode-icon">♡</span><span><strong>NURTURE AN EGG</strong><small>One shared goal · one surprise hatch</small></span><Check size={16} /></div></div>
          <div className="hero-actions"><button className="primary-button" type="button" onClick={() => setJoined(true)}>{joined ? 'PACT JOINED' : 'START A PACT'} <ArrowRight size={17} /></button><button className="text-button" type="button" onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}>VIEW THE QUEST <ChevronRight size={15} /></button></div>
          <div className="social-proof"><div className="avatar-stack"><span>J</span><span>M</span><span>A</span><span>+</span></div><span>MADE FOR FRIENDS WHO SHOW UP</span></div>
        </div>

      </section>

      <section className="hatch-section" id="how-it-works"><div className="section-heading"><p className="eyebrow"><span className="eyebrow-line" /> THE EGG IS YOUR SAVE FILE</p><h2>Make a pact.<br /><em>Raise a pal.</em></h2><p className="section-intro">Choose a goal, pick a finish line, and seal it with a handshake. Each day your team contributes, the shell cracks a little further. Miss a day and your egg starts to fade.</p></div><div className="creature-gallery"><div className="creature-gallery-art"><img src={`${process.env.NEXT_PUBLIC_BASE_PATH || ''}/pact-pals-pixel-creatures.png`} alt="Four possible pixel creatures hatching from shared eggs" /></div><div className="creature-gallery-copy"><span className="tiny-label">THE HATCH IS A SURPRISE</span><strong>Same pact.<br />New pet.</strong><p>When the shell finally cracks, a fully formed mystery pal joins your collection. Longer pacts give you better odds of a rare hatch. Keep every creature in your library and start the next quest.</p><span className="creature-legend"><i /> Build your pet library</span></div></div><div className="stage-grid">{hatchStages.map((item, index) => <button className={`stage-card ${stage === index ? 'stage-active' : ''}`} key={item.label} type="button" onClick={() => setStage(index)}><span className="stage-count">0{index + 1}</span><span className="stage-icon">{item.icon}</span><span className="stage-label-text">{item.label}</span><span className="stage-copy">{item.copy}</span><span className="stage-check">{stage > index ? <Check size={13} /> : <Lock size={12} />}</span></button>)}</div></section>

      <section className="launch-section" id="join"><div className="launch-copy"><p className="eyebrow"><span className="eyebrow-line" /> EARLY ACCESS IS OPEN</p><h2>Fitness for gamers.<br /><em>Fun for your kids.</em></h2><p>Join the first Pact Pals players and help shape a healthy, accessible fitness game: co-op fitness for friends, fitness for gamers, and a playful way to gamify fitness for your kids without pressure or exhaustion.</p><form className="waitlist-form" onSubmit={joinWaitlist}><input aria-label="Email address" type="email" required placeholder="your@email.com" value={email} onChange={(event) => setEmail(event.target.value)} /><button className="primary-button" type="submit" disabled={waitlistState === 'loading'}>{waitlistState === 'joined' ? "YOU'RE IN" : waitlistState === 'loading' ? 'JOINING...' : 'JOIN THE WAITLIST'} <ArrowRight size={17} /></button></form><span className="waitlist-note">No spam. Just launch news, beta invites, and hatch-day updates.</span>{waitlistState === 'error' && <span className="form-error">Something went wrong. Try again.</span>}</div><div className="wearable-card"><div className="wearable-top"><span>PACT PALS // COMING SOON</span><Watch size={18} /></div><div className="watch-visual"><div className="watch-face"><span className="watch-label">TODAY&apos;S PACT</span><strong>04</strong><span className="watch-unit">DAYS ALIVE</span><div className="watch-progress"><span /></div><small>JULES + MAX · KEEP GOING</small></div></div><div className="wearable-copy"><strong>THE PACT WATCH</strong><span>Your shared egg, your streak, and your pal&apos;s progress — right on your wrist.</span></div></div></section>
      <section className="pact-callout"><div><p className="eyebrow"><span className="eyebrow-line" /> THE GOLDEN RULE</p><h2>One pact.<br /><em>Everyone shows up.</em></h2></div><div className="callout-copy"><p>Seal it with a handshake, choose your shared goal, and set the finish line. If someone misses a day, the egg starts to fade for the whole team. Keep the streak alive and crack open a surprise you can add to your collection.</p><button className="outline-button" type="button" onClick={() => document.getElementById('join')?.scrollIntoView({ behavior: 'smooth' })}>FIND YOUR PLAYER <ArrowRight size={15} /></button></div></section>
      <footer><span>© 2026 PACT PALS</span><span className="footer-center"><Heart size={13} fill="currentColor" /> BUILT TOGETHER</span><span>INSERT GOOD HABIT HERE</span></footer>
    </main>
  )
}
