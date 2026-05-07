# UX Reviewer — 4-Skill Diagnostic System for Professional Service Websites

A modular diagnostic tool to analyze and improve website copy, structure,
visual design, and strategy for professional service websites.
Built with a context layer system: declare your sector, get analysis
calibrated to your specific user's emotional state.

Currently available context: **therapy practice** (psychologists,
psychotherapists). Coaching and counseling layers coming next.

---

## The 4-Skill System

| Skill | File | What it analyzes |
|---|---|---|
| 1 — Copy & Tone | `skill.md` | Messaging, empathy, friction, rewrites |
| 2 — Structure & IA | `skill-2.md` | Page organization, user journey, CTA placement |
| 3 — Aesthetics & UI | `skill-3.md` | Visual trust, branding, typography, emotional register |
| 4 — Strategic Audit | `skill-4.md` | Full synthesis, prioritized issues, redesign roadmap |

Skills run independently or in sequence.
Skills 1–3 feed into Skill 4 for the full audit.

---

## How to use it

### In Claude (no setup required)
1. Open the skill file you want to use
2. Paste the website URL or copy
3. Add one line of context: `context: therapy`
4. Run the analysis

### Web app (browser UI + web scraping)
Runs with FastAPI + BeautifulSoup. Drop a URL, pick a skill, get the output.

```bash
pip install fastapi uvicorn groq python-dotenv requests beautifulsoup4
```

Add your Groq API key to `.env`:
GROQ_API_KEY=your_key_here

Start the server:
```bash
python app.py
```

Open `index.html` in your browser.

### CLI (quick terminal analysis)
Reads `skill.md` as system prompt. Uses the Anthropic API.

```bash
pip install anthropic python-dotenv
```

Add your Anthropic API key to `.env`:
ANTHROPIC_API_KEY=your_key_here

Run:
```bash
python review.py "paste your website copy here"
# or
python review.py --file your_copy.txt
```

---

## Project structure
ux-reviewer/ ├── skill.md # Skill 1 — Copy & Tone ├── skill-2.md # Skill 2 — Structure & IA ├── skill-3.md # Skill 3 — Aesthetics & UI ├── skill-4.md # Skill 4 — Strategic Audit ├── app.py # FastAPI web server (Groq backend) ├── review.py # CLI script (Anthropic backend) ├── index.html # Browser UI ├── style.css ├── script.js ├── .env.example # API key template (never commit .env) └── README.md

---

## Context layer

Declare the context at the start of your prompt:
context: therapy

The skill adapts every judgment, rewrite, and recommendation
to the emotional state of your specific user.
Therapy patients are not SaaS users evaluating a free trial.
The system knows the difference.

---

## Before / After

**Original hero copy (recurring pattern across therapy websites):**
> "Hi there, my name is [Name] and I am a licensed therapist with over
> 12 years in private practice. I provide a safe, supportive, and
> compassionate space where clients can explore their experiences
> and begin to heal."

**Rewrite A — for the ambivalent user:**
> "Sometimes you can't name what's wrong. You just know something
> isn't right. That's a good enough reason to talk."

**Rewrite B — for the user who's ready but scared:**
> "Reaching out doesn't mean you've decided anything.
> It means you're curious about what's possible. That's enough to start."

**Rewrite C — for the user seeking confirmation:**
> "I work with adults who are tired of carrying things alone.
> If that sounds like you, I'd like to hear your story."
