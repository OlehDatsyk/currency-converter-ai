# 💱 Exchange Desk - Currency Converter (Web)

A modern, responsive currency converter built with **Flask**, **HTML5**, **CSS3**, and **vanilla JavaScript**. It has a dark/light glassmorphism UI, live exchange rates, a swap button, and full error handling.

This README is written for someone who has **never run a Python or Flask project before** and has only installed Visual Studio Code so far. Follow it top to bottom and you will have the app running locally.

---

## Table of contents

1. [What you need before you start](#1-what-you-need-before-you-start)
2. [Install Python](#2-install-python)
3. [Install Git (optional but recommended)](#3-install-git-optional-but-recommended)
4. [Get the project into VS Code](#4-get-the-project-into-vs-code)
5. [Open the integrated terminal in VS Code](#5-open-the-integrated-terminal-in-vs-code)
6. [Create a virtual environment](#6-create-a-virtual-environment)
7. [Activate the virtual environment](#7-activate-the-virtual-environment)
8. [Install project dependencies](#8-install-project-dependencies)
9. [Set up your .env file and API key](#9-set-up-your-env-file-and-api-key)
10. [Run the Flask application](#10-run-the-flask-application)
11. [Open the app in your browser](#11-open-the-app-in-your-browser)
12. [Project folder structure explained](#12-project-folder-structure-explained)
13. [How the app works (high level)](#13-how-the-app-works-high-level)
14. [Common errors and how to fix them](#14-common-errors-and-how-to-fix-them)
15. [Useful VS Code terminal commands cheat sheet](#15-useful-vs-code-terminal-commands-cheat-sheet)
16. [Next steps / ideas to extend the project](#16-next-steps--ideas-to-extend-the-project)

---

## 1. What you need before you start

- A computer running **Windows**, **macOS**, or **Linux**.
- **Visual Studio Code** installed (you already have this ✅). If not, download it from https://code.visualstudio.com/ and install it with default options.
- An internet connection (the app fetches live exchange rates from the web).

You do **not** need to know Python already - every command below is copy-pasteable.

---

## 2. Install Python

Flask is a Python framework, so you need Python installed on your computer first.

### Check if Python is already installed

Open a terminal (see [section 5](#5-open-the-integrated-terminal-in-vs-code) if you're not sure how) and run:

```bash
python --version
```

or, on macOS/Linux, sometimes:

```bash
python3 --version
```

- If you see something like `Python 3.11.4`, Python is already installed. Make sure the version is **3.9 or higher**, then skip to [section 3](#3-install-git-optional-but-recommended).
- If you see an error like `command not found` or `'python' is not recognized`, follow the install steps below.

### Windows

1. Go to https://www.python.org/downloads/
2. Click the yellow **"Download Python 3.x.x"** button.
3. Run the installer.
4. ⚠️ **Very important:** On the first installer screen, check the box **"Add python.exe to PATH"** at the bottom before clicking "Install Now".
5. Once installation finishes, close and reopen VS Code completely.
6. Verify by running `python --version` in a new terminal.

### macOS

1. Go to https://www.python.org/downloads/ and download the macOS installer.
2. Run the `.pkg` installer and follow the prompts.
3. Close and reopen VS Code.
4. Verify with `python3 --version`.

*(Alternative for macOS users who have Homebrew: `brew install python`)*

### Linux (Debian/Ubuntu example)

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Verify with `python3 --version`.

---

## 3. Install Git (optional but recommended)

Git lets you download (clone) and version-control the project. If you already have the project files on your computer (e.g., unzipped into a folder), you can **skip this step**.

- Windows/macOS: download from https://git-scm.com/downloads and install with default options.
- Linux: `sudo apt install git`

Verify installation:

```bash
git --version
```

---

## 4. Get the project into VS Code

If you downloaded/unzipped this project already, simply:

1. Open VS Code.
2. Go to **File -> Open Folder…**
3. Select the `currency-converter-web` folder.

If you are cloning from a Git repository instead:

```bash
git clone <your-repository-url>
cd currency-converter-web
code .
```

The `code .` command opens the current folder in VS Code.

---

## 5. Open the integrated terminal in VS Code

You will run every command in this guide from VS Code's built-in terminal.

- **Menu:** Terminal -> New Terminal
- **Keyboard shortcut:** `` Ctrl + ` `` (backtick) on Windows/Linux, `` Cmd + ` `` on macOS

Make sure the terminal's current folder is the project root (`currency-converter-web`). You should see a prompt similar to:

```
PS C:\Users\YourName\currency-converter-web>
```

or on macOS/Linux:

```
yourname@machine currency-converter-web %
```

If it's not in the right folder, run `cd path/to/currency-converter-web`.

---

## 6. Create a virtual environment

A **virtual environment** is an isolated Python installation just for this project, so its dependencies don't clash with other projects on your computer. This is standard professional practice.

In the VS Code terminal, from the project root, run:

**Windows:**
```bash
python -m venv venv
```

**macOS/Linux:**
```bash
python3 -m venv venv
```

This creates a new folder called `venv/` inside your project (it's already excluded from Git via `.gitignore`).

---

## 7. Activate the virtual environment

You must **activate** the virtual environment every time you open a new terminal to work on this project.

**Windows (PowerShell)** - the default VS Code terminal on Windows:
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt / cmd.exe):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux (bash/zsh):**
```bash
source venv/bin/activate
```

✅ **You'll know it worked** when you see `(venv)` at the start of your terminal prompt, like this:

```
(venv) PS C:\Users\YourName\currency-converter-web>
```

> ⚠️ If PowerShell shows an error like *"running scripts is disabled on this system"*, see the [Common errors](#14-common-errors-and-how-to-fix-them) section below - there's a one-line fix.

---

## 8. Install project dependencies

With the virtual environment **activated**, install all required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Expected terminal output (abbreviated):

```
Collecting Flask==3.0.3
  Downloading flask-3.0.3-py3-none-any.whl (101 kB)
Collecting requests==2.32.3
  Downloading requests-2.32.3-py3-none-any.whl (64 kB)
Collecting python-dotenv==1.0.1
  Downloading python_dotenv-1.0.1-py3-none-any.whl (19 kB)
...
Successfully installed Flask-3.0.3 requests-2.32.3 python-dotenv-1.0.1 ...
```

If this finishes without red error text, you're ready for the next step.

---

## 9. Set up your .env file and API key

The app reads configuration (like your API key) from a file named `.env`. A template is provided as `.env.example`.

### Create your `.env` file

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### Get a free exchange rate API key (optional but recommended)

The app works **out of the box without any API key** - it automatically falls back to a free, keyless exchange rate provider. However, for higher reliability and request limits, you can get a free key:

1. Go to https://www.exchangerate-api.com/
2. Click **"Get Free Key"**.
3. Sign up with your email and verify your account.
4. Copy the API key shown on your dashboard.
5. Open `.env` in VS Code and paste it in:

```
EXCHANGE_RATE_API_KEY=paste_your_key_here
```

6. Save the file (`Ctrl+S` / `Cmd+S`).

> 🔒 **Never share or commit your `.env` file.** It's already listed in `.gitignore` so Git will ignore it automatically.

---

## 10. Run the Flask application

With your virtual environment still **activated** (you should see `(venv)` in the prompt), run:

```bash
python app.py
```

Expected terminal output:

```
2026-07-08 12:00:01 [INFO] currency-converter: Starting Currency Converter on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

Leave this terminal running - it is your live server. To stop the server at any time, press `Ctrl + C` in the terminal.

---

## 11. Open the app in your browser

Open your web browser and go to:

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

You should see the **Exchange Desk** currency converter UI, with dropdowns already populated and a default conversion (1 USD -> EUR) calculated automatically.

Try it out:
- Change the amount in the "From" box.
- Change either currency dropdown.
- Click the circular swap button to flip currencies.
- Click the sun/moon toggle in the top right to switch between dark and light mode.

---

## 12. Project folder structure explained

```
currency-converter-web/
│
├── app.py                     # Flask app: defines web routes (/) and API routes (/api/...)
│
├── services/
│   ├── __init__.py            # Marks this folder as a Python package
│   └── exchange_service.py    # All exchange-rate fetching/caching/conversion logic
│
├── templates/
│   └── index.html             # The single HTML page (Jinja2 template rendered by Flask)
│
├── static/
│   ├── css/
│   │   └── style.css          # All styling: theme, glassmorphism, layout, animations
│   └── js/
│       └── script.js          # Frontend logic: fetch calls, dropdowns, swap, theming
│
├── requirements.txt           # Exact Python package versions this project needs
├── .env.example                # Template for environment variables (copy to .env)
├── .gitignore                  # Files/folders Git should ignore (venv, .env, caches...)
└── README.md                   # This file
```

**Why this structure?**
- `app.py` stays thin - it only handles HTTP requests/responses and input validation.
- `services/` holds business logic (talking to the external exchange rate API), separate from routing. This makes the code easier to test, read, and reuse.
- `templates/` and `static/` follow Flask's default conventions, so `render_template()` and `url_for('static', ...)` work with zero extra configuration.

---

## 13. How the app works (high level)

1. The browser loads `/`, which Flask serves using `templates/index.html`.
2. `static/js/script.js` runs and calls `GET /api/currencies` using the Fetch API to populate both dropdowns.
3. It then calls `GET /api/convert?from=USD&to=EUR&amount=1` to display an initial conversion.
4. Whenever you change the amount or a currency, JavaScript waits briefly (debounce) then calls `/api/convert` again via AJAX - no page reload needed.
5. `app.py` validates the request and calls `services/exchange_service.py`, which:
   - Checks a short-lived in-memory cache first.
   - If no API key is set, or the primary provider fails, automatically falls back to a free public exchange-rate API.
   - Returns the conversion rate and result as JSON.
6. The JavaScript animates the new result into view and updates the small "1 USD = 0.92 EUR" rate line.

---

## 14. Common errors and how to fix them

### ❌ `'python' is not recognized as an internal or external command`
**Cause:** Python isn't installed, or wasn't added to PATH.
**Fix:** Reinstall Python and make sure to check **"Add python.exe to PATH"** during setup (Windows). Restart VS Code afterwards.

---

### ❌ PowerShell: `venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system`
**Cause:** Windows PowerShell blocks script execution by default.
**Fix:** Run this once in the same terminal, then try activating again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Type `Y` and press Enter when prompted, then re-run `venv\Scripts\Activate.ps1`.

---

### ❌ `ModuleNotFoundError: No module named 'flask'`
**Cause:** Either the virtual environment isn't activated, or dependencies weren't installed.
**Fix:**
1. Make sure you see `(venv)` in your terminal prompt. If not, activate it (see [section 7](#7-activate-the-virtual-environment)).
2. Run `pip install -r requirements.txt` again.

---

### ❌ `Address already in use` / `OSError: [Errno 48] Address already in use`
**Cause:** Something else (maybe a previous run of this app) is already using port 5000.
**Fix:** Either stop the other process, or run this app on a different port by editing `.env`:
```
PORT=5001
```
Then restart with `python app.py` and visit `http://127.0.0.1:5001`.

---

### ❌ Browser shows "Could not load the currency list" or "Rate unavailable"
**Cause:** No internet connection, or the exchange rate API is temporarily down/rate-limited.
**Fix:**
1. Check your internet connection.
2. Wait a minute and try again (the free fallback API has rate limits).
3. If you added an API key in `.env`, double-check it was copied correctly and that you restarted `python app.py` after editing `.env` (environment variables are only read on startup).

---

### ❌ `pip: command not found` (macOS/Linux)
**Fix:** Use `pip3` instead of `pip`, or make sure your virtual environment is activated (it provides its own `pip`).

---

### ❌ Changes to CSS/JS don't seem to appear in the browser
**Cause:** Browser caching.
**Fix:** Hard-refresh the page: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (macOS).

---

### ❌ `SyntaxError` when running `python app.py`
**Cause:** Usually an outdated Python version.
**Fix:** Confirm you're running Python 3.9+ with `python --version`. Reinstall a newer version if needed (see [section 2](#2-install-python)).

---

## 15. Useful VS Code terminal commands cheat sheet

| Task | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Check Python version | `python --version` | `python3 --version` |
| Create virtual environment | `python -m venv venv` | `python3 -m venv venv` |
| Activate virtual environment | `venv\Scripts\Activate.ps1` | `source venv/bin/activate` |
| Deactivate virtual environment | `deactivate` | `deactivate` |
| Install dependencies | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Run the app | `python app.py` | `python3 app.py` |
| Stop the app | `Ctrl + C` | `Ctrl + C` |
| Copy env template | `Copy-Item .env.example .env` | `cp .env.example .env` |

---

## 16. Next steps / ideas to extend the project

Once you're comfortable running the app, here are some beginner-friendly ways to extend it:

- Add historical rate charts using a JavaScript charting library.
- Add more currencies to `services/exchange_service.py`'s `SUPPORTED_CURRENCIES` list.
- Persist recently used currency pairs using the browser's `localStorage`.
- Add unit tests for `services/exchange_service.py` using `pytest`.
- Deploy the app using `gunicorn` (already included in `requirements.txt`) on a platform like Render, Railway, or Fly.io.

---

**Enjoy building!** If you run into an issue not covered here, re-read the terminal output carefully - Python and Flask error messages usually tell you exactly which line and file caused the problem.
