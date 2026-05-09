---
title: Skilled Reviewer
emoji: 🚀
colorFrom: green
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Skilled UX Reviewer 🚀
### Professional 4-Skill Diagnostic System for High-Conversion Websites

Skilled Reviewer is a modular diagnostic platform designed to analyze and transform website copy, structure, visual design, and overall strategy. Powered by the **GPT-OSS 120B** model on **Groq's LPU™** infrastructure, it delivers professional-grade audits with surgical precision and sub-second reasoning.

---

## 🌐 Live Deployment
**Experience the system live in your browser:**  
👉 **[Skilled UX Reviewer - Live Demo on Hugging Face](https://huggingface.co/spaces/Magghy/ux-copy-reviewer)**

---

## 🛠 The 4-Skill Expert System
The architecture is based on four independent but interconnected "experts" that evaluate your project from multiple strategic dimensions:

| Expert Skill | Core Focus | Key Deliverables |
| :--- | :--- | :--- |
| **1 — Copy & Tone** | Messaging & Empathy | Tone-of-voice alignment, friction point identification, and tactical rewrites. |
| **2 — Structure & IA** | Information Architecture | User journey mapping, hierarchy evaluation, and strategic CTA placement. |
| **3 — Aesthetic Audit** | Visual Trust & UI | Semantic assessment of branding, typography coherence, and emotional register. |
| **4 — Strategic Recap** | Executive Summary | Full synthesis of all findings with a prioritized redesign roadmap. |

---

## 🧠 The Context Layer System
This is the core innovation of the project. Declare your sector (e.g., `context: therapy`) and the system recalibrates its entire knowledge base to your user's specific emotional state.

> **Why it matters:** A user seeking a therapist is in a state of vulnerability and urgency. They are not a SaaS user evaluating a project management tool. The system understands these nuances and adapts every rewrite and suggestion accordingly.

### Real-World Example (Therapy Context)
**Original Hero Copy (Common pattern):**
*"Hi there, my name is [Name] and I am a licensed therapist with over 12 years in private practice. I provide a safe space where clients can begin to heal."*

**AI-Driven Rewrites based on User Intent:**
*   **For the ambivalent user:** *"Sometimes you can't name what's wrong. You just know something isn't right. That's a good enough reason to talk."*
*   **For the user seeking confirmation:** *"I work with adults who are tired of carrying things alone. If that sounds like you, I'd like to hear your story."*

---

## 🚀 How to Use

### A. Web Application (Recommended)
1. Open the [Live Demo](https://huggingface.co/spaces/Magghy/ux-copy-reviewer).
2. Enter the **URL** of the website (or paste text).
3. Select an **Expert Skill** from the sidebar.
4. *(Optional)* Add your **Context Layer** (e.g., "Counselor", "Coaching", "Freelance").
5. Click **Analyze** for an instant professional audit.

### B. Inside Claude (Manual Mode)
1. Open any of the `.md` skill files in this repo.
2. Paste your website copy.
3. Use the command `context: [your_sector]`.

### C. Local CLI / API Setup
```bash
# Install dependencies
pip install fastapi uvicorn groq python-dotenv requests beautifulsoup4

# Setup environment
echo "GROQ_API_KEY=your_key_here" > .env

# Run server
python app.py
```

---

## 💻 Technical Architecture & Resilience
- **Backend**: FastAPI (Python) with high-performance scraping using BeautifulSoup4.
- **Frontend**: Custom Vanilla HTML/CSS/JS with a "Neon/Cyberpunk" Dark UI.
- **Resilience Layer**: Implemented **Semantic Visual Analysis** fallback. If visual input is unavailable, the AI reconstructs the visual intent from DOM structure and metadata, ensuring audits never fail.
- **Routing**: Universal Root Strategy for seamless deployment on Hugging Face Spaces.

---

## 📂 Project Structure
```text
ux-reviewer/
├── skill.md       # Skill 1 — Copy & Tone Expert
├── skill-2.md     # Skill 2 — Structure & IA Expert
├── skill-3.md     # Skill 3 — Aesthetic & UI Expert
├── skill-4.md     # Skill 4 — Strategic Roadmap Expert
├── app.py         # FastAPI Gateway (Groq Backend)
├── index.html     # Unified Browser Interface
├── .env.example   # API Template
└── README.md      # Master Documentation
```

---
