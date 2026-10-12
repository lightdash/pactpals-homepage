import { NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { sql } from 'drizzle-orm'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : ''
    if (!/^\S+@\S+\.\S+$/.test(email) || email.length > 254) {
      return NextResponse.json({ error: 'Enter a valid email address.' }, { status: 400 })
    }

    await db.execute(sql`INSERT INTO waitlist_signups (email) VALUES (${email}) ON CONFLICT (email) DO NOTHING`)
    return NextResponse.json({ ok: true })
  } catch {
    return NextResponse.json({ error: 'Unable to join right now.' }, { status: 500 })
  }
}
