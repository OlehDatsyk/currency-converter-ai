# Project Review - Ledger: AI Currency Assistant

**Reviewed as:** Senior Software Engineer / Code Reviewer / DevOps Engineer
**Review type:** Read-only audit. No source files were modified as part of this review.
**Scope:** `app.py`, `config.py`, `services/`, `utils/`, `templates/`, `static/`, project root config files.

---

## 1. Repository file checklist

| File | Status | Notes |
|---|---|---|
| `README.md` | ✅ Present | Already comprehensive (beginner setup guide, API reference, deployment guide). Not regenerated, per instructions. |
| `LICENSE` | ❌ Missing | See §2 |
| `.gitignore` | ✅ Present | Covers `.env`, `__pycache__/`, `venv/`, `.vscode/`, OS files, `*.log`. Reasonable for this project. |
| `requirements.txt` | ✅ Present | Pinned versions for all 6 dependencies. |
| `pyproject.toml` | ❌ Missing | See §2 |
| `.env.example` | ✅ Present | Well-commented, includes both AI providers and the currency API key. |

### Why the missing files matter

**`LICENSE`** - Without a license file, the project is **all rights reserved by default** under copyright law, even if it's public on GitHub. Anyone who finds the repo technically cannot legally copy, modify, or reuse the code - even for learning - without explicit permission. If the intent is to share this as an open-source portfolio piece or let others build on it, an `MIT` or `Apache-2.0` license (both permissive and beginner-friendly) should be added. If the intent is to keep it fully proprietary, a license file stating that explicitly is still useful so visitors don't have to guess.

**`pyproject.toml`** - This project currently relies solely on `requirements.txt`, which works fine for a simple Flask app and is not a defect. However, a `pyproject.toml` would let the project: (1) declare itself as an installable package with a single `pip install .`, (2) centralize tool configuration (e.g. `black`, `ruff`, `pytest`) in one file instead of scattering `.flake8`/`pytest.ini`/etc., and (3) be ready for modern packaging/build tooling if this ever grows past a single-file Flask app. For a project this size it is a "nice to have," not a blocker.

---

## 2. Code review findings

Findings are ordered by severity (High -> Low). Nothing below was changed - this is a report only.

### High severity

**H1. Flask debug mode defaults to `True`, including in "production."**
- **File:** `config.py` - `DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"`
- **Why it matters:** If `FLASK_DEBUG` is ever left unset on a real deployment (e.g. a host where the env var wasn't configured), Flask's interactive debugger becomes reachable on any unhandled exception. Werkzeug's debugger allows arbitrary Python code execution from the browser - this is a well-known critical vulnerability if exposed publicly. The README does correctly warn to set `FLASK_DEBUG=False` in production, but the *code's own default* still fails open (defaults to debug **on**) rather than failing safe (defaulting to **off**).
- **Recommendation:** Flip the default so debug mode is **off** unless explicitly enabled: `os.environ.get("FLASK_DEBUG", "False") == "True"`. Production safety should not depend on every deployment target remembering to set an env var.

**H2. Hard-coded fallback `SECRET_KEY`.**
- **File:** `config.py` - `SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")`
- **Why it matters:** Flask's `SECRET_KEY` signs session cookies and CSRF tokens. If a deployment forgets to set `FLASK_SECRET_KEY`, every instance of this app running with the default key shares the exact same, publicly-visible-in-source secret. Anyone can forge session data against it. This app doesn't currently use sessions, but the key is wired up and ready to be used, so the risk is latent rather than theoretical.
- **Recommendation:** In production, fail loudly if `FLASK_SECRET_KEY` isn't set (raise at startup) rather than silently falling back to a guessable default. For local dev, the current fallback is fine and can stay, gated behind a `if DEBUG` check.

### Medium severity

**M1. No rate limiting on AI-backed endpoints.**
- **Files:** `app.py` (`/api/convert`, `/api/trend`, `/api/travel-tips`, `/api/investment-tips`, `/api/compare`, `/api/chat`)
- **Why it matters:** Every one of these routes calls a paid, metered external API (OpenAI or Anthropic) with no per-IP or per-session throttling. A single user (or a script, or a bot that discovers the public URL) could hammer `/api/chat` in a tight loop and run up real billing costs quickly, since there's no cap on requests-per-minute.
- **Recommendation:** Add a lightweight rate limiter such as `Flask-Limiter` (e.g. 10-20 requests/minute per IP on AI routes) before deploying this publicly.

**M2. No automated tests.**
- **Files:** entire project
- **Why it matters:** `services/currency_service.py` and `services/ai_service.py` contain non-trivial branching logic (cache TTL, provider fallback from ExchangeRate-API -> Frankfurter, OpenAI vs Claude branching) with zero test coverage. Any refactor or dependency upgrade (e.g. `openai` or `anthropic` SDK major version bumps, which happen often) has no safety net and could silently break the app.
- **Recommendation:** Add `pytest` + `responses`/`unittest.mock` to cover: cache hit/miss behavior, the Frankfurter fallback path, and both AI provider branches with mocked HTTP calls. The README already promises this under "Future improvements" - worth prioritizing before this goes live.

**M3. In-memory cache is not viable beyond a single dev process.**
- **File:** `services/currency_service.py` - `self._cache = {}` (instance-level dict)
- **Why it matters:** The cache lives on the `CurrencyService` instance created once at import time in `app.py`. This works for local development and single-process deployments, but most production WSGI servers (including the `gunicorn` this project ships a `Procfile` for) spin up multiple worker processes by default - each gets its own empty cache, so the "10-minute cache" claim in the comments silently stops holding true in production with >1 worker, and cache benefits (and API call savings) are inconsistent across requests.
- **Recommendation:** Either pin `gunicorn` to `--workers 1` for this app's scale, or move the cache to something shared across processes (Redis, or even a simple SQLite file) if the app is expected to run with multiple workers.

**M4. `/api/chat` and other endpoints trust client-submitted history size but not content length.**
- **File:** `app.py` - `chat()` function
- **Why it matters:** The code correctly caps history to the last 10 turns (`[-10:]`), which is good. However, neither `message` nor any historical `content` field has a maximum character length enforced. A malicious or buggy client could submit an extremely long single message, inflating token usage/cost per request with no server-side guard.
- **Recommendation:** Add a reasonable max length check (e.g. 2,000-4,000 characters) on `message` and reject/truncate longer input with a clear error.

**M5. `days` parameter type conversion can throw an unhandled `ValueError`.**
- **Files:** `app.py` - `historical_rates()`, `trend_summary()`, `investment_tips()` all do `days = int(payload.get("days", 30))`
- **Why it matters:** If a client sends `days: "abc"` or `days: null`, `int(...)` raises a `ValueError` that isn't caught anywhere in that code path, so it falls through to the generic Flask 500 handler instead of the app's clean `error_response()` JSON envelope. This is a minor inconsistency in error-handling, not a security bug - the app doesn't crash, but the caller gets a generic "Internal server error" instead of a helpful validation message.
- **Recommendation:** Wrap the `int()` conversion in a `try/except (TypeError, ValueError)` and return `error_response("days must be a number.")`, consistent with how `amount` is already validated in `convert_currency()`.

### Low severity

**L1. Broad `except Exception` in `ai_service.py`.**
- **File:** `services/ai_service.py` - `_ask()` and `chat_reply()` both use `except Exception as exc:` (with a `# noqa: BLE001` acknowledging the tradeoff).
- **Why it matters:** This is a defensible, intentional choice here - it uniformly converts any SDK-level failure (network errors, auth errors, malformed responses) into a single `AIServiceError` the routes already know how to handle, and it's explicitly commented as a deliberate decision rather than an oversight. Flagged only because blanket exception handling can occasionally swallow real bugs (e.g. a `TypeError` from a code mistake would look identical to a network failure to anyone debugging from logs alone).
- **Recommendation:** Optional: log `exc` (via Python's `logging` module) before re-raising as `AIServiceError`, so the original traceback isn't lost when triaging issues.

**L2. No structured logging anywhere in the app.**
- **Files:** entire project
- **Why it matters:** There are no `logging` calls at all - errors are only ever surfaced as JSON responses to the client. In production, this means there's no server-side record of failures (bad API keys, upstream API outages, stack traces) unless the hosting platform happens to capture stdout/stderr and someone is actively watching it.
- **Recommendation:** Add basic `logging` configuration in `app.py` (e.g. `logging.basicConfig(level=logging.INFO)`) and log caught exceptions in each route's `except` block before returning the error response.

**L3. `get_supported_currencies()` cache key never expires distinctly from rate caches.**
- **File:** `services/currency_service.py`
- **Why it matters:** Minor: the currency list is cached under the same 10-minute TTL as live exchange rates. The list of supported currencies changes essentially never, so re-fetching it every 10 minutes is a small, unnecessary source of external calls. Not a bug, just a slight inefficiency.
- **Recommendation:** Give `get_supported_currencies()` its own, much longer TTL (e.g. 24 hours) or cache it to a local file at first run.

**L4. No `favicon.ico` / `static/img/` is empty but referenced in README.**
- **Files:** `README.md` folder structure section mentions `static/img/` for icons; the actual `static/` folder in the zip only contains `css/` and `js/` - no `img/` directory exists.
- **Why it matters:** Purely cosmetic - browsers will silently 404 on the default favicon request, which is harmless but shows up as noise in server logs / browser dev tools.
- **Recommendation:** Either add a small `favicon.ico`/`favicon.svg` and link it in `templates/index.html`, or remove the `static/img/` mention from the README folder diagram since the folder isn't actually created.

**L5. Type hints are absent throughout the Python codebase.**
- **Files:** `app.py`, `config.py`, `services/*.py`, `utils/helpers.py`
- **Why it matters:** None of the functions use type hints (e.g. `def convert(self, base_currency, target_currency, amount):`). The code is otherwise clearly written with good docstrings and naming, so this doesn't hurt readability much today, but it means editors/IDEs can't catch type mistakes (e.g. passing a `str` where a `float` is expected) before runtime, and it's a bit more work for new contributors to understand expected shapes at a glance.
- **Recommendation:** Incrementally add type hints, starting with the `services/` layer (e.g. `def get_live_rate(self, base_currency: str, target_currency: str) -> float:`), since that's the most reused and highest-risk code in the app.

### Positive observations (things done well)

- **Clear separation of concerns:** routes (`app.py`) vs. business logic (`services/`) vs. small utilities (`utils/`) is a clean, conventional Flask layout.
- **No API keys or secrets are hard-coded** anywhere in the source - everything routes through `Config`/`.env`, which is exactly right.
- **Frontend security:** `static/js/app.js` consistently uses `textContent` (not `innerHTML`) when inserting user- or AI-generated text into the DOM (e.g. chat bubbles), which avoids a straightforward XSS vector that's easy to introduce by mistake in vanilla-JS chat widgets.
- **Sensible fallbacks:** the currency service gracefully falls back from the paid ExchangeRate-API to the free, keyless Frankfurter API when no key is configured, so the app is usable out-of-the-box.
- **Consistent JSON envelope** (`{success, data}` / `{success, error}`) across every endpoint makes the frontend's `apiGet`/`apiPost` helpers simple and predictable.
- **Input validation exists** on the endpoints that most need it (currency codes, amount, minimum comparison count), even though a couple of edge cases (see M5) aren't fully covered.
- **No unused or dead code was found** - every file, function, and route observed is reachable and used.
- **No duplicate logic** of any real significance was found between `app.py`, `services/`, and `utils/`.

---

## 3. GitHub readiness review

| Check | Status | Notes |
|---|---|---|
| Repository cleanliness | ✅ Good | No stray temp files, `__pycache__`, or editor cruft found in the archive. |
| `.gitignore` coverage | ✅ Good | Correctly ignores `.env`, virtual environments, bytecode, OS files, logs. |
| API key exposure | ✅ Clean | No real API keys found anywhere in source; `.env.example` uses only placeholder values. |
| Sensitive files present in repo | ✅ None found | No `.env`, credentials, or private keys were included in the uploaded archive. |
| Cache / generated files | ✅ None found | No `__pycache__/`, `.pyc`, or build artifacts present. |
| Virtual environment committed | ✅ Not present | No `venv/`/`.venv/` folder was included. |
| Documentation | ✅ Strong | `README.md` is unusually thorough for a public repo (setup, API reference, deployment, troubleshooting). |
| License | ❌ Missing | See §1/§2 - add before making the repo public if you want others to legally reuse the code. |
| Code quality / consistency | ✅ Good | Consistent style, docstrings on every module and most functions, sensible naming throughout. |

**Overall verdict:** This project is very close to GitHub-ready. The only blocking gap for a "proper" public open-source release is the missing `LICENSE` file (§2). The High-severity findings (H1, H2) are more about safe defaults for whoever *deploys* this app than about publishing the source code itself - they should be addressed before pointing a real domain at a hosted instance, not necessarily before pushing to GitHub.

---

## 4. Repository size audit

| Metric | Value | Within recommended limit? |
|---|---|---|
| Total size (excluding venv/cache - none present) | **160 KB** | ✅ Well under the 20 MB guideline |
| Total file count | **15 files** | ✅ Well under the 100-file guideline |
| Largest individual file | `README.md` (24 KB) | ✅ No concern |

No optimization is needed. This is a small, lean, single-service Flask project - nothing to trim.

---

## 5. Summary

| Category | Result |
|---|---|
| Missing recommended files | `LICENSE`, `pyproject.toml` (see §1 for why they matter) |
| High-severity issues | 2 (unsafe debug-mode default, hard-coded fallback secret key) |
| Medium-severity issues | 5 (no rate limiting, no tests, cache scoping, unbounded chat input, unhandled `int()` conversion) |
| Low-severity issues | 5 (broad exception handling, no logging, minor cache TTL inefficiency, unused `img/` reference, missing type hints) |
| GitHub readiness | Ready, pending a `LICENSE` file |
| Repository size | Well within recommended limits (160 KB, 15 files) |

No project files were modified as part of this review, per the task instructions. All recommendations above are optional next steps for you to apply at your discretion.
