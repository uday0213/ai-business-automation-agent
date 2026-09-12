import threading
from pathlib import Path
import tkinter as tk

from tkinter import messagebox

import customtkinter as ctk

from agent import BusinessAutomationAgent


# -----------------------------
# Theme
# -----------------------------
BG = "#0B0B0D"
SURFACE = "#111114"
CARD = "#17171B"
CARD_HOVER = "#1D1D22"
INPUT = "#0F0F12"
BORDER = "#2A2A31"
TEXT = "#F5F1E8"
MUTED = "#9B9AA2"
ACCENT = "#D6B98C"
ACCENT_HOVER = "#E2C99F"
SUCCESS = "#91C89A"
ERROR = "#E07A7A"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

agent = BusinessAutomationAgent()


class AutomationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Business Automation Agent")
        self.geometry("1120x820")
        self.minsize(860, 680)
        self.configure(fg_color=BG)

        self.selected_mode = "general"
        self.animating = False
        self.animation_step = 0

        self._build_header()
        self._build_scroll_area()
        self._build_footer()
        self._set_status("Ready to automate your business tasks.", MUTED)
        self.protocol("WM_DELETE_WINDOW", self._close_app)

    # -----------------------------
    # Layout
    # -----------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=88)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="y", padx=30)

        ctk.CTkLabel(
            left,
            text="✦  AI BUSINESS AUTOMATION",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", pady=(17, 0))

        ctk.CTkLabel(
            left,
            text="Turn natural-language requests into useful business outputs.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=MUTED,
        ).pack(anchor="w", pady=(1, 0))

        self.status_pill = ctk.CTkLabel(
            header,
            text="●  LOCAL AI  •  READY",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=SUCCESS,
            fg_color="#152019",
            corner_radius=16,
            padx=13,
            pady=7,
        )
        self.status_pill.pack(side="right", padx=30, pady=25)

    def _build_scroll_area(self):
        outer = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        outer.pack(fill="both", expand=True)

        # Use a native Tk canvas for scrolling instead of CTkScrollableFrame.
        # This avoids redraw/ghosting artifacts when the mouse wheel is moved
        # very quickly on Windows.
        canvas_shell = ctk.CTkFrame(outer, fg_color=BG, corner_radius=0)
        canvas_shell.pack(fill="both", expand=True, padx=18, pady=(14, 4))
        canvas_shell.grid_rowconfigure(0, weight=1)
        canvas_shell.grid_columnconfigure(0, weight=1)

        self.scroll_canvas = tk.Canvas(
            canvas_shell,
            bg=BG,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(
            canvas_shell,
            orientation="vertical",
            command=self.scroll_canvas.yview,
            button_color="#34343B",
            button_hover_color="#4A4A52",
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = ctk.CTkFrame(self.scroll_canvas, fg_color=BG, corner_radius=0)
        self._content_window = self.scroll_canvas.create_window(
            (10, 4),
            window=self.content,
            anchor="nw",
        )

        self.content.bind("<Configure>", self._content_configured)
        self.scroll_canvas.bind("<Configure>", self._canvas_configured)

        # Controlled wheel scrolling. One wheel event moves a fixed amount,
        # preventing the rapid-scroll redraw/ghosting effect.
        # Bind the wheel once at the application level. Do NOT bind it to every
        # child widget: doing that can flood the Windows event/render queue during
        # rapid scrolling and cause visual ghosting.
        self._wheel_after = None
        self._wheel_units = 0
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

        self._build_hero()
        self._build_templates()
        self._build_request()
        self._build_details()
        self._build_run_area()
        self._build_output()
        self._build_saved_files()

    def _on_mousewheel(self, event):
        # Coalesce very fast wheel events into one small update. This keeps
        # Windows/Tk from processing hundreds of canvas redraws back-to-back.
        units = -int(event.delta / 120)
        if units == 0:
            units = -1 if event.delta > 0 else 1
        self._wheel_units += units

        if self._wheel_after is None:
            self._wheel_after = self.after(8, self._flush_wheel)
        return "break"

    def _flush_wheel(self):
        self._wheel_after = None
        units = self._wheel_units
        self._wheel_units = 0
        if units:
            # Clamp one flush so an extremely fast wheel cannot skip huge
            # sections or trigger a burst of redraws.
            units = max(-6, min(6, units))
            self.scroll_canvas.yview_scroll(units, "units")

    def _content_configured(self, _event=None):
        # Update geometry after Tk finishes the current layout pass.
        self.after_idle(lambda: self.scroll_canvas.configure(
            scrollregion=self.scroll_canvas.bbox(self._content_window)
        ))

    def _canvas_configured(self, event):
        self.scroll_canvas.itemconfigure(
            self._content_window,
            width=max(event.width - 20, 1),
        )
        self.after_idle(lambda: self.scroll_canvas.configure(
            scrollregion=self.scroll_canvas.bbox(self._content_window)
        ))

    def _build_footer(self):
        self.footer = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=42)
        self.footer.pack(fill="x")
        self.footer.pack_propagate(False)

        self.footer_status = ctk.CTkLabel(
            self.footer,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=MUTED,
            anchor="w",
        )
        self.footer_status.pack(fill="x", padx=25, pady=11)

    def _section_label(self, title, subtitle):
        wrapper = ctk.CTkFrame(self.content, fg_color="transparent")
        wrapper.pack(fill="x", pady=(14, 8))

        ctk.CTkLabel(
            wrapper,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            wrapper,
            text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=MUTED,
        ).pack(anchor="w", pady=(2, 0))
        return wrapper

    def _build_hero(self):
        hero = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        hero.pack(fill="x", pady=(4, 8))

        ctk.CTkLabel(
            hero,
            text="Your AI workspace",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=24, pady=(22, 0))

        ctk.CTkLabel(
            hero,
            text="Choose a workflow, describe what you need, and let the agent handle the repetitive work.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=MUTED,
        ).pack(anchor="w", padx=24, pady=(4, 22))

    def _build_templates(self):
        self._section_label("Quick automations", "Start with a workflow or write a completely custom request.")

        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))
        for i in range(4):
            row.grid_columnconfigure(i, weight=1)

        cards = [
            ("✉", "Email", "Professional email", "email"),
            ("▣", "Report", "Business analysis", "report"),
            ("♧", "Support", "Customer response", "support"),
            ("✦", "General", "Ask the AI anything", "general"),
        ]

        for i, (icon, title, desc, mode) in enumerate(cards):
            button = ctk.CTkButton(
                row,
                text=f"{icon}\n{title}\n{desc}",
                height=92,
                fg_color=CARD,
                hover_color=CARD_HOVER,
                border_width=1,
                border_color=BORDER,
                corner_radius=15,
                text_color=TEXT,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                command=lambda m=mode: self.load_template(m),
            )
            button.grid(row=0, column=i, sticky="ew", padx=5)

    def _build_request(self):
        self._section_label("Automation request", "Describe the task in plain language. The agent will detect the intent automatically.")

        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 8))

        self.request_box = ctk.CTkTextbox(
            card,
            height=145,
            fg_color=INPUT,
            border_width=1,
            border_color=BORDER,
            corner_radius=12,
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wrap="word",
        )
        self.request_box.pack(fill="x", padx=15, pady=15)
        self.request_box.insert("1.0", "Tell the AI what you want to automate...")
        self.request_box.bind("<FocusIn>", self._clear_placeholder)
        self.request_box.bind("<FocusOut>", self._restore_placeholder)

    def _build_details(self):
        self._section_label("Additional details", "Only fill the fields relevant to your workflow. Defaults are used when appropriate.")

        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        self.receiver_entry = self._field(card, "Receiver email", "customer@example.com", 0, 0)
        self.subject_entry = self._field(card, "Email subject", "Business Request Update", 0, 1)
        self.report_title_entry = self._field(card, "Report title", "Business Analysis Report", 1, 0)
        self.customer_name_entry = self._field(card, "Customer name", "Customer", 1, 1)

    def _field(self, parent, label, placeholder, row, col):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=row, column=col, sticky="ew", padx=15, pady=(12 if row == 0 else 6, 8))

        ctk.CTkLabel(
            box,
            text=label.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", pady=(0, 5))

        entry = ctk.CTkEntry(
            box,
            height=42,
            fg_color=INPUT,
            border_color=BORDER,
            border_width=1,
            corner_radius=10,
            text_color=TEXT,
            placeholder_text=placeholder,
            placeholder_text_color="#66666E",
            font=ctk.CTkFont(family="Segoe UI", size=11),
        )
        entry.pack(fill="x")
        return entry

    def _build_run_area(self):
        area = ctk.CTkFrame(self.content, fg_color="transparent")
        area.pack(fill="x", pady=(10, 18))

        self.run_button = ctk.CTkButton(
            area,
            text="✦  RUN AUTOMATION",
            height=52,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#17130E",
            corner_radius=13,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.run_request,
        )
        self.run_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.clear_button = ctk.CTkButton(
            area,
            text="Clear",
            width=105,
            height=52,
            fg_color=CARD,
            hover_color=CARD_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            corner_radius=13,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.clear_fields,
        )
        self.clear_button.pack(side="right")

        self.progress = ctk.CTkProgressBar(area, mode="indeterminate", height=3, fg_color="#25252B", progress_color=ACCENT)
        self.progress.pack(fill="x", pady=(8, 0))
        self.progress.stop()
        self.progress.pack_forget()

        self.loading_label = ctk.CTkLabel(
            area,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=ACCENT,
        )
        self.loading_label.pack_forget()

    def _build_output(self):
        self._section_label("AI output", "Your generated business output will appear here.")

        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(fill="x", pady=(0, 8))

        self.result_box = ctk.CTkTextbox(
            card,
            height=300,
            fg_color=INPUT,
            border_width=1,
            border_color=BORDER,
            corner_radius=12,
            text_color=TEXT,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word",
        )
        self.result_box.pack(fill="x", padx=15, pady=(15, 10))
        self._set_result("Your generated response will appear here.")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=15, pady=(0, 15))

        self.copy_button = self._small_button(actions, "Copy response", self.copy_response)
        self.copy_button.pack(side="left", padx=(0, 6))
        self.open_button = self._small_button(actions, "Open saved file", self.open_saved_file)
        self.open_button.pack(side="left", padx=6)
        self.files_button = self._small_button(actions, "View saved files", self.show_saved_files)
        self.files_button.pack(side="left", padx=6)

    def _small_button(self, parent, text, command):
        return ctk.CTkButton(
            parent,
            text=text,
            height=36,
            fg_color="#222127",
            hover_color="#2C2B32",
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            corner_radius=9,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=command,
        )

    def _build_saved_files(self):
        self._section_label("Recent saved outputs", "Outputs generated by the agent are stored locally in the outputs folder.")

        self.saved_frame = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        self.saved_frame.pack(fill="x", pady=(0, 22))
        self.refresh_saved_files()

    # -----------------------------
    # Interaction
    # -----------------------------
    def _clear_placeholder(self, _event=None):
        if self.request_box.get("1.0", "end").strip() == "Tell the AI what you want to automate...":
            self.request_box.delete("1.0", "end")

    def _restore_placeholder(self, _event=None):
        if not self.request_box.get("1.0", "end").strip():
            self.request_box.insert("1.0", "Tell the AI what you want to automate...")

    def _set_status(self, text, color=MUTED):
        self.footer_status.configure(text=text, text_color=color)

    def _set_result(self, text):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")

    def load_template(self, mode):
        self.selected_mode = mode
        self.request_box.delete("1.0", "end")

        if mode == "email":
            self.request_box.insert("1.0", "Write an email to a customer informing them that their order has shipped.")
            self.subject_entry.delete(0, "end")
            self.subject_entry.insert(0, "Your Order Has Shipped")
            self._set_status("Email workflow selected.", ACCENT)

        elif mode == "report":
            self.request_box.insert("1.0", "Create a sales report for 100 orders with total revenue of 50000 rupees.")
            self.report_title_entry.delete(0, "end")
            self.report_title_entry.insert(0, "Monthly Sales Report")
            self._set_status("Report workflow selected.", ACCENT)

        elif mode == "support":
            self.request_box.insert("1.0", "My order has not arrived yet. Please write a polite reply to the customer.")
            self.customer_name_entry.delete(0, "end")
            self.customer_name_entry.insert(0, "Customer")
            self._set_status("Customer support workflow selected.", ACCENT)

        else:
            self.request_box.insert("1.0", "Suggest three ways to improve customer retention for a small business.")
            self._set_status("General AI workflow selected.", ACCENT)

        self._set_result("Your generated response will appear here.")

    def run_request(self):
        request = self.request_box.get("1.0", "end").strip()

        if request == "Tell the AI what you want to automate...":
            request = ""

        if not request:
            self._set_status("Please enter a business request.", ERROR)
            return

        receiver = self.receiver_entry.get().strip() or "customer@example.com"
        subject = self.subject_entry.get().strip() or "Business Request Update"
        report_title = self.report_title_entry.get().strip() or "Business Analysis Report"
        customer_name = self.customer_name_entry.get().strip() or "Customer"

        self.run_button.configure(state="disabled", text="◌  PROCESSING...")
        self.clear_button.configure(state="disabled")
        self._set_result("AI is preparing your business output...\n\nPlease wait.")
        self._set_status("AI is processing your request...", ACCENT)
        self.status_pill.configure(text="●  LOCAL AI  •  WORKING", text_color=ACCENT)
        self.progress.pack(fill="x", pady=(8, 0))
        self.progress.start()
        self.loading_label.pack(pady=(5, 0))
        self.animating = True
        self.animation_step = 0
        self._animate_loading()

        worker = threading.Thread(
            target=self._process_request,
            args=(request, receiver, subject, report_title, customer_name),
            daemon=True,
        )
        worker.start()

    def _process_request(self, request, receiver, subject, report_title, customer_name):
        try:
            response = agent.process_request(
                request,
                receiver=receiver,
                subject=subject,
                report_title=report_title,
                customer_name=customer_name,
            )
            self.after(0, lambda: self._request_success(response))
        except Exception as error:
            self.after(0, lambda: self._request_error(error))

    def _request_success(self, response):
        self._stop_loading()
        self._set_result(response)
        self._set_status("Automation completed successfully. Output was saved.", SUCCESS)
        self.status_pill.configure(text="●  LOCAL AI  •  READY", text_color=SUCCESS)
        self.run_button.configure(state="normal", text="✦  RUN AUTOMATION")
        self.clear_button.configure(state="normal")
        self.refresh_saved_files()

    def _request_error(self, error):
        self._stop_loading()
        self._set_result(f"Something went wrong:\n\n{error}")
        self._set_status("Automation failed. Check that Ollama is running and try again.", ERROR)
        self.status_pill.configure(text="●  LOCAL AI  •  ERROR", text_color=ERROR)
        self.run_button.configure(state="normal", text="✦  RUN AUTOMATION")
        self.clear_button.configure(state="normal")

    def _animate_loading(self):
        if not self.animating:
            return
        dots = "." * ((self.animation_step % 3) + 1)
        self.loading_label.configure(text=f"AI is thinking{dots}")
        self.animation_step += 1
        self.after(420, self._animate_loading)

    def _stop_loading(self):
        self.animating = False
        self.progress.stop()
        self.progress.pack_forget()
        self.loading_label.pack_forget()

    def _close_app(self):
        try:
            self.unbind_all("<MouseWheel>")
        except Exception:
            pass
        self.destroy()

    def clear_fields(self):
        self.request_box.delete("1.0", "end")
        self.request_box.insert("1.0", "Tell the AI what you want to automate...")
        for entry in [self.receiver_entry, self.subject_entry, self.report_title_entry, self.customer_name_entry]:
            entry.delete(0, "end")
        self._set_result("Your generated response will appear here.")
        self._set_status("Fields cleared. Ready for a new request.", MUTED)

    def copy_response(self):
        response = self.result_box.get("1.0", "end").strip()
        if not response or response == "Your generated response will appear here.":
            self._set_status("No response available to copy.", ERROR)
            return
        self.clipboard_clear()
        self.clipboard_append(response)
        self._set_status("AI response copied to clipboard.", SUCCESS)

    def show_saved_files(self):
        folder = Path("outputs")
        files = sorted(folder.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True) if folder.exists() else []
        if not files:
            self._set_result("No saved output files found yet.")
            self._set_status("No output files found.", ERROR)
            return
        text = "RECENT SAVED OUTPUTS\n\n" + "\n".join(f"• {p.name}" for p in files[:20])
        self._set_result(text)
        self._set_status(f"Loaded {min(len(files), 20)} saved output file(s).", SUCCESS)

    def refresh_saved_files(self):
        for widget in self.saved_frame.winfo_children():
            widget.destroy()

        folder = Path("outputs")
        files = sorted(folder.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True) if folder.exists() else []

        if not files:
            ctk.CTkLabel(
                self.saved_frame,
                text="No saved outputs yet. Run an automation to create one.",
                text_color=MUTED,
                font=ctk.CTkFont(family="Segoe UI", size=10),
            ).pack(anchor="w", padx=18, pady=18)
            return

        for path in files[:5]:
            row = ctk.CTkFrame(self.saved_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=5)

            ctk.CTkLabel(
                row,
                text=path.name,
                text_color=TEXT,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=6)

            ctk.CTkButton(
                row,
                text="Open",
                width=70,
                height=28,
                fg_color="#222127",
                hover_color="#2C2B32",
                text_color=TEXT,
                corner_radius=8,
                command=lambda p=path: self.open_file_path(p),
            ).pack(side="right", padx=5)

    def open_file_path(self, path):
        try:
            self._set_result(path.read_text(encoding="utf-8"))
            self._set_status(f"Opened: {path.name}", SUCCESS)
        except Exception as error:
            self._set_status(f"Could not open file: {error}", ERROR)

    def open_saved_file(self):
        folder = Path("outputs")
        files = sorted(folder.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True) if folder.exists() else []
        if not files:
            self._set_status("No saved output files found.", ERROR)
            return
        self.open_file_path(files[0])


if __name__ == "__main__":
    app = AutomationApp()
    app.mainloop()
