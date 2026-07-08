/**
 * Exchange Desk — Currency Converter
 * ------------------------------------
 * Front-end logic. No frameworks, no build step — just the Fetch API,
 * vanilla DOM manipulation, and a few small animations.
 *
 * Responsibilities:
 *   1. Load the supported currency list from /api/currencies and fill
 *      the two <select> dropdowns.
 *   2. Call /api/convert whenever the amount or currencies change
 *      (debounced) and animate the result in.
 *   3. Handle the swap button, quick-pair shortcuts, loading spinner,
 *      error banner, and dark/light theme toggle.
 */

(() => {
  "use strict";

  // ---- DOM references ----------------------------------------------------
  const fromCurrencySelect = document.getElementById("fromCurrency");
  const toCurrencySelect = document.getElementById("toCurrency");
  const fromAmountInput = document.getElementById("fromAmount");
  const resultValueEl = document.getElementById("resultValue");
  const rateLineText = document.getElementById("rateLineText");
  const convertBtn = document.getElementById("convertBtn");
  const swapBtn = document.getElementById("swapBtn");
  const errorBanner = document.getElementById("errorBanner");
  const themeToggle = document.getElementById("themeToggle");
  const quickPairsList = document.getElementById("quickPairs");
  const optionTemplate = document.getElementById("currencyOptionTemplate");

  const DEBOUNCE_MS = 450;
  const QUICK_PAIRS = [
    ["USD", "EUR"],
    ["USD", "GBP"],
    ["EUR", "GBP"],
    ["USD", "JPY"],
    ["GBP", "INR"],
    ["USD", "PKR"],
  ];

  let debounceTimer = null;
  let currentRequestId = 0; // guards against out-of-order responses

  // ---- Theme handling ------------------------------------------------------
  function initTheme() {
    const saved = localStorage.getItem("ec-theme");
    const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
    const theme = saved || (prefersLight ? "light" : "dark");
    applyTheme(theme);
  }

  function applyTheme(theme) {
    if (theme === "light") {
      document.documentElement.setAttribute("data-theme", "light");
      themeToggle.setAttribute("aria-pressed", "false");
    } else {
      document.documentElement.removeAttribute("data-theme");
      themeToggle.setAttribute("aria-pressed", "true");
    }
    localStorage.setItem("ec-theme", theme);
  }

  themeToggle.addEventListener("click", () => {
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    applyTheme(isLight ? "dark" : "light");
  });

  // ---- Error banner helpers -------------------------------------------------
  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.hidden = false;
  }

  function clearError() {
    errorBanner.hidden = true;
    errorBanner.textContent = "";
  }

  // ---- Populate currency dropdowns -------------------------------------------
  async function loadCurrencies() {
    try {
      const response = await fetch("/api/currencies");
      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Could not load currency list.");
      }

      fillSelect(fromCurrencySelect, data.currencies, "USD");
      fillSelect(toCurrencySelect, data.currencies, "EUR");
      buildQuickPairs();
      runConversion();
    } catch (err) {
      showError("Could not load the currency list. Check your connection and refresh.");
      console.error(err);
    }
  }

  function fillSelect(selectEl, currencies, defaultCode) {
    selectEl.innerHTML = "";
    currencies.forEach(({ code, name }) => {
      const option = optionTemplate.content.firstElementChild.cloneNode(true);
      option.value = code;
      option.textContent = `${code} — ${name}`;
      if (code === defaultCode) option.selected = true;
      selectEl.appendChild(option);
    });
  }

  function buildQuickPairs() {
    quickPairsList.innerHTML = "";
    QUICK_PAIRS.forEach(([from, to]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quick-pair";
      btn.textContent = `${from} → ${to}`;
      btn.addEventListener("click", () => {
        fromCurrencySelect.value = from;
        toCurrencySelect.value = to;
        runConversion();
      });
      quickPairsList.appendChild(btn);
    });
  }

  // ---- Conversion ---------------------------------------------------------------
  function scheduleConversion() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runConversion, DEBOUNCE_MS);
  }

  async function runConversion() {
    clearError();

    const from = fromCurrencySelect.value;
    const to = toCurrencySelect.value;
    const rawAmount = fromAmountInput.value.trim();

    if (!from || !to) return;

    const amount = parseFloat(rawAmount);
    if (rawAmount === "" || Number.isNaN(amount) || amount < 0) {
      resultValueEl.textContent = "0.00";
      rateLineText.textContent = "Enter a valid amount to convert.";
      return;
    }

    const requestId = ++currentRequestId;
    setLoading(true);

    try {
      const params = new URLSearchParams({ from, to, amount: String(amount) });
      const response = await fetch(`/api/convert?${params.toString()}`);
      const data = await response.json();

      // Ignore stale responses if the user changed inputs again quickly.
      if (requestId !== currentRequestId) return;

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Conversion failed.");
      }

      animateResult(data.result);
      rateLineText.textContent =
        `1 ${data.from} = ${formatNumber(data.rate, 6)} ${data.to}`;
    } catch (err) {
      if (requestId !== currentRequestId) return;
      showError(err.message || "Something went wrong. Please try again.");
      rateLineText.textContent = "Rate unavailable.";
    } finally {
      if (requestId === currentRequestId) setLoading(false);
    }
  }

  function setLoading(isLoading) {
    convertBtn.classList.toggle("is-loading", isLoading);
    convertBtn.disabled = isLoading;
  }

  function formatNumber(value, maxDecimals = 2) {
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: maxDecimals,
      minimumFractionDigits: 2,
    }).format(value);
  }

  function animateResult(newValue) {
    const formatted = formatNumber(newValue, 4);
    resultValueEl.classList.add("is-updating");
    window.setTimeout(() => {
      resultValueEl.textContent = formatted;
      resultValueEl.classList.remove("is-updating");
    }, 180);
  }

  // ---- Swap button ------------------------------------------------------------------
  swapBtn.addEventListener("click", () => {
    const from = fromCurrencySelect.value;
    const to = toCurrencySelect.value;
    fromCurrencySelect.value = to;
    toCurrencySelect.value = from;

    swapBtn.classList.add("is-spinning");
    window.setTimeout(() => swapBtn.classList.remove("is-spinning"), 400);

    runConversion();
  });

  // ---- Event wiring -------------------------------------------------------------------
  fromAmountInput.addEventListener("input", () => {
    // Allow only digits and a single decimal point while typing.
    fromAmountInput.value = fromAmountInput.value.replace(/[^0-9.]/g, "");
    scheduleConversion();
  });

  fromCurrencySelect.addEventListener("change", runConversion);
  toCurrencySelect.addEventListener("change", runConversion);
  convertBtn.addEventListener("click", runConversion);

  // ---- Init ------------------------------------------------------------------------------
  initTheme();
  loadCurrencies();
})();
