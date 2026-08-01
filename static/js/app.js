/* =========================================================================
   Ledger - AI Currency Assistant - Frontend logic
   Vanilla JS, no build step. Talks to the Flask API defined in app.py.
   ========================================================================= */

(() => {
  "use strict";

  // -----------------------------------------------------------------------
  // Constants & state
  // -----------------------------------------------------------------------
  const API = {
    currencies: "/api/currencies",
    convert: "/api/convert",
    historical: "/api/historical",
    trend: "/api/trend",
    travel: "/api/travel-tips",
    invest: "/api/investment-tips",
    compare: "/api/compare",
    chat: "/api/chat",
  };

  const POPULAR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "INR", "AUD", "CAD", "CHF", "CNY", "ZAR"];

  const state = {
    currencies: {},          // { USD: "United States Dollar", ... }
    lastConversion: null,    // last successful /api/convert result
    selectedCompareCodes: new Set(["USD", "EUR", "GBP", "JPY"]),
    chatHistory: [],         // [{role, content}]
  };

  // -----------------------------------------------------------------------
  // DOM references
  // -----------------------------------------------------------------------
  const el = {
    apiStatusPill: document.getElementById("apiStatusPill"),
    themeToggle: document.getElementById("themeToggle"),

    convertForm: document.getElementById("convertForm"),
    amountInput: document.getElementById("amountInput"),
    baseSelect: document.getElementById("baseSelect"),
    targetSelect: document.getElementById("targetSelect"),
    swapBtn: document.getElementById("swapBtn"),
    convertBtn: document.getElementById("convertBtn"),

    resultBox: document.getElementById("resultBox"),
    resultAmount: document.getElementById("resultAmount"),
    resultCurrency: document.getElementById("resultCurrency"),
    resultRate: document.getElementById("resultRate"),

    explanationBlock: document.getElementById("explanationBlock"),
    explanationText: document.getElementById("explanationText"),

    trendChart: document.getElementById("trendChart"),
    chartEmpty: document.getElementById("chartEmpty"),
    trendBtn: document.getElementById("trendBtn"),
    trendBlock: document.getElementById("trendBlock"),
    trendText: document.getElementById("trendText"),

    travelBtn: document.getElementById("travelBtn"),
    travelBlock: document.getElementById("travelBlock"),
    travelText: document.getElementById("travelText"),

    investBtn: document.getElementById("investBtn"),
    investBlock: document.getElementById("investBlock"),
    investText: document.getElementById("investText"),

    chipSelect: document.getElementById("chipSelect"),
    compareBtn: document.getElementById("compareBtn"),
    compareResults: document.getElementById("compareResults"),
    compareTableBody: document.getElementById("compareTableBody"),
    compareText: document.getElementById("compareText"),

    chatLog: document.getElementById("chatLog"),
    chatForm: document.getElementById("chatForm"),
    chatInput: document.getElementById("chatInput"),
    chatSendBtn: document.getElementById("chatSendBtn"),
    clearHistoryBtn: document.getElementById("clearHistoryBtn"),
  };

  // -----------------------------------------------------------------------
  // Utilities
  // -----------------------------------------------------------------------
  async function apiPost(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = await response.json();
    if (!response.ok || !json.success) {
      throw new Error(json.error || "Request failed.");
    }
    return json.data;
  }

  async function apiGet(url) {
    const response = await fetch(url);
    const json = await response.json();
    if (!response.ok || !json.success) {
      throw new Error(json.error || "Request failed.");
    }
    return json.data;
  }

  function formatNumber(n) {
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 4 });
  }

  /** Animates text into a target element character-by-character. */
  function typeText(targetEl, text, speedMs = 14) {
    return new Promise((resolve) => {
      targetEl.textContent = "";
      targetEl.classList.add("is-typing");
      let i = 0;
      const chunk = Math.max(1, Math.round(text.length / 220)); // keep long text snappy
      function step() {
        i += chunk;
        targetEl.textContent = text.slice(0, i);
        if (i < text.length) {
          setTimeout(step, speedMs);
        } else {
          targetEl.textContent = text;
          targetEl.classList.remove("is-typing");
          resolve();
        }
      }
      step();
    });
  }

  function setLoading(button, isLoading, loadingLabel = "Working\u2026") {
    if (isLoading) {
      button.dataset.originalLabel = button.textContent;
      button.textContent = loadingLabel;
      button.disabled = true;
    } else {
      button.textContent = button.dataset.originalLabel || button.textContent;
      button.disabled = false;
    }
  }

  // -----------------------------------------------------------------------
  // Theme (dark mode) - persisted in localStorage
  // -----------------------------------------------------------------------
  function initTheme() {
    const saved = localStorage.getItem("ledger-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved || (prefersDark ? "dark" : "light");
    applyTheme(theme);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    el.themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
    el.themeToggle.querySelector(".theme-toggle__label").textContent =
      theme === "dark" ? "Light mode" : "Dark mode";
    localStorage.setItem("ledger-theme", theme);
  }

  el.themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  });

  // -----------------------------------------------------------------------
  // Load supported currencies -> populate selects + chips
  // -----------------------------------------------------------------------
  async function loadCurrencies() {
    try {
      const data = await apiGet(API.currencies);
      state.currencies = data;
      populateSelects();
      populateChips();
      setStatus(true);
    } catch (err) {
      setStatus(false);
      // Fallback so the UI is still usable even if the API call failed.
      state.currencies = Object.fromEntries(
        POPULAR_CURRENCIES.map((c) => [c, c])
      );
      populateSelects();
      populateChips();
    }
  }

  function setStatus(online) {
    el.apiStatusPill.classList.toggle("online", online);
    el.apiStatusPill.classList.toggle("offline", !online);
    el.apiStatusPill.innerHTML = `<span class="status-dot"></span> ${
      online ? "Connected" : "Offline / check API keys"
    }`;
  }

  function populateSelects() {
    const codes = Object.keys(state.currencies).sort();
    const buildOptions = (selectEl, defaultCode) => {
      selectEl.innerHTML = "";
      codes.forEach((code) => {
        const opt = document.createElement("option");
        opt.value = code;
        opt.textContent = `${code} - ${state.currencies[code]}`;
        if (code === defaultCode) opt.selected = true;
        selectEl.appendChild(opt);
      });
    };
    buildOptions(el.baseSelect, codes.includes("USD") ? "USD" : codes[0]);
    buildOptions(el.targetSelect, codes.includes("EUR") ? "EUR" : codes[1] || codes[0]);
  }

  function populateChips() {
    el.chipSelect.innerHTML = "";
    POPULAR_CURRENCIES.filter((c) => state.currencies[c]).forEach((code) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip" + (state.selectedCompareCodes.has(code) ? " selected" : "");
      chip.textContent = code;
      chip.addEventListener("click", () => {
        if (state.selectedCompareCodes.has(code)) {
          state.selectedCompareCodes.delete(code);
        } else {
          state.selectedCompareCodes.add(code);
        }
        chip.classList.toggle("selected");
      });
      el.chipSelect.appendChild(chip);
    });
  }

  // -----------------------------------------------------------------------
  // Conversion
  // -----------------------------------------------------------------------
  el.swapBtn.addEventListener("click", () => {
    const b = el.baseSelect.value;
    el.baseSelect.value = el.targetSelect.value;
    el.targetSelect.value = b;
  });

  el.convertForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const amount = parseFloat(el.amountInput.value);
    const base = el.baseSelect.value;
    const target = el.targetSelect.value;

    if (!amount || amount <= 0) return;

    setLoading(el.convertBtn, true, "Converting\u2026");
    el.explanationBlock.hidden = true;

    try {
      const data = await apiPost(API.convert, { base, target, amount });
      state.lastConversion = data;

      el.resultBox.hidden = false;
      el.resultAmount.textContent = formatNumber(data.converted_amount);
      el.resultCurrency.textContent = data.target_currency;
      el.resultRate.textContent = `1 ${data.base_currency} = ${formatNumber(data.rate)} ${data.target_currency}`;

      if (data.explanation) {
        el.explanationBlock.hidden = false;
        await typeText(el.explanationText, data.explanation);
      }

      // Enable dependent AI features now that we have a valid pair
      el.trendBtn.disabled = false;
      el.travelBtn.disabled = false;
      el.investBtn.disabled = false;

      loadTrendChart(base, target);
    } catch (err) {
      alert(`Conversion failed: ${err.message}`);
    } finally {
      setLoading(el.convertBtn, false);
    }
  });

  // -----------------------------------------------------------------------
  // Historical chart (lightweight inline SVG line chart, no dependencies)
  // -----------------------------------------------------------------------
  async function loadTrendChart(base, target) {
    try {
      const data = await apiPost(API.historical, { base, target, days: 30 });
      drawChart(data.history);
    } catch (err) {
      el.chartEmpty.hidden = false;
      el.chartEmpty.textContent = `Could not load history: ${err.message}`;
    }
  }

  function drawChart(history) {
    const svg = el.trendChart;
    svg.innerHTML = "";

    if (!history || history.length < 2) {
      el.chartEmpty.hidden = false;
      el.chartEmpty.textContent = "Not enough historical data to draw a chart.";
      return;
    }
    el.chartEmpty.hidden = true;

    const width = 600, height = 220, padding = 24;
    const rates = history.map((h) => h.rate);
    const min = Math.min(...rates), max = Math.max(...rates);
    const range = max - min || 1;

    const points = history.map((h, i) => {
      const x = padding + (i / (history.length - 1)) * (width - padding * 2);
      const y = height - padding - ((h.rate - min) / range) * (height - padding * 2);
      return [x, y];
    });

    const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
    const areaD = `${pathD} L${points[points.length - 1][0]},${height - padding} L${points[0][0]},${height - padding} Z`;

    const ns = "http://www.w3.org/2000/svg";

    const area = document.createElementNS(ns, "path");
    area.setAttribute("d", areaD);
    area.setAttribute("class", "chart-area");
    area.setAttribute("fill", "var(--color-weave)");
    area.setAttribute("stroke", "none");
    svg.appendChild(area);

    const line = document.createElementNS(ns, "path");
    line.setAttribute("d", pathD);
    line.setAttribute("fill", "none");
    line.setAttribute("stroke", "var(--color-green)");
    line.setAttribute("stroke-width", "2.5");
    line.setAttribute("stroke-linejoin", "round");
    line.setAttribute("stroke-linecap", "round");
    svg.appendChild(line);

    // Start / end dots + labels
    [0, points.length - 1].forEach((idx) => {
      const [x, y] = points[idx];
      const dot = document.createElementNS(ns, "circle");
      dot.setAttribute("cx", x); dot.setAttribute("cy", y); dot.setAttribute("r", 4);
      dot.setAttribute("fill", "var(--color-gold)");
      svg.appendChild(dot);

      const label = document.createElementNS(ns, "text");
      label.setAttribute("x", x); label.setAttribute("y", idx === 0 ? y - 10 : y - 10);
      label.setAttribute("text-anchor", idx === 0 ? "start" : "end");
      label.setAttribute("font-size", "11");
      label.setAttribute("font-family", "var(--font-mono)");
      label.setAttribute("fill", "var(--color-ink-soft)");
      label.textContent = history[idx].rate.toFixed(4);
      svg.appendChild(label);
    });
  }

  // -----------------------------------------------------------------------
  // AI feature buttons: trend / travel / investment / compare
  // -----------------------------------------------------------------------
  el.trendBtn.addEventListener("click", async () => {
    if (!state.lastConversion) return;
    const { base_currency: base, target_currency: target } = state.lastConversion;
    setLoading(el.trendBtn, true, "Analyzing\u2026");
    try {
      const data = await apiPost(API.trend, { base, target, days: 30 });
      el.trendBlock.hidden = false;
      await typeText(el.trendText, data.summary);
    } catch (err) {
      alert(`Could not summarize trend: ${err.message}`);
    } finally {
      setLoading(el.trendBtn, false);
    }
  });

  el.travelBtn.addEventListener("click", async () => {
    if (!state.lastConversion) return;
    const { base_currency: base, target_currency: target } = state.lastConversion;
    setLoading(el.travelBtn, true, "Thinking\u2026");
    try {
      const data = await apiPost(API.travel, { base, target });
      el.travelBlock.hidden = false;
      await typeText(el.travelText, data.tips);
    } catch (err) {
      alert(`Could not fetch travel tips: ${err.message}`);
    } finally {
      setLoading(el.travelBtn, false);
    }
  });

  el.investBtn.addEventListener("click", async () => {
    if (!state.lastConversion) return;
    const { base_currency: base, target_currency: target } = state.lastConversion;
    setLoading(el.investBtn, true, "Thinking\u2026");
    try {
      const data = await apiPost(API.invest, { base, target, days: 30 });
      el.investBlock.hidden = false;
      await typeText(el.investText, data.suggestion);
    } catch (err) {
      alert(`Could not fetch investment insight: ${err.message}`);
    } finally {
      setLoading(el.investBtn, false);
    }
  });

  el.compareBtn.addEventListener("click", async () => {
    const codes = Array.from(state.selectedCompareCodes);
    if (codes.length < 2) {
      alert("Select at least two currencies to compare.");
      return;
    }
    setLoading(el.compareBtn, true, "Comparing\u2026");
    try {
      const data = await apiPost(API.compare, { currencies: codes });
      el.compareResults.hidden = false;
      el.compareTableBody.innerHTML = Object.entries(data.rates)
        .map(([code, rate]) => `<tr><td>${code}</td><td>${formatNumber(rate)}</td></tr>`)
        .join("");
      await typeText(el.compareText, data.comparison);
    } catch (err) {
      alert(`Comparison failed: ${err.message}`);
    } finally {
      setLoading(el.compareBtn, false);
    }
  });

  // -----------------------------------------------------------------------
  // Chat / conversation history
  // -----------------------------------------------------------------------
  function appendChatMessage(role, content) {
    const wrap = document.createElement("div");
    wrap.className = `chat-msg chat-msg--${role === "user" ? "user" : "assistant"}`;
    const bubble = document.createElement("span");
    bubble.className = "chat-msg__bubble";
    wrap.appendChild(bubble);
    el.chatLog.appendChild(wrap);
    el.chatLog.scrollTop = el.chatLog.scrollHeight;
    return bubble;
  }

  function persistChatHistory() {
    localStorage.setItem("ledger-chat-history", JSON.stringify(state.chatHistory));
  }

  function restoreChatHistory() {
    const saved = localStorage.getItem("ledger-chat-history");
    if (!saved) return;
    try {
      const history = JSON.parse(saved);
      history.forEach((msg) => {
        const bubble = appendChatMessage(msg.role, msg.content);
        bubble.textContent = msg.content;
      });
      state.chatHistory = history;
    } catch (_) {
      /* ignore corrupted local storage */
    }
  }

  el.chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = el.chatInput.value.trim();
    if (!message) return;

    appendChatMessage("user", message).textContent = message;
    state.chatHistory.push({ role: "user", content: message });
    persistChatHistory();
    el.chatInput.value = "";

    const assistantBubble = appendChatMessage("assistant", "");
    assistantBubble.classList.add("typing-target");
    setLoading(el.chatSendBtn, true, "\u2026");

    try {
      const data = await apiPost(API.chat, {
        message,
        history: state.chatHistory.slice(0, -1), // exclude the message just sent (server appends it)
      });
      await typeText(assistantBubble, data.reply);
      state.chatHistory.push({ role: "assistant", content: data.reply });
      persistChatHistory();
    } catch (err) {
      assistantBubble.textContent = `Sorry, something went wrong: ${err.message}`;
    } finally {
      setLoading(el.chatSendBtn, false);
      el.chatLog.scrollTop = el.chatLog.scrollHeight;
    }
  });

  el.clearHistoryBtn.addEventListener("click", () => {
    state.chatHistory = [];
    localStorage.removeItem("ledger-chat-history");
    el.chatLog.innerHTML = "";
    appendChatMessage("assistant", "").textContent =
      "Conversation cleared. Ask me anything about currencies!";
  });

  // -----------------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------------
  initTheme();
  loadCurrencies();
  restoreChatHistory();
})();
