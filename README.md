# Ledger - AI Currency Assistant

A full-stack **AI-powered currency converter** built with Python, Flask, an
LLM (OpenAI or Claude), and a hand-crafted HTML/CSS/JS frontend styled like
a banknote/ledger. It converts currencies, explains exchange rates in plain
English, summarizes historical trends, gives travel money tips, offers
general investment perspective, compares multiple currencies, and includes
a full chat assistant with conversation history - all with a light/dark
theme and a responsive, mobile-friendly layout.

> **This README assumes you have never set up a Python project before.**
> It assumes the *only* thing installed on your computer is Visual Studio
> Code. Follow the steps in order and you will have the app running
> locally in about 15-20 minutes.

---

## Table of contents

1. [What you're building](#1-what-youre-building)
2. [Project folder structure](#2-project-folder-structure)
3. [Step 1 - Install Python](#3-step-1--install-python)
4. [Step 2 - Install Git (optional but recommended)](#4-step-2--install-git-optional-but-recommended)
5. [Step 3 - Get the project into VS Code](#5-step-3--get-the-project-into-vs-code)
6. [Step 4 - Create a virtual environment](#6-step-4--create-a-virtual-environment)
7. [Step 5 - Activate the virtual environment](#7-step-5--activate-the-virtual-environment)
8. [Step 6 - Install dependencies](#8-step-6--install-dependencies)
9. [Step 7 - Get your API keys](#9-step-7--get-your-api-keys)
10. [Step 8 - Create your .env file](#10-step-8--create-your-env-file)
11. [Step 9 - Run the application](#11-step-9--run-the-application)
12. [Step 10 - Use the app](#12-step-10--use-the-app)
13. [Common errors & how to fix them](#13-common-errors--how-to-fix-them)
14. [How the project is organized (folder-by-folder)](#14-how-the-project-is-organized-folder-by-folder)
15. [API endpoints reference](#15-api-endpoints-reference)
16. [Deployment guide](#16-deployment-guide)
17. [Future improvements](#17-future-improvements)
18. [License](#18-license)

---

## 1. What you're building

A Flask web server (`app.py`) serves one page (`templates/index.html`).
That page calls small JSON APIs on the same server, which in turn:

- Fetch live/historical exchange rates from a currency API.
- Send prompts to an AI model (OpenAI GPT or Anthropic Claude) to generate
  human-friendly explanations, trend summaries, travel tips, investment
  perspective, currency comparisons, and free-form chat answers.

```
Browser (HTML/CSS/JS)
        │  fetch() calls
        ▼
Flask app (app.py)
        │
        ├── services/currency_service.py -> Currency exchange rate API
        └── services/ai_service.py -> OpenAI API or Claude API
```

---

## 2. Project folder structure

```
currency-ai-assistant/
│
├── app.py # Flask entry point - defines all routes
├── config.py # Loads settings & API keys from .env
├── requirements.txt # List of Python packages this project needs
├── .env.example # Template for your secret keys (copy -> .env)
├── .env # YOUR real secrets (you create this, never commit it)
├── .gitignore # Tells Git which files to ignore (like .env)
├── Procfile # Used by some deployment platforms (Heroku/Render)
├── README.md # This file
│
├── services/ # "Business logic" - talks to external APIs
│   ├── __init__.py
│   ├── currency_service.py # Currency conversion + historical rates
│   └── ai_service.py # All OpenAI/Claude prompt logic
│
├── utils/ # Small reusable helper functions
│   ├── __init__.py
│   └── helpers.py
│
├── templates/ # HTML files Flask renders
│   └── index.html # The single-page frontend
│
└── static/ # CSS, JS, images served as-is
    ├── css/
    │   └── style.css # All styling (light + dark theme)
    ├── js/
    │   └── app.js # All frontend behavior
    └── img/ # (empty - add your own images/icons here)
```

---

## 3. Step 1 - Install Python

The app is written in Python, so your computer needs a Python interpreter
installed. VS Code alone does **not** include Python.

1. Go to **https://www.python.org/downloads/** in your web browser.
2. Click the big **"Download Python 3.x.x"** button (any version 3.10 or
   newer works fine).
3. Run the installer you downloaded.
   - **Windows:** On the very first installer screen, **check the box that
     says "Add python.exe to PATH"** before clicking "Install Now". This
     step is the #1 thing beginners forget, and skipping it causes the
     `'python' is not recognized` error later.
   - **macOS:** Run the `.pkg` installer and click through with the default
     options.
4. Verify the install. Open VS Code, then open its built-in terminal:
   - Menu bar -> **Terminal -> New Terminal** (or press `` Ctrl+` ``).
5. In the terminal that opens at the bottom of VS Code, type:

   ```bash
   python --version
   ```

   or, on macOS/Linux, if that doesn't work, try:

   ```bash
   python3 --version
   ```

   You should see something like:

   ```
   Python 3.12.4
   ```

   If you see a version number, Python is installed correctly. If you get
   an error, see the [Troubleshooting](#13-common-errors--how-to-fix-them)
   section below.

6. **Recommended:** In VS Code, install the official **Python extension**
   (by Microsoft) from the Extensions panel on the left sidebar
   (icon looks like 4 squares). Search "Python" and click **Install**.
   This gives you IntelliSense, debugging, and automatic virtual
   environment detection.

---

## 4. Step 2 - Install Git (optional but recommended)

Git lets you download (clone) this project and track changes. If you
already have the project folder on your computer (e.g. downloaded as a
ZIP), you can **skip this step**.

1. Go to **https://git-scm.com/downloads** and download the installer for
   your operating system.
2. Run the installer, accepting all the default options.
3. Verify it worked - in the VS Code terminal, type:

   ```bash
   git --version
   ```

   You should see something like `git version 2.45.1`.

---

## 5. Step 3 - Get the project into VS Code

**If you already have the `currency-ai-assistant` folder** (for example,
you downloaded/unzipped it, or a teammate sent it to you):

1. Open VS Code.
2. Go to **File -> Open Folder...**
3. Select the `currency-ai-assistant` folder and click **Select Folder**.

**If you're starting from a Git repository:**

1. Open VS Code.
2. Press `` Ctrl+` `` (or `` Cmd+` `` on Mac) to open the terminal.
3. Run:

   ```bash
   git clone <your-repository-url>
   cd currency-ai-assistant
   code .
   ```

   The last command (`code .`) reopens VS Code inside that folder.

Either way, you should end up with the file structure from
[section 2](#2-project-folder-structure) visible in the VS Code Explorer
panel on the left.

---

## 6. Step 4 - Create a virtual environment

A **virtual environment** is an isolated, private copy of Python just for
this project, so the packages you install don't clash with other Python
projects on your computer. Think of it as a clean sandbox.

Open the VS Code terminal (`` Ctrl+` ``) and make sure you're inside the
`currency-ai-assistant` folder (the prompt should show that folder name).
Then run:

**Windows:**
```bash
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

This creates a new folder called `venv/` inside your project. This is
where the isolated Python install and packages will live. You'll see it
appear in the VS Code Explorer sidebar - you can ignore its contents.

> 💡 The `.gitignore` file already tells Git to ignore the `venv/` folder,
> so it won't get uploaded if you push this project to GitHub.

---

## 7. Step 5 - Activate the virtual environment

Creating the virtual environment isn't enough - you must **activate** it
every time you open a new terminal to work on this project.

**Windows (Command Prompt or PowerShell, via VS Code terminal):**
```bash
venv\Scripts\activate
```

If PowerShell blocks the script with an error about "execution policies",
run this once, then try activating again:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

✅ **How to know it worked:** your terminal prompt will now show `(venv)`
at the beginning, like this:

```
(venv) C:\Users\you\currency-ai-assistant>
```
or
```
(venv) you@mac currency-ai-assistant %
```

From now on, every `pip install` and `python` command you run in this
terminal uses the isolated environment, not your system-wide Python.

> ⚠️ You must re-activate the virtual environment every time you close and
> reopen VS Code (or open a brand-new terminal tab). If commands start
> failing with "module not found" errors, the first thing to check is
> whether `(venv)` is showing in your prompt.

In VS Code, you can also select the interpreter permanently: press
`Ctrl+Shift+P` -> type **"Python: Select Interpreter"** -> choose the one
that shows `./venv/...`. VS Code will then auto-activate it in new
terminals.

---

## 8. Step 6 - Install dependencies

With `(venv)` active, install every package this project needs in one
command:

```bash
pip install -r requirements.txt
```

This reads `requirements.txt` and installs:

| Package | What it's for |
|---|---|
| `Flask` | The web server framework |
| `python-dotenv` | Loads your `.env` secrets into the app |
| `requests` | Makes HTTP calls to the currency exchange API |
| `openai` | Official OpenAI Python SDK (for AI explanations) |
| `anthropic` | Official Anthropic (Claude) Python SDK - alternative AI provider |
| `gunicorn` | Production web server, used only when you deploy |

You'll see a lot of text scroll by ending in something like:

```
Successfully installed Flask-3.0.3 anthropic-0.34.2 openai-1.51.2 ...
```

That means it worked.

---

## 9. Step 7 - Get your API keys

This app needs **two** kinds of API keys:

### A) An AI provider key - pick ONE

**Option 1: OpenAI (default)**
1. Go to **https://platform.openai.com/signup** and create an account
   (or log in).
2. Go to **https://platform.openai.com/api-keys**.
3. Click **"Create new secret key"**, give it a name, click **Create**.
4. **Copy the key immediately** - it starts with `sk-` and is only shown
   once.
5. Note: OpenAI requires billing to be set up (a card on file) even for
   small usage - check their pricing page. New accounts often include a
   small free trial credit.

**Option 2: Anthropic Claude (alternative)**
1. Go to **https://console.anthropic.com/** and create an account.
2. Navigate to **Settings -> API Keys**.
3. Click **"Create Key"**, name it, and copy the value (starts with
   `sk-ant-`).
4. If you choose this option, set `AI_PROVIDER=claude` in your `.env` file
   (see next step).

### B) A currency exchange rate API key (optional but recommended)

1. Go to **https://www.exchangerate-api.com/** and click **"Get Free Key"**.
2. Sign up with your email, verify it, and copy your API key from the
   dashboard.
3. The free tier is generous (1,500 requests/month) and perfect for local
   development and small projects.

> 🆓 **Don't want to sign up for anything yet?** You can leave
> `EXCHANGE_RATE_API_KEY` blank in your `.env` file. The app automatically
> falls back to the free, keyless **Frankfurter API**
> (https://www.frankfurter.app/) for live rates and history. This is
> great for a first test run, but the paid key gives you more currencies
> and higher reliability.

---

## 10. Step 8 - Create your .env file

Your API keys must **never** be typed directly into the code - they go in
a special file called `.env` that stays private on your machine.

1. In the VS Code Explorer, find the file **`.env.example`**.
2. Duplicate it and rename the copy to exactly **`.env`** (no ".example").
   - Easiest way: in the VS Code terminal, run:
     - Windows: `copy .env.example .env`
     - macOS/Linux: `cp .env.example .env`
3. Open the new `.env` file and fill in your real values:

   ```dotenv
   FLASK_SECRET_KEY=any-random-string-you-like
   FLASK_DEBUG=True

   AI_PROVIDER=openai

   OPENAI_API_KEY=sk-your-real-key-here
   OPENAI_MODEL=gpt-4o-mini

   ANTHROPIC_API_KEY=
   ANTHROPIC_MODEL=claude-sonnet-5

   EXCHANGE_RATE_API_KEY=your-real-key-here-or-leave-blank
   ```

4. Save the file (`Ctrl+S` / `Cmd+S`).

> 🔒 **Security note:** `.env` is listed in `.gitignore`, so if you ever
> push this project to GitHub, your secrets stay on your computer and are
> never uploaded. Never remove `.env` from `.gitignore`, and never paste
> your real keys into a chat, issue, or screenshot you plan to share.

---

## 11. Step 9 - Run the application

With your virtual environment active (`(venv)` visible in the prompt) and
your `.env` file filled in, start the Flask server:

```bash
python app.py
```

(On macOS/Linux, use `python3 app.py` if `python` isn't recognized.)

You should see terminal output similar to this:

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.1.23:8000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

That `Running on http://127.0.0.1:8000` line is the important one.

---

## 12. Step 10 - Use the app

1. Hold `Ctrl` (or `Cmd` on Mac) and click the
   `http://127.0.0.1:8000` link in the terminal - or just open your web
   browser and manually go to **http://127.0.0.1:8000**.
2. You should see the "Ledger - AI Currency Assistant" interface load.
3. Try it out:
   - Enter an amount, pick two currencies, click **Convert**.
   - Click **Summarize trend with AI**, **Get travel tips**, **Get
     investment insight**.
   - Select a few chips in the "Compare currencies" section and click
     **Compare selected**.
   - Type a question in the chat box at the bottom.
   - Click the **Dark mode** toggle in the top-right corner.
4. To stop the server, click back into the VS Code terminal and press
   `Ctrl+C`.

---

## 13. Common errors & how to fix them

| Error message | What it means | How to fix it |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python isn't on your system PATH. | Reinstall Python and check **"Add python.exe to PATH"** during setup (Windows), or use `python3` instead of `python` (macOS/Linux). |
| `ModuleNotFoundError: No module named 'flask'` | Dependencies aren't installed, or your virtual environment isn't active. | Make sure `(venv)` shows in your terminal prompt, then re-run `pip install -r requirements.txt`. |
| `pip: command not found` | Same root cause as above - Python/pip isn't installed or on PATH. | Reinstall Python (see Step 1); pip is bundled with modern Python installers. |
| Terminal shows no `(venv)` prefix after activating | The activation command didn't run, or you're in the wrong folder. | Make sure you're inside the `currency-ai-assistant` folder, then re-run the activation command from [Step 5](#7-step-5--activate-the-virtual-environment). |
| PowerShell: `venv\Scripts\activate` **is not digitally signed / cannot be loaded** | Windows PowerShell's execution policy blocks scripts by default. | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then try again. |
| `AIServiceError: OPENAI_API_KEY is missing` (shown in the browser) | Your `.env` file wasn't created, is misnamed, or the key field is empty. | Confirm the file is named exactly `.env` (not `.env.example` or `.env.txt`), sits in the project root, and has your real key pasted in. Restart the server after editing `.env`. |
| `AIServiceError: AI provider request failed: Error code: 401` | Your API key is invalid, expired, or has no billing set up. | Double-check you copied the whole key with no extra spaces, and that your OpenAI/Anthropic account has billing configured. |
| Conversion works but "explanation unavailable" / AI sections error out | The currency conversion succeeded but the AI call failed (bad key, no internet, rate limit). | Check the terminal output for the specific error; verify your API key and internet connection. |
| `CurrencyServiceError: Could not fetch...` | The currency API is unreachable, or your `EXCHANGE_RATE_API_KEY` is invalid. | Leave `EXCHANGE_RATE_API_KEY` blank to use the free Frankfurter fallback, or verify your key at exchangerate-api.com. |
| Browser shows "This site can't be reached" at 127.0.0.1:8000 | The Flask server isn't running, or it crashed. | Check the VS Code terminal for error text; make sure `python app.py` is still running and didn't exit. |
| Port `8000` already in use | Another program (or a previous run of this app) is using port 8000. | Stop the other process, or change the port in `app.py`'s last line, e.g. `app.run(port=5001)`, then visit `http://127.0.0.1:5001`. On macOS, AirPlay Receiver sometimes uses 8000 - disable it in System Settings -> General -> AirDrop & Handoff, or just change the port. |
| Changes to `style.css` / `app.js` don't show up in the browser | Your browser cached the old file. | Hard-refresh with `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac). |
| `UnicodeDecodeError` or garbled terminal symbols on Windows | Rare console encoding issue. | Run `chcp 65001` in the terminal before starting the app, or use the VS Code integrated terminal instead of an external one. |

If you hit an error not listed here, copy the **exact** error text from
the terminal and search for it - the specific wording almost always
points straight to the fix.

---

## 14. How the project is organized (folder-by-folder)

- **`app.py`** - The Flask application. Defines every URL route
  (`/`, `/api/convert`, `/api/chat`, etc.), validates incoming requests,
  and calls into the `services/` layer to do the real work. Keep this
  file focused on "routing" - not business logic.

- **`config.py`** - Reads all environment variables (from `.env`) into one
  `Config` class so the rest of the app never touches `os.environ`
  directly. Change default models, timeouts, or URLs here.

- **`services/currency_service.py`** - Talks to the currency exchange
  rate APIs (ExchangeRate-API and/or Frankfurter). Includes a small
  in-memory cache so repeated requests for the same pair don't hit the
  external API every time.

- **`services/ai_service.py`** - Talks to OpenAI or Claude. Contains all
  the prompt templates (`explain_exchange_rate`, `summarize_trend`,
  `travel_recommendation`, `investment_suggestion`, `compare_currencies`,
  `chat_reply`). If you want to tweak the AI's tone or add a new AI
  feature, this is the file to edit.

- **`utils/helpers.py`** - Tiny shared utilities, like the standard JSON
  success/error response format and basic input validation.

- **`templates/index.html`** - The one and only HTML page. Uses Flask's
  Jinja templating just to link the CSS/JS files (`url_for`) - everything
  else is static markup that JavaScript fills in dynamically.

- **`static/css/style.css`** - All visual styling, including CSS custom
  properties (`:root` and `[data-theme="dark"]`) that power the light and
  dark themes, plus responsive breakpoints for mobile.

- **`static/js/app.js`** - All frontend behavior: fetching data from the
  Flask API, rendering the trend chart (hand-drawn inline SVG, no chart
  library needed), the typing animation for AI text, the chat widget with
  `localStorage`-backed history, and the dark mode toggle.

- **`requirements.txt`** - Exact list of Python packages + versions this
  project depends on. `pip install -r requirements.txt` reads this file.

- **`.env` / `.env.example`** - Your secret configuration. `.env.example`
  is committed to version control as a template; `.env` (your real copy)
  never is.

---

## 15. API endpoints reference

All endpoints return JSON in the shape `{ "success": true, "data": {...} }`
or `{ "success": false, "error": "message" }`.

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Renders the frontend page |
| GET | `/api/currencies` | List of supported currency codes/names |
| POST | `/api/convert` | Convert an amount + get an AI explanation |
| POST | `/api/historical` | Get a historical rate series (for the chart) |
| POST | `/api/trend` | AI-generated summary of the historical trend |
| POST | `/api/travel-tips` | AI travel money recommendations |
| POST | `/api/investment-tips` | AI general investment-education perspective |
| POST | `/api/compare` | Compare multiple currencies against USD |
| POST | `/api/chat` | Free-form conversational endpoint |

Example request body for `/api/convert`:
```json
{ "base": "USD", "target": "EUR", "amount": 100, "include_explanation": true }
```

---

## 16. Deployment guide

The app is a standard Flask app, so it works on most Python-friendly
hosts. Below are two common, beginner-friendly options.

### Option A: Render.com (recommended for beginners, free tier available)

1. Push this project to a GitHub repository (create one at github.com,
   then in your project folder run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
   - remember `.env` is git-ignored, so your secrets stay local).
2. Go to **https://render.com**, sign up, and click **New -> Web Service**.
3. Connect your GitHub repo.
4. Configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
5. Under **Environment Variables**, add every key from your `.env` file
   (`OPENAI_API_KEY`, `AI_PROVIDER`, `EXCHANGE_RATE_API_KEY`, etc.) - this
   is the cloud equivalent of your local `.env` file.
6. Click **Create Web Service**. Render will build and deploy; you'll get
   a public URL like `https://your-app.onrender.com`.

### Option B: Heroku

1. Install the Heroku CLI and run `heroku login`.
2. In your project folder:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```
3. Set your environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=sk-...
   heroku config:set AI_PROVIDER=openai
   heroku config:set EXCHANGE_RATE_API_KEY=...
   ```
4. Heroku automatically detects the `Procfile` (`web: gunicorn app:app`)
   included in this project and starts the app correctly.

### General deployment notes

- Always set `FLASK_DEBUG=False` in production environment variables -
  debug mode should never be enabled on a public server.
- Never commit `.env` - always configure secrets through your host's
  dashboard/CLI (as shown above).
- The free/hobby tiers of most hosts "sleep" after inactivity, so the
  first request after idling may take a few seconds to wake up - that's
  expected behavior, not a bug.

---

## 17. Future improvements

Ideas if you want to keep extending this project:

- **Persist chat history server-side** (e.g. SQLite or Postgres) instead
  of `localStorage`, so history survives across devices.
- **Rate charts with more ranges** (7d / 30d / 90d / 1y toggle).
- **Push notifications / email alerts** when a currency crosses a target
  rate.
- **User accounts** so people can save favorite currency pairs.
- **Streaming AI responses** (token-by-token from the API) instead of the
  simulated typing animation, for a snappier feel on longer answers.
- **Automated tests** for `services/currency_service.py` and
  `services/ai_service.py` using `pytest` and mocked HTTP responses.
- **Multi-language support** for the AI explanations and UI text.
- **Currency news feed integration** to ground AI trend commentary in
  real, cited headlines.

---

## 18. License

This project is provided as-is for educational purposes. Add your own
license (MIT is a common, permissive choice) if you plan to share or
publish it.
