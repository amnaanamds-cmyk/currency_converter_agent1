"""
ui.py
-----
Tkinter user interface for the Currency Converter Agent.

Layout (top to bottom, single window):
    1. Converter card: amount entry, source/target searchable currency
       dropdowns, a swap button, and a Convert button.
    2. Result panel: converted amount, live rate, last-updated timestamp,
       and (when applicable) an offline/cached-rate warning.
    3. Travel context card: coffee / meal / hotel price references for the
       target country (converted into the source currency), a tipping-
       culture note, and backpacker/mid-range/luxury daily budgets.

All network calls run on a background thread so the UI never freezes;
results are handed back to the main thread via a queue.Queue and polled
with Tk's `.after()`.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import font as tkfont
from tkinter import ttk
from typing import Dict, Optional

import api
import travel_data

# --------------------------------------------------------------------------- #
# Color / style constants (kept centralized for a clean, consistent look)
# --------------------------------------------------------------------------- #

COLOR_BG = "#f4f6f9"
COLOR_CARD = "#ffffff"
COLOR_PRIMARY = "#2f6fed"
COLOR_PRIMARY_DARK = "#2557c4"
COLOR_TEXT = "#1f2430"
COLOR_MUTED = "#667085"
COLOR_ERROR = "#c0392b"
COLOR_ERROR_BG = "#fdecea"
COLOR_WARN = "#8a6100"
COLOR_WARN_BG = "#fff4d6"
COLOR_SUCCESS = "#1c7c3f"


class SearchableCurrencyCombobox(ttk.Combobox):
    """A ttk.Combobox that filters its dropdown list as the user types.

    Values are displayed as "CODE - Currency Name" but the underlying
    3-letter ISO code can always be retrieved with `get_code()`.
    """

    def __init__(self, master: tk.Widget, currencies: Dict[str, str], **kwargs) -> None:
        """Initialize the searchable combobox.

        Args:
            master: Parent widget.
            currencies: Mapping of currency code -> display name.
            **kwargs: Extra keyword arguments passed to ttk.Combobox.
        """
        self.currencies: Dict[str, str] = currencies
        self._all_display = self._build_display_list(currencies)
        super().__init__(master, values=self._all_display, **kwargs)
        self.bind("<KeyRelease>", self._on_keyrelease)

    @staticmethod
    def _build_display_list(currencies: Dict[str, str]) -> list:
        return sorted(f"{code} - {name}" for code, name in currencies.items())

    def update_currencies(self, currencies: Dict[str, str]) -> None:
        """Replace the underlying currency list (e.g. after a live refresh)."""
        self.currencies = currencies
        self._all_display = self._build_display_list(currencies)
        self["values"] = self._all_display

    def _on_keyrelease(self, event: tk.Event) -> None:
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return
        typed = self.get().upper()
        filtered = self._all_display if not typed else [
            d for d in self._all_display if typed in d.upper()
        ]
        self["values"] = filtered
        if filtered:
            self.event_generate("<Down>")

    def get_code(self) -> str:
        """Return the 3-letter currency code currently entered/selected."""
        val = self.get().strip()
        if " - " in val:
            return val.split(" - ")[0].strip().upper()
        return val.upper()

    def set_code(self, code: str) -> None:
        """Programmatically set the widget to a given currency code."""
        code = code.upper()
        name = self.currencies.get(code, "")
        self.set(f"{code} - {name}" if name else code)


class CurrencyConverterApp:
    """Main application window for the Currency Converter Agent."""

    def __init__(self, root: tk.Tk) -> None:
        """Build the full UI and kick off an async currency-list refresh.

        Args:
            root: The Tk root window.
        """
        self.root = root
        self.root.title("Currency Converter Agent")
        self.root.geometry("620x760")
        self.root.minsize(560, 700)
        self.root.configure(bg=COLOR_BG)

        self._result_queue: "queue.Queue" = queue.Queue()
        self.currencies: Dict[str, str] = dict(api.STATIC_CURRENCY_NAMES)
        self._last_rate_result: Optional[api.RateResult] = None

        self._setup_style()
        self._build_layout()
        self._refresh_currency_list_async()

    # ------------------------------------------------------------------ #
    # Style / layout construction
    # ------------------------------------------------------------------ #

    def _setup_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.font_title = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_section = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_body = tkfont.Font(family="Segoe UI", size=10)
        self.font_result = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=9)

        style.configure("Card.TFrame", background=COLOR_CARD)
        style.configure("App.TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=self.font_body)
        style.configure("App.TLabel", background=COLOR_BG)
        style.configure("Muted.TLabel", foreground=COLOR_MUTED, background=COLOR_CARD, font=self.font_small)
        style.configure("Section.TLabel", font=self.font_section, background=COLOR_CARD, foreground=COLOR_TEXT)
        style.configure(
            "Primary.TButton",
            background=COLOR_PRIMARY, foreground="white",
            font=self.font_body, padding=8, borderwidth=0,
        )
        style.map("Primary.TButton", background=[("active", COLOR_PRIMARY_DARK)])
        style.configure("Swap.TButton", font=self.font_body, padding=4)
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=6)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(outer, text="\U0001F4B1 Currency Converter Agent",
                           font=self.font_title, style="App.TLabel", foreground=COLOR_TEXT)
        title.pack(anchor="w", pady=(0, 12))

        self._build_converter_card(outer)
        self._build_result_card(outer)
        self._build_travel_card(outer)

    def _build_converter_card(self, parent: tk.Widget) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))

        ttk.Label(card, text="Amount", style="TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.amount_var = tk.StringVar(value="100")
        self.amount_entry = ttk.Entry(card, textvariable=self.amount_var, font=self.font_body)
        self.amount_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 12))

        ttk.Label(card, text="From", style="TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(card, text="", style="TLabel").grid(row=2, column=1)
        ttk.Label(card, text="To", style="TLabel").grid(row=2, column=2, sticky="w")

        self.source_combo = SearchableCurrencyCombobox(card, self.currencies, width=18)
        self.source_combo.grid(row=3, column=0, sticky="ew", padx=(0, 4))
        self.source_combo.set_code("USD")

        swap_btn = ttk.Button(card, text="\u21C4", width=3, style="Swap.TButton", command=self._swap_currencies)
        swap_btn.grid(row=3, column=1, padx=4)

        self.target_combo = SearchableCurrencyCombobox(card, self.currencies, width=18)
        self.target_combo.grid(row=3, column=2, sticky="ew", padx=(4, 0))
        self.target_combo.set_code("EUR")

        card.columnconfigure(0, weight=1)
        card.columnconfigure(2, weight=1)

        self.convert_btn = ttk.Button(card, text="Convert", style="Primary.TButton", command=self._start_conversion)
        self.convert_btn.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(14, 0))

        self.error_label = tk.Label(
            card, text="", font=self.font_small, fg=COLOR_ERROR, bg=COLOR_ERROR_BG,
            wraplength=540, justify="left", padx=8, pady=6,
        )
        # gridded on demand in _show_error / hidden via grid_remove

    def _build_result_card(self, parent: tk.Widget) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))
        self.result_card = card

        self.result_amount_label = ttk.Label(card, text="Enter an amount and press Convert",
                                              font=self.font_result, style="TLabel", foreground=COLOR_PRIMARY_DARK)
        self.result_amount_label.pack(anchor="w")

        self.result_rate_label = ttk.Label(card, text="", style="Muted.TLabel")
        self.result_rate_label.pack(anchor="w", pady=(4, 0))

        self.result_time_label = ttk.Label(card, text="", style="Muted.TLabel")
        self.result_time_label.pack(anchor="w")

        self.cache_warning_label = tk.Label(
            card, text="", font=self.font_small, fg=COLOR_WARN, bg=COLOR_WARN_BG,
            wraplength=540, justify="left", padx=8, pady=6,
        )
        # gridded/packed on demand

    def _build_travel_card(self, parent: tk.Widget) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.pack(fill="both", expand=True)
        self.travel_card = card

        self.travel_title_label = ttk.Label(card, text="Travel Context", style="Section.TLabel")
        self.travel_title_label.pack(anchor="w", pady=(0, 8))

        self.travel_body = ttk.Frame(card, style="Card.TFrame")
        self.travel_body.pack(fill="both", expand=True)

        self.travel_placeholder = ttk.Label(
            self.travel_body,
            text="Convert a currency to see coffee, meal, hotel prices, a tipping note, "
                 "and daily budget estimates for that destination.",
            style="Muted.TLabel", wraplength=540, justify="left",
        )
        self.travel_placeholder.pack(anchor="w")

    # ------------------------------------------------------------------ #
    # Currency list refresh (background)
    # ------------------------------------------------------------------ #

    def _refresh_currency_list_async(self) -> None:
        def worker() -> None:
            currencies = api.get_supported_currencies()
            self._result_queue.put(("currencies", currencies, None))

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(150, self._poll_queue)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #

    def _swap_currencies(self) -> None:
        source_code = self.source_combo.get_code()
        target_code = self.target_combo.get_code()
        self.source_combo.set_code(target_code)
        self.target_combo.set_code(source_code)

    def _start_conversion(self) -> None:
        self._hide_error()

        amount_text = self.amount_var.get().strip()
        try:
            amount = float(amount_text)
            if amount < 0:
                raise ValueError
        except ValueError:
            self._show_error("Please enter a valid, non-negative numeric amount.")
            return

        source = self.source_combo.get_code()
        target = self.target_combo.get_code()

        if not source or not target or len(source) != 3 or len(target) != 3:
            self._show_error(f"Please choose valid 3-letter currency codes (got '{source}' -> '{target}').")
            return

        self.convert_btn.config(state="disabled", text="Converting...")
        self.result_amount_label.config(text="Fetching live rate...")
        self._hide_cache_warning()

        def worker() -> None:
            try:
                rate_result = api.get_exchange_rate(source, target)
                self._result_queue.put(("convert_success", rate_result, amount))
            except api.CurrencyAPIError as exc:
                self._result_queue.put(("convert_error", str(exc), amount))
            except Exception as exc:  # noqa: BLE001 - surface any unexpected failure gracefully
                self._result_queue.put(("convert_error", f"Unexpected error: {exc}", amount))

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(100, self._poll_queue)

    # ------------------------------------------------------------------ #
    # Queue polling (keeps all Tk widget updates on the main thread)
    # ------------------------------------------------------------------ #

    def _poll_queue(self) -> None:
        try:
            while True:
                kind, payload, extra = self._result_queue.get_nowait()
                if kind == "currencies":
                    self._on_currencies_loaded(payload)
                elif kind == "convert_success":
                    self._on_convert_success(payload, extra)
                elif kind == "convert_error":
                    self._on_convert_error(payload)
        except queue.Empty:
            pass
        self.root.after(150, self._poll_queue)

    def _on_currencies_loaded(self, currencies: Dict[str, str]) -> None:
        if not currencies:
            return
        self.currencies = currencies
        source_code = self.source_combo.get_code()
        target_code = self.target_combo.get_code()
        self.source_combo.update_currencies(currencies)
        self.target_combo.update_currencies(currencies)
        if source_code:
            self.source_combo.set_code(source_code)
        if target_code:
            self.target_combo.set_code(target_code)

    def _on_convert_success(self, rate_result: api.RateResult, amount: float) -> None:
        self.convert_btn.config(state="normal", text="Convert")
        self._last_rate_result = rate_result
        converted = api.converted_amount(amount, rate_result)

        self.result_amount_label.config(
            text=f"{amount:,.2f} {rate_result.base} = {converted:,.2f} {rate_result.target}"
        )
        self.result_rate_label.config(
            text=f"Live rate: 1 {rate_result.base} = {rate_result.rate:,.4f} {rate_result.target}"
            f"  (source: {rate_result.source})"
        )

        if rate_result.is_cached:
            try:
                ts = datetime.fromisoformat(rate_result.timestamp)  # type: ignore[attr-defined]
            except Exception:
                ts = None
            when = rate_result.timestamp
            self.result_time_label.config(text=f"Rate last fetched: {when}")
            self._show_cache_warning(
                "\u26A0 No live connection available - showing the last cached rate "
                f"from {when}. Values may be out of date."
            )
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.result_time_label.config(text=f"Last updated: {now_str}")
            self._hide_cache_warning()

        self._render_travel_context(rate_result, amount)

    def _on_convert_error(self, message: str) -> None:
        self.convert_btn.config(state="normal", text="Convert")
        self.result_amount_label.config(text="Conversion failed")
        self.result_rate_label.config(text="")
        self.result_time_label.config(text="")
        self._hide_cache_warning()
        self._show_error(message)

    # ------------------------------------------------------------------ #
    # Travel context rendering
    # ------------------------------------------------------------------ #

    def _render_travel_context(self, rate_result: api.RateResult, amount: float) -> None:
        for child in self.travel_body.winfo_children():
            child.destroy()

        context = travel_data.get_travel_context(rate_result.target)
        source = rate_result.base

        if context is None:
            self.travel_title_label.config(text="Travel Context")
            ttk.Label(
                self.travel_body,
                text=f"No curated travel-cost data is available yet for {rate_result.target}.",
                style="Muted.TLabel", wraplength=540, justify="left",
            ).pack(anchor="w")
            return

        self.travel_title_label.config(text=f"Travel Context: {context['country']} ({rate_result.target})")

        def to_source(local_amount: float) -> float:
            if rate_result.rate == 0:
                return 0.0
            return local_amount / rate_result.rate

        # --- Coffee / meal / hotel reference prices -------------------- #
        items_frame = ttk.Frame(self.travel_body, style="Card.TFrame")
        items_frame.pack(fill="x", pady=(0, 12))

        references = [
            ("\u2615  Coffee", context["coffee"]),
            ("\U0001F37D  Mid-range meal", context["meal"]),
            ("\U0001F6CF  Budget hotel / night", context["hotel"]),
        ]
        for row, (label_text, local_amount) in enumerate(references):
            ttk.Label(items_frame, text=label_text, style="TLabel").grid(row=row, column=0, sticky="w", pady=2)
            converted_text = f"\u2248 {to_source(local_amount):,.2f} {source}"
            local_text = f"({local_amount:,.2f} {rate_result.target})"
            ttk.Label(items_frame, text=converted_text, style="TLabel",
                      font=self.font_body).grid(row=row, column=1, sticky="w", padx=(12, 6))
            ttk.Label(items_frame, text=local_text, style="Muted.TLabel").grid(row=row, column=2, sticky="w")

        # --- Tipping note ------------------------------------------------ #
        ttk.Label(self.travel_body, text="Tipping culture", style="Section.TLabel").pack(anchor="w", pady=(4, 2))
        ttk.Label(
            self.travel_body, text=context["tipping"], style="TLabel",
            wraplength=540, justify="left",
        ).pack(anchor="w", pady=(0, 12))

        # --- Daily budget table ------------------------------------------ #
        ttk.Label(self.travel_body, text="Estimated daily budget", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        budget_frame = ttk.Frame(self.travel_body, style="Card.TFrame")
        budget_frame.pack(fill="x")

        budget_rows = [
            ("Backpacker", context["budget"]["backpacker"]),
            ("Mid-range", context["budget"]["mid_range"]),
            ("Luxury", context["budget"]["luxury"]),
        ]
        for row, (label_text, local_amount) in enumerate(budget_rows):
            ttk.Label(budget_frame, text=label_text, style="TLabel").grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(
                budget_frame,
                text=f"\u2248 {to_source(local_amount):,.2f} {source} / day",
                style="TLabel", font=self.font_body,
            ).grid(row=row, column=1, sticky="w", padx=(12, 6))
            ttk.Label(
                budget_frame, text=f"({local_amount:,.2f} {rate_result.target})", style="Muted.TLabel",
            ).grid(row=row, column=2, sticky="w")

    # ------------------------------------------------------------------ #
    # Error / warning banners
    # ------------------------------------------------------------------ #

    def _show_error(self, message: str) -> None:
        self.error_label.config(text=f"\u26A0 {message}")
        self.error_label.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))

    def _hide_error(self) -> None:
        self.error_label.grid_remove()

    def _show_cache_warning(self, message: str) -> None:
        self.cache_warning_label.config(text=message)
        self.cache_warning_label.pack(anchor="w", pady=(8, 0), fill="x")

    def _hide_cache_warning(self) -> None:
        self.cache_warning_label.pack_forget()


def launch() -> None:
    """Create the Tk root window and start the application's main loop."""
    root = tk.Tk()
    CurrencyConverterApp(root)
    root.mainloop()
