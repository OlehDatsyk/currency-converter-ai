"""
services/ai_service.py
------------------------
All AI/LLM logic lives here. The rest of the app never talks to
OpenAI or Anthropic directly — it calls methods on `AIService`.

Why this matters:
- Keeps prompt engineering in ONE place.
- Makes it trivial to switch providers (see Config.AI_PROVIDER).
- Makes the Flask routes easy to read and test.
"""

from config import Config


class AIServiceError(Exception):
    """Raised when the AI provider fails to return a usable response."""
    pass


class AIService:
    def __init__(self):
        self.provider = Config.AI_PROVIDER

        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "claude":
            self._init_claude()
        else:
            raise AIServiceError(
                f"Unknown AI_PROVIDER '{self.provider}'. Use 'openai' or 'claude'."
            )

    # ------------------------------------------------------------------
    # Provider setup
    # ------------------------------------------------------------------
    def _init_openai(self):
        from openai import OpenAI

        if not Config.OPENAI_API_KEY:
            raise AIServiceError(
                "OPENAI_API_KEY is missing. Add it to your .env file."
            )
        self._client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self._model = Config.OPENAI_MODEL

    def _init_claude(self):
        import anthropic

        if not Config.ANTHROPIC_API_KEY:
            raise AIServiceError(
                "ANTHROPIC_API_KEY is missing. Add it to your .env file."
            )
        self._client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self._model = Config.ANTHROPIC_MODEL

    # ------------------------------------------------------------------
    # Low-level "ask the model" helper
    # ------------------------------------------------------------------
    def _ask(self, system_prompt, user_prompt, max_tokens=500):
        """Sends a single prompt to whichever provider is configured
        and returns the plain text reply."""
        try:
            if self.provider == "openai":
                response = self._client.chat.completions.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content.strip()

            # provider == "claude"
            response = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()

        except Exception as exc:  # noqa: BLE001 - surface any provider error uniformly
            raise AIServiceError(f"AI provider request failed: {exc}")

    # ------------------------------------------------------------------
    # Feature-specific prompts
    # ------------------------------------------------------------------
    SYSTEM_PERSONA = (
        "You are a friendly, concise financial assistant embedded in a "
        "currency converter web app. You explain exchange rates, travel "
        "money tips, and general investment ideas in plain English. "
        "You are NOT a licensed financial advisor: always add a brief, "
        "natural disclaimer when giving investment-flavoured suggestions. "
        "Keep responses tight — use short paragraphs or bullet points, "
        "no more than ~150 words unless asked for more detail."
    )

    def explain_exchange_rate(self, base, target, rate, amount, converted_amount):
        prompt = (
            f"Explain this currency conversion to an everyday user:\n"
            f"- 1 {base} = {rate} {target}\n"
            f"- {amount} {base} converts to {converted_amount} {target}\n\n"
            f"Briefly mention 1-2 plausible macroeconomic factors that "
            f"generally influence the {base}/{target} pair (interest rates, "
            f"trade balance, inflation, central bank policy, etc.) without "
            f"inventing specific news events or numbers you don't actually know."
        )
        return self._ask(self.SYSTEM_PERSONA, prompt)

    def summarize_trend(self, base, target, history):
        """`history` is a list of {date, rate} dicts, oldest first."""
        if not history:
            return "Not enough historical data was available to summarize a trend."

        first = history[0]
        last = history[-1]
        change_pct = ((last["rate"] - first["rate"]) / first["rate"]) * 100

        prompt = (
            f"Here is the {base}/{target} exchange rate trend over the last "
            f"{len(history)} days:\n"
            f"- Start ({first['date']}): {first['rate']}\n"
            f"- End ({last['date']}): {last['rate']}\n"
            f"- Change: {change_pct:.2f}%\n\n"
            f"Summarize this trend in plain English (2-4 sentences): is the "
            f"{base} strengthening or weakening against {target}, and what "
            f"could this mean for someone converting money soon?"
        )
        return self._ask(self.SYSTEM_PERSONA, prompt)

    def travel_recommendation(self, base, target, rate):
        prompt = (
            f"A traveller is going from a country using {base} to a country "
            f"using {target}. The current rate is 1 {base} = {rate} {target}. "
            f"Give 3-4 short, practical money tips for this trip (e.g. best "
            f"way to exchange money, whether to use cards vs cash, general "
            f"budgeting mindset). Keep it as a short bullet list."
        )
        return self._ask(self.SYSTEM_PERSONA, prompt)

    def investment_suggestion(self, base, target, history):
        trend_desc = "insufficient historical data"
        if history and len(history) >= 2:
            change_pct = (
                (history[-1]["rate"] - history[0]["rate"]) / history[0]["rate"]
            ) * 100
            trend_desc = f"{change_pct:.2f}% change over {len(history)} days"

        prompt = (
            f"Currency pair {base}/{target} has shown: {trend_desc}. "
            f"Give a brief, general-education perspective (NOT personalized "
            f"financial advice) on how currency movements like this are "
            f"typically thought about by everyday savers/investors (e.g. "
            f"diversification, hedging, DCA, long time horizon). Explicitly "
            f"remind the reader this is educational, not a recommendation "
            f"to buy or sell anything, and that they should consult a "
            f"licensed financial advisor for personal advice."
        )
        return self._ask(self.SYSTEM_PERSONA, prompt)

    def compare_currencies(self, currency_list, rates_vs_usd):
        """
        `rates_vs_usd` is a dict {currency_code: rate_vs_usd}
        """
        lines = "\n".join(
            f"- {code}: 1 USD = {rate} {code}" for code, rate in rates_vs_usd.items()
        )
        prompt = (
            f"Compare these currencies relative to USD:\n{lines}\n\n"
            f"In 3-5 sentences, give the user a plain-English comparison: "
            f"which currencies are relatively strong/weak vs USD right now, "
            f"and one general observation about the group (e.g. region, "
            f"volatility) without inventing specific facts you don't know."
        )
        return self._ask(self.SYSTEM_PERSONA, prompt)

    def chat_reply(self, conversation_history, user_message):
        """
        General-purpose conversational endpoint used by the chat widget.
        `conversation_history` is a list of {role, content} dicts.
        """
        try:
            if self.provider == "openai":
                messages = [{"role": "system", "content": self.SYSTEM_PERSONA}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": user_message})
                response = self._client.chat.completions.create(
                    model=self._model, max_tokens=400, messages=messages
                )
                return response.choices[0].message.content.strip()

            # claude
            messages = list(conversation_history) + [
                {"role": "user", "content": user_message}
            ]
            response = self._client.messages.create(
                model=self._model,
                max_tokens=400,
                system=self.SYSTEM_PERSONA,
                messages=messages,
            )
            return response.content[0].text.strip()

        except Exception as exc:  # noqa: BLE001
            raise AIServiceError(f"AI provider request failed: {exc}")
