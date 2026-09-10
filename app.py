import tkinter as tk
from tkinter import scrolledtext, simpledialog
from pathlib import Path

from agent import BusinessAutomationAgent


BACKGROUND = "#0b0b0b"
SURFACE = "#151515"
CARD = "#1c1c1c"
INPUT_BG = "#050505"

TEXT = "#f3e7d3"
MUTED_TEXT = "#c7b9a5"

ACCENT = "#d6b98c"
ACCENT_HOVER = "#c6a46f"

SUCCESS = "#a7d7a0"
BORDER = "#3a342c"
TEMPLATE_BG = "#2b251f"


agent = BusinessAutomationAgent()


def set_result(message):
    result_box.config(state=tk.NORMAL)
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, message)
    result_box.config(state=tk.DISABLED)


def run_request():

    request = request_box.get("1.0", tk.END).strip()

    if not request:
        status_label.config(text="Please enter a business request.", fg="#f87171")
        set_result("Your response will appear here.")
        return

    receiver = receiver_entry.get().strip() or "customer@example.com"
    subject = subject_entry.get().strip() or "Business Request Update"
    report_title = report_title_entry.get().strip() or "Business Analysis Report"
    customer_name = customer_name_entry.get().strip() or "Customer"

    status_label.config(text="AI is processing your request...", fg=ACCENT)
    set_result("Please wait...")
    run_button.config(state=tk.DISABLED)
    window.update_idletasks()

    try:
        response = agent.process_request(
            request,
            receiver=receiver,
            subject=subject,
            report_title=report_title,
            customer_name=customer_name
        )

        set_result(response)

        status_label.config(
            text="Automation completed successfully. Output file was saved.",
            fg=SUCCESS
        )

    except Exception as error:
        set_result(f"Something went wrong:\n\n{error}")
        status_label.config(text="Automation failed. Please try again.", fg="#f87171")

    finally:
        run_button.config(state=tk.NORMAL)


def clear_fields():

    request_box.delete("1.0", tk.END)
    receiver_entry.delete(0, tk.END)
    subject_entry.delete(0, tk.END)
    report_title_entry.delete(0, tk.END)
    customer_name_entry.delete(0, tk.END)

    set_result("Your response will appear here.")
    status_label.config(text="Fields cleared. Ready for a new request.", fg=MUTED_TEXT)


def copy_response():

    response = result_box.get("1.0", tk.END).strip()

    if not response or response == "Your response will appear here.":
        status_label.config(text="No response available to copy.", fg="#f87171")
        return

    window.clipboard_clear()
    window.clipboard_append(response)

    status_label.config(text="AI response copied to clipboard.", fg=SUCCESS)


def show_saved_files():

    output_folder = Path("outputs")

    if not output_folder.exists():
        set_result("No saved output files found yet.")
        status_label.config(text="No output files found.", fg="#f87171")
        return

    files = list(output_folder.glob("*.txt"))

    if not files:
        set_result("No saved output files found yet.")
        status_label.config(text="No output files found.", fg="#f87171")
        return

    file_list = "\n".join(file.name for file in files)

    set_result(f"========== SAVED OUTPUT FILES ==========\n\n{file_list}")
    status_label.config(text="Saved output files loaded.", fg=SUCCESS)


def open_saved_file():

    file_name = simpledialog.askstring(
        "Open Saved File",
        "Enter the saved .txt file name:"
    )

    if not file_name:
        return

    if file_name != Path(file_name).name or not file_name.endswith(".txt"):
        status_label.config(text="Please enter a valid .txt file name.", fg="#f87171")
        return

    file_path = Path("outputs") / file_name

    if not file_path.exists():
        status_label.config(text="File not found.", fg="#f87171")
        return

    set_result(file_path.read_text(encoding="utf-8"))
    status_label.config(text=f"Opened: {file_name}", fg=SUCCESS)


def load_template(template_type):

    clear_fields()

    if template_type == "email":
        request_box.insert(
            tk.END,
            "Write an email to a customer informing them that their order has shipped."
        )
        subject_entry.insert(0, "Your Order Has Shipped")
        status_label.config(text="Email template loaded.", fg=ACCENT)

    elif template_type == "report":
        request_box.insert(
            tk.END,
            "Create a sales report for 100 orders with total revenue of 50000 rupees."
        )
        report_title_entry.insert(0, "Monthly Sales Report")
        status_label.config(text="Report template loaded.", fg=ACCENT)

    elif template_type == "support":
        request_box.insert(
            tk.END,
            "My order has not arrived yet. Please write a polite reply to the customer."
        )
        customer_name_entry.insert(0, "Customer")
        status_label.config(text="Customer support template loaded.", fg=ACCENT)


def create_compact_entry(parent, label_text, row, column):

    field_frame = tk.Frame(parent, bg=CARD)
    field_frame.grid(row=row, column=column, sticky="ew", padx=5, pady=5)

    label = tk.Label(
        field_frame,
        text=label_text,
        font=("Segoe UI", 9),
        bg=CARD,
        fg=MUTED_TEXT,
        anchor="w"
    )
    label.pack(fill="x", pady=(0, 4))

    entry = tk.Entry(
        field_frame,
        font=("Segoe UI", 10),
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT
    )
    entry.pack(fill="x", ipady=7)

    return entry


window = tk.Tk()

window.title("AI Business Automation Agent")
window.geometry("1100x700")
window.minsize(900, 650)
window.configure(bg=BACKGROUND)


header = tk.Frame(window, bg=SURFACE, height=90)
header.pack(fill="x")
header.pack_propagate(False)

header_title = tk.Label(
    header,
    text="AI Business Automation Agent",
    font=("Segoe UI", 20, "bold"),
    bg=SURFACE,
    fg=TEXT
)
header_title.pack(anchor="w", padx=30, pady=(14, 2))

header_subtitle = tk.Label(
    header,
    text="Create emails, business reports, and customer support replies using AI.",
    font=("Segoe UI", 10),
    bg=SURFACE,
    fg=MUTED_TEXT
)
header_subtitle.pack(anchor="w", padx=30)


main_frame = tk.Frame(window, bg=BACKGROUND)
main_frame.pack(fill="both", expand=True, padx=25, pady=18)

left_panel = tk.Frame(
    main_frame,
    bg=CARD,
    padx=20,
    pady=18,
    highlightthickness=1,
    highlightbackground=BORDER
)
left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

right_panel = tk.Frame(
    main_frame,
    bg=CARD,
    padx=20,
    pady=18,
    highlightthickness=1,
    highlightbackground=BORDER
)
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))


input_title = tk.Label(
    left_panel,
    text="Create Automation",
    font=("Segoe UI", 15, "bold"),
    bg=CARD,
    fg=TEXT
)
input_title.pack(anchor="w")

input_subtitle = tk.Label(
    left_panel,
    text="Choose a template or write your own request.",
    font=("Segoe UI", 10),
    bg=CARD,
    fg=MUTED_TEXT
)
input_subtitle.pack(anchor="w", pady=(2, 10))


template_frame = tk.Frame(left_panel, bg=CARD)
template_frame.pack(fill="x", pady=(0, 12))

email_template_button = tk.Button(
    template_frame,
    text="Email",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=6,
    command=lambda: load_template("email")
)
email_template_button.pack(side="left", padx=(0, 5))

report_template_button = tk.Button(
    template_frame,
    text="Report",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=6,
    command=lambda: load_template("report")
)
report_template_button.pack(side="left", padx=5)

support_template_button = tk.Button(
    template_frame,
    text="Support",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=12,
    pady=6,
    command=lambda: load_template("support")
)
support_template_button.pack(side="left", padx=5)


request_label = tk.Label(
    left_panel,
    text="Business Request",
    font=("Segoe UI", 10),
    bg=CARD,
    fg=MUTED_TEXT,
    anchor="w"
)
request_label.pack(fill="x", pady=(0, 5))

request_box = scrolledtext.ScrolledText(
    left_panel,
    height=4,
    font=("Segoe UI", 10),
    bg=INPUT_BG,
    fg=TEXT,
    insertbackground=TEXT,
    wrap=tk.WORD,
    relief="flat",
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=ACCENT
)
request_box.pack(fill="x", pady=(0, 8))


details_frame = tk.Frame(left_panel, bg=CARD)
details_frame.pack(fill="x", pady=(0, 10))

details_frame.columnconfigure(0, weight=1)
details_frame.columnconfigure(1, weight=1)

receiver_entry = create_compact_entry(details_frame, "Receiver Email", 0, 0)
subject_entry = create_compact_entry(details_frame, "Email Subject", 0, 1)
report_title_entry = create_compact_entry(details_frame, "Report Title", 1, 0)
customer_name_entry = create_compact_entry(details_frame, "Customer Name", 1, 1)


button_frame = tk.Frame(left_panel, bg=CARD)
button_frame.pack(fill="x", pady=(6, 0))

run_button = tk.Button(
    button_frame,
    text="Run Automation",
    font=("Segoe UI", 11, "bold"),
    bg=ACCENT,
    fg="#1b140b",
    activebackground=ACCENT_HOVER,
    activeforeground="#1b140b",
    relief="flat",
    cursor="hand2",
    padx=18,
    pady=9,
    command=run_request
)
run_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

clear_button = tk.Button(
    button_frame,
    text="Clear",
    font=("Segoe UI", 11, "bold"),
    bg=BORDER,
    fg=TEXT,
    activebackground="#544a3d",
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=18,
    pady=9,
    command=clear_fields
)
clear_button.pack(side="right", padx=(5, 0))

copy_button = tk.Button(
    left_panel,
    text="Copy Response",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=16,
    pady=6,
    command=copy_response
)
copy_button.pack(pady=(8, 0))

view_files_button = tk.Button(
    left_panel,
    text="View Saved Files",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=16,
    pady=6,
    command=show_saved_files
)
view_files_button.pack(pady=(6, 0))

open_file_button = tk.Button(
    left_panel,
    text="Open Saved File",
    font=("Segoe UI", 10, "bold"),
    bg=TEMPLATE_BG,
    fg=TEXT,
    activebackground=BORDER,
    activeforeground=TEXT,
    relief="flat",
    cursor="hand2",
    padx=16,
    pady=6,
    command=open_saved_file
)
open_file_button.pack(pady=(6, 0))


response_title = tk.Label(
    right_panel,
    text="AI Response",
    font=("Segoe UI", 15, "bold"),
    bg=CARD,
    fg=TEXT
)
response_title.pack(anchor="w")

response_subtitle = tk.Label(
    right_panel,
    text="Your generated business output appears below.",
    font=("Segoe UI", 10),
    bg=CARD,
    fg=MUTED_TEXT
)
response_subtitle.pack(anchor="w", pady=(2, 12))

result_box = scrolledtext.ScrolledText(
    right_panel,
    font=("Segoe UI", 10),
    bg=INPUT_BG,
    fg=TEXT,
    insertbackground=TEXT,
    wrap=tk.WORD,
    relief="flat",
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=ACCENT
)
result_box.pack(fill="both", expand=True)

result_box.insert(tk.END, "Your response will appear here.")
result_box.config(state=tk.DISABLED)


status_label = tk.Label(
    window,
    text="Ready to automate your business tasks.",
    font=("Segoe UI", 10),
    bg=BACKGROUND,
    fg=MUTED_TEXT,
    anchor="w"
)
status_label.pack(fill="x", padx=30, pady=(0, 12))


window.mainloop()