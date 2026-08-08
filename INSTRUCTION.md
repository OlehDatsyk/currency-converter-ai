# INSTRUCTION.md — Complete Beginner's Setup & Usage Guide

Welcome! This guide assumes you have **never** used Python, Git, Visual
Studio Code, a terminal, virtual environments, or any API before in your
life. Every step is spelled out. Follow them in order from top to bottom,
and by the end you'll have "Ledger — AI Currency Assistant" running on
your own computer.

Budget about **20–30 minutes** for a first-time setup.

---

## Table of contents

1. [What this app does](#1-what-this-app-does)
2. [Install Python](#2-install-python)
3. [Install Git](#3-install-git)
4. [Install Visual Studio Code](#4-install-visual-studio-code)
5. [Install the recommended VS Code extensions](#5-install-the-recommended-vs-code-extensions)
6. [Open the project in VS Code](#6-open-the-project-in-vs-code)
7. [Create a virtual environment](#7-create-a-virtual-environment)
8. [Activate the virtual environment](#8-activate-the-virtual-environment)
9. [Install the project's dependencies](#9-install-the-projects-dependencies)
10. [Create your `.env` file](#10-create-your-env-file)
11. [Get your API keys](#11-get-your-api-keys)
12. [Run the application](#12-run-the-application)
13. [Test that everything works](#13-test-that-everything-works)
14. [Using every feature of the app](#14-using-every-feature-of-the-app)
15. [Troubleshooting](#15-troubleshooting)
16. [FAQ](#16-faq)
17. [Common mistakes beginners make](#17-common-mistakes-beginners-make)
18. [Security recommendations](#18-security-recommendations)
19. [Next learning steps](#19-next-learning-steps)

---

## 1. What this app does

"Ledger" is a small website that runs on your own computer. It:

- Converts an amount from one currency to another (e.g. 100 USD → EUR).
- Uses an AI model (OpenAI or Claude) to explain the exchange rate in
  plain English.
- Shows a 30-day historical trend chart.
- Gives AI-generated travel tips and general investment-education notes.
- Lets you compare several currencies at once.
- Includes a simple AI chat box you can ask questions in.

It is made of two halves that work together:

- A **backend** (written in Python, using a framework called Flask) that
  talks to external services and serves data.
- A **frontend** (HTML, CSS, and JavaScript) that you view in your web
  browser — this is what you'll actually click around in.

You don't need to understand Python or JavaScript to use the app. You do
need to follow the setup steps below once.

---

## 2. Install Python

Python is the programming language the backend of this app is written
in. Your computer almost certainly does not have it pre-installed in a
usable form, so install it first.

1. Open your web browser and go to **https://www.python.org/downloads/**.
2. Click the large **"Download Python 3.x.x"** button (any version 3.10
   or newer is fine — the button will already suggest the latest one).
3. Once downloaded, open the installer file:
   - **On Windows:** On the very first screen of the installer, you'll
     see a checkbox at the bottom that says **"Add python.exe to PATH"**.
     **Check this box** before clicking "Install Now." This single step
     prevents the single most common beginner error later on.
   - **On macOS:** Open the downloaded `.pkg` file and click "Continue"
     through each screen, accepting the defaults.
4. Once the installer finishes, you can close it.

You'll verify this install worked in [Section 6](#6-open-the-project-in-vs-code)
once VS Code is installed, since you need a terminal to check it.

---

## 3. Install Git

Git is a tool for downloading and tracking changes to code projects. If
you already have this project's folder on your computer (for example,
you downloaded it as a `.zip` and extracted it), Git is **optional** —
you can skip to [Section 4](#4-install-visual-studio-code). If you plan
to download the project from a GitHub link, install Git first:

1. Go to **https://git-scm.com/downloads**.
2. Download the installer for your operating system.
3. Run it, clicking "Next"/"Continue" through every screen and accepting
   the default options — the defaults are safe for beginners.

---

## 4. Install Visual Studio Code

Visual Studio Code (VS Code) is a free code editor. It's where you'll
open the project folder, run terminal commands, and (optionally) edit
files.

1. Go to **https://code.visualstudio.com/**.
2. Click the big **Download** button for your operating system.
3. Run the installer, accepting the default options.
4. Launch VS Code once installation finishes, just to confirm it opens.

---

## 5. Install the recommended VS Code extensions

Extensions add extra functionality to VS Code. You only need one for
this project:

1. In VS Code, look at the far-left vertical strip of icons — this is
   the **Activity Bar**. Click the icon that looks like four small
   squares (one detached) — this opens the **Extensions** panel.
2. In the search box at the top of that panel, type **Python**.
3. Find the extension simply called **"Python"**, published by
   **Microsoft** (it will usually be the first result and have millions
   of installs). Click **Install**.

This gives you things like automatic detection of your virtual
environment, code completion, and error highlighting — all of which
make the rest of this guide smoother.

---

## 6. Open the project in VS Code

**If you already have the project folder** (e.g. you unzipped it
somewhere on your computer):

1. In VS Code, go to the top menu bar → **File → Open Folder…**
2. Browse to and select the project folder (the one containing `app.py`,
   `README.md`, etc.) and click **Select Folder** (or **Open** on Mac).

**If you're cloning it from a Git repository instead:**

1. In VS Code, open the terminal: menu bar → **Terminal → New Terminal**
   (or the keyboard shortcut `` Ctrl+` `` on Windows/Linux, `` Cmd+` ``
   on Mac).
2. In the terminal panel that appears at the bottom, type:
   ```bash
   git clone <the-repository-url-you-were-given>
   cd currency-converter-ai
   code .
   ```
3. Press Enter after each line. The last command reopens VS Code inside
   the newly downloaded folder.

**Now verify Python is installed correctly.** Open a terminal in VS Code
(`` Ctrl+` `` / `` Cmd+` ``) and type:

```bash
python --version
```

If that gives an error on macOS/Linux, try:

```bash
python3 --version
```

You should see output like `Python 3.12.4`. If you see a version number,
you're ready to continue. If you see an error instead, jump to
[Troubleshooting](#15-troubleshooting).

---

## 7. Create a virtual environment

A **virtual environment** is a private, isolated copy of Python just for
this one project. It keeps this project's installed packages completely
separate from anything else on your computer, so nothing conflicts.

With the VS Code terminal open and the project folder as your current
location (the terminal prompt should show the project folder's name),
run:

**Windows:**
```bash
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

This creates a new folder named `venv` inside your project. You'll see
it appear in the file list on the left side of VS Code. You never need
to open or edit anything inside it.

> The project's `.gitignore` file already excludes `venv/`, so if you
> ever upload this project to GitHub, this folder won't be included —
> which is correct and expected.

---

## 8. Activate the virtual environment

Creating the virtual environment isn't enough on its own — you have to
**turn it on** ("activate" it) every time you open a fresh terminal to
work on this project.

**Windows:**
```bash
venv\Scripts\activate
```

If you see an error mentioning "execution policies," run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try the activation command again.

**macOS / Linux:**
```bash
source venv/bin/activate
```

**How do you know it worked?** Your terminal prompt will now start with
`(venv)`, like:

```
(venv) C:\Users\you\currency-converter-ai>
```

or

```
(venv) you@mac currency-converter-ai %
```

If you don't see `(venv)`, repeat the command for your operating system
above before continuing.

> You must repeat this activation step every time you close and reopen
> VS Code, or open a brand-new terminal tab. If you ever see "module not
> found" errors later, the very first thing to check is whether
> `(venv)` is showing.

---

## 9. Install the project's dependencies

With `(venv)` visible in your terminal prompt, run:

```bash
pip install -r requirements.txt
```

This reads the `requirements.txt` file in the project and downloads
everything the app needs:

| Package | What it does |
|---|---|
| `Flask` | Runs the web server |
| `python-dotenv` | Loads your secret settings from the `.env` file |
| `requests` | Lets the app fetch live currency data |
| `openai` | Talks to OpenAI's AI models |
| `anthropic` | Talks to Anthropic's Claude AI models |
| `gunicorn` | A production-grade server, used only if you deploy online |

You'll see text scroll by, ending with something like:

```
Successfully installed Flask-3.0.3 anthropic-0.34.2 openai-1.51.2 ...
```

That means it worked.

---

## 10. Create your `.env` file

Your secret API keys must never be typed directly into the code files.
Instead, they live in a special file called `.env` that stays private
on your computer and is never shared or uploaded anywhere.

1. In the VS Code file list on the left, find the file **`.env.example`**.
2. Make a copy of it and rename the copy to exactly **`.env`** — no
   `.example` at the end. The easiest way is through the terminal:

   **Windows:**
   ```bash
   copy .env.example .env
   ```

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

3. Click on the new `.env` file in VS Code's file list to open it. You'll
   fill in the real values in the next section.

---

## 11. Get your API keys

The app needs an **AI provider key** to generate explanations, tips, and
chat replies. A currency-rate API key is optional — the app has a free
fallback built in.

### A) Choose ONE AI provider

**Option 1 — OpenAI**
1. Go to **https://platform.openai.com/signup** and create an account
   (or log in if you already have one).
2. Go to **https://platform.openai.com/api-keys**.
3. Click **"Create new secret key,"** give it any name, and click
   **Create**.
4. **Copy the key immediately** — it starts with `sk-` and is only shown
   to you once. Paste it somewhere safe temporarily (like a plain text
   note) if you're not pasting it straight into `.env`.
5. Note: OpenAI generally requires a payment method on file, even for
   very small amounts of usage. New accounts sometimes include free
   trial credit.

**Option 2 — Anthropic (Claude)**
1. Go to **https://console.anthropic.com/** and create an account.
2. Go to **Settings → API Keys**.
3. Click **"Create Key,"** name it, and copy the value (starts with
   `sk-ant-`).
4. If you choose this option, you'll set `AI_PROVIDER=claude` in your
   `.env` file (shown below).

### B) Currency exchange rate key (optional)

1. Go to **https://www.exchangerate-api.com/** and click **"Get Free
   Key."**
2. Sign up with your email and verify it, then copy your key from your
   dashboard.
3. The free tier allows 1,500 requests/month, plenty for personal use
   and testing.

> **Don't want to sign up for a second service right now?** Leave
> `EXCHANGE_RATE_API_KEY` blank in your `.env` file. The app
> automatically uses a free, no-key-required service (Frankfurter) as a
> fallback for live and historical rates.

### C) Fill in your `.env` file

Open the `.env` file you created in Section 10 and fill it in like this
(replacing the placeholder values with your real ones):

```dotenv
FLASK_SECRET_KEY=any-random-string-you-make-up
FLASK_DEBUG=True

AI_PROVIDER=openai

OPENAI_API_KEY=sk-your-real-key-here
OPENAI_MODEL=gpt-4o-mini

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-5

EXCHANGE_RATE_API_KEY=your-real-key-here-or-leave-blank
```

If you chose Claude instead of OpenAI, set `AI_PROVIDER=claude` and fill
in `ANTHROPIC_API_KEY` instead (you can leave `OPENAI_API_KEY` blank).

Save the file with `Ctrl+S` (Windows/Linux) or `Cmd+S` (Mac).

---

## 12. Run the application

Make sure `(venv)` is still showing in your terminal prompt (if you
closed VS Code and reopened it, redo [Section 8](#8-activate-the-virtual-environment)
first). Then run:

```bash
python app.py
```

On macOS/Linux, if that's not recognized, try `python3 app.py` instead.

You should see output similar to:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:1000
Press CTRL+C to quit
```

The line `Running on http://127.0.0.1:1000` means the app is live on
your computer.

---

## 13. Test that everything works

1. Hold `Ctrl` (or `Cmd` on Mac) and click the `http://127.0.0.1:1000`
   link in the terminal, or open your browser and type
   `http://127.0.0.1:1000` into the address bar yourself.
2. You should see the "Ledger — AI Currency Assistant" page load, with a
   status pill near the top that says **"Connected"** once the currency
   list finishes loading.
3. Type an amount (e.g. `100`), leave the currencies as their defaults,
   and click **Convert**. You should see a converted amount appear,
   followed a moment later by an AI-written explanation typing itself
   out underneath.

If all of that happens, your setup is complete and working correctly.

---

## 14. Using every feature of the app

- **Convert currency:** Enter an amount, choose a "From" and "To"
  currency from the dropdowns, and click **Convert**. Use the swap
  button (⇆) between the two dropdowns to flip them instantly.
- **AI explanation:** Appears automatically under your conversion
  result, explaining the rate in plain English.
- **Historical trend chart:** After converting, a 30-day line chart
  appears automatically showing how that currency pair has moved.
- **Summarize trend with AI:** Click this button (enabled after your
  first conversion) to get a short AI-written summary of the chart.
- **Get travel tips:** AI-generated, practical money tips for someone
  travelling between your two selected currencies.
- **Get investment insight:** A general, educational (not personalized)
  perspective on the currency pair's movement. This is explicitly not
  financial advice, and the AI is prompted to say so.
- **Compare currencies:** Click currency "chips" to select or deselect
  them, then click **Compare selected** (minimum 2) to see their rates
  against USD plus an AI-written comparison.
- **Chat:** Type any currency-related question into the chat box at the
  bottom and press **Send**. Your conversation is saved in your browser
  so it's still there if you reload the page — click **Clear
  conversation** to erase it.
- **Dark mode:** Click the toggle in the top-right corner of the page.
  Your choice is remembered for next time.

To stop the app, click back into the VS Code terminal running it and
press `Ctrl+C`.

---

## 15. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python isn't on your system PATH. | Reinstall Python and make sure to check "Add python.exe to PATH" during setup (Windows). On macOS/Linux, use `python3` instead of `python`. |
| `ModuleNotFoundError: No module named 'flask'` | Your virtual environment isn't active, or dependencies aren't installed. | Confirm `(venv)` is showing in your terminal, then re-run `pip install -r requirements.txt`. |
| `pip: command not found` | Python/pip isn't installed correctly. | Reinstall Python — pip comes bundled with modern versions. |
| No `(venv)` prefix shows after activating | You're in the wrong folder, or the command didn't run. | Make sure your terminal is inside the project folder, then repeat [Section 8](#8-activate-the-virtual-environment). |
| PowerShell says the activate script "cannot be loaded" / "is not digitally signed" | Windows blocks scripts by default. | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then try activating again. |
| Browser shows `AIServiceError: OPENAI_API_KEY is missing` | Your `.env` file wasn't created, is misnamed, or the key field is empty. | Make sure the file is named exactly `.env` (not `.env.example`), lives in the project's root folder, and has a real key pasted in. Restart the app after editing. |
| `AIServiceError: AI provider request failed: Error code: 401` | Your API key is invalid, mistyped, or has no billing configured. | Re-copy the key carefully (no extra spaces), and check your account's billing status on the provider's website. |
| Conversion works, but the AI explanation says "unavailable" | The conversion succeeded, but the AI call failed separately. | Check the terminal for the specific error text; double-check your API key and internet connection. |
| `CurrencyServiceError: Could not fetch...` | The currency API is unreachable or your key is invalid. | Leave `EXCHANGE_RATE_API_KEY` blank to use the free fallback, or verify your key on exchangerate-api.com. |
| Browser says "This site can't be reached" at `127.0.0.1:1000` | The server isn't running or has crashed. | Check the VS Code terminal for error output; make sure `python app.py` is still running. |
| Port 1000 already in use | Another program is already using that port. | Close the other program, or open `app.py`, change the last line's `port=1000` to `port=5001`, save, and restart — then visit `http://127.0.0.1:5001` instead. On Mac, this is sometimes caused by AirPlay Receiver — you can disable it in System Settings → General → AirDrop & Handoff. |
| CSS/JS changes don't show up in the browser | Your browser cached the old files. | Force a refresh with `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac). |

If you hit an error not listed here, copy the exact error text from the
terminal and search for it online — the specific wording almost always
leads straight to the fix.

---

## 16. FAQ

**Do I need to know how to code to use this app?**
No. Setup requires typing a handful of copy-pasted commands, but you
don't need to write or understand any code to use the app itself once
it's running.

**Is this safe to leave running while I'm not using it?**
Yes, on your own computer for local development. Just know that while
it's running, it's technically available to other devices on your same
local network too (not just you) unless you change that behavior — see
[Section 18](#18-security-recommendations).

**Do I have to pay for anything?**
The app itself is free. OpenAI generally requires a payment method on
file (though new accounts often get some free trial credit), while the
optional currency-rate API and the Frankfurter fallback are both free.
Actual AI usage costs are typically fractions of a cent per request for
light personal use, but you should check current pricing on your chosen
provider's website.

**Can I use both OpenAI and Claude?**
Not at the same time automatically — the app uses whichever one you set
in `AI_PROVIDER` in your `.env` file. You can switch between them at any
time by changing that value and restarting the app.

**What happens to my chat history?**
It's stored in your browser only (not on any server), so it stays on
your device and is private to you. Clearing your browser data or
clicking "Clear conversation" in the app will erase it.

**Can other people on the internet access my app?**
Not unless you deploy it to a hosting service (see the "Deployment
guide" section in `README.md`) or configure your router/firewall to
expose it. Running it locally via `python app.py` keeps it on your own
machine (and, by default, reachable by other devices on your local
network — see Section 18).

---

## 17. Common mistakes beginners make

- **Forgetting to check "Add python.exe to PATH"** during the Windows
  Python installer — causes the `'python' is not recognized` error.
- **Forgetting to activate the virtual environment** before running
  `pip install` or `python app.py` — causes "module not found" errors.
- **Naming the file `.env.txt` instead of `.env`** — some operating
  systems hide file extensions by default, so double-check the exact
  filename in VS Code's file list, not just in Windows File Explorer or
  macOS Finder.
- **Pasting an API key with extra spaces or line breaks** — always paste
  directly into the `.env` file and check there's nothing before or
  after the key on that line.
- **Editing `.env.example` instead of `.env`** — remember: `.env.example`
  is just a template; your real secrets go in the separate `.env` file
  you created.
- **Closing the terminal and expecting the app to keep running** — the
  app stops the moment its terminal window/tab is closed or you press
  `Ctrl+C`.
- **Committing the `.env` file to Git** — this would leak your private
  API keys publicly. The provided `.gitignore` already prevents this by
  default; don't remove `.env` from it.

---

## 18. Security recommendations

- **Never share your `.env` file, or paste its contents into a chat,
  issue, screenshot, or public forum.** Anyone with your API key can
  spend money on your account.
- **Keep `.env` out of version control.** The project's `.gitignore`
  already excludes it — don't remove that line.
- **Set `FLASK_DEBUG=False`** before ever deploying this app anywhere
  public-facing (a real domain, a hosting platform, etc.). Debug mode is
  meant for local development only — it can expose sensitive
  information and, in some configurations, allow arbitrary code
  execution if left on in production.
- **Set a strong, random `FLASK_SECRET_KEY`** rather than leaving the
  placeholder value, especially before any public deployment.
- **Rotate (regenerate) your API keys** if you ever suspect they were
  exposed — both OpenAI's and Anthropic's dashboards let you revoke and
  create new keys in a couple of clicks.
- **Be mindful of API usage costs** if you deploy this publicly without
  any request limits — anyone who finds the URL could trigger AI calls
  on your account's dime. See `PROJECT_REVIEW.md` for a specific
  recommendation on adding rate limiting before any public deployment.

---

## 19. Next learning steps

If this project sparked your interest in web development, here are
natural next things to explore, roughly in order of difficulty:

1. **Read `app.py` top to bottom.** Each route is short, commented, and
   fairly self-explanatory — this is a good way to see how a web
   backend responds to requests.
2. **Try changing something small and safe**, like the AI's personality
   in `services/ai_service.py` (`SYSTEM_PERSONA`), and restart the app
   to see the effect.
3. **Learn the basics of HTML/CSS/JavaScript** by exploring
   `templates/index.html`, `static/css/style.css`, and
   `static/js/app.js` — this project is a realistic, complete example of
   all three working together without any complex build tools.
4. **Learn Git properly** (not just clone) — commits, branches, and
   pushing changes — so you can track your own edits to this project or
   contribute changes back.
5. **Learn basic testing** with `pytest` — try writing a test for the
   `CurrencyService.convert()` method as a first exercise.
6. **Try deploying it** using the "Deployment guide" section of
   `README.md` so it's reachable from a real URL, not just your own
   computer.

Good luck, and enjoy exploring the project!
