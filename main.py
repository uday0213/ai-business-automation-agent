from datetime import datetime
from pathlib import Path

from agent import BusinessAutomationAgent


def save_to_history(request, response):

    with open("history.txt", "a", encoding="utf-8") as file:
        file.write("\n" + "=" * 50 + "\n")
        file.write(f"Date and Time: {datetime.now()}\n")
        file.write(f"User Request: {request}\n")
        file.write("\nAI Response:\n")
        file.write(response)
        file.write("\n" + "=" * 50 + "\n")


def show_history():

    try:
        with open("history.txt", "r", encoding="utf-8") as file:
            print("\n========== REQUEST HISTORY ==========")
            print(file.read())

    except FileNotFoundError:
        print("\nNo history found yet. Run an automation first.")


def clear_history():

    confirm = input("\nType 'yes' to clear all history: ").strip().lower()

    if confirm == "yes":
        with open("history.txt", "w", encoding="utf-8") as file:
            file.write("")

        print("\nHistory cleared successfully.")

    else:
        print("\nHistory was not cleared.")


def show_output_files():

    output_folder = Path("outputs")

    if not output_folder.exists():
        print("\nNo output files found yet.")
        return

    files = list(output_folder.glob("*.txt"))

    if not files:
        print("\nNo output files found yet.")
        return

    print("\n========== SAVED OUTPUT FILES ==========")

    for file in files:
        print(file.name)


def open_output_file():

    file_name = input("\nEnter output file name: ").strip()

    if file_name != Path(file_name).name or not file_name.endswith(".txt"):
        print("\nPlease enter a valid .txt file name.")
        return

    file_path = Path("outputs") / file_name

    if not file_path.exists():
        print("\nFile not found.")
        return

    print("\n========== FILE CONTENT ==========")
    print(file_path.read_text(encoding="utf-8"))


def show_stats():

    output_folder = Path("outputs")

    email_count = len(list(output_folder.glob("email_*.txt")))
    report_count = len(list(output_folder.glob("report_*.txt")))
    support_count = len(list(output_folder.glob("support_response_*.txt")))

    print("\n========== AUTOMATION STATS ==========")
    print(f"Emails created: {email_count}")
    print(f"Reports created: {report_count}")
    print(f"Support responses created: {support_count}")


def main():

    agent = BusinessAutomationAgent()

    print("======================================")
    print("     AI BUSINESS AUTOMATION AGENT")
    print("======================================")
    print("Type 'help' for examples.")
    print("Type 'history' to view saved requests.")
    print("Type 'files' to view saved output files.")
    print("Type 'open' to read a saved output file.")
    print("Type 'stats' to view automation counts.")
    print("Type 'clear' to clear saved history.")
    print("Type 'exit' to close the program.")

    while True:

        request = input("\nEnter your business request: ").strip()

        if request.lower() == "exit":
            print("\nThank you for using AI Business Automation Agent!")
            break

        if request.lower() == "history":
            show_history()
            continue

        if request.lower() == "files":
            show_output_files()
            continue

        if request.lower() == "open":
            open_output_file()
            continue

        if request.lower() == "stats":
            show_stats()
            continue

        if request.lower() == "clear":
            clear_history()
            continue

        if request.lower() == "help":
            print("\nAvailable automations:")

            print("\n1. EMAIL")
            print("   Example: Write an email to a customer about order shipment.")

            print("\n2. REPORT")
            print("   Example: Create a sales report for 100 orders.")

            print("\n3. CUSTOMER SUPPORT")
            print("   Example: My order is delayed. Write a polite reply.")

            continue

        if not request:
            print("\nPlease enter a business request.")
            continue

        try:
            print("\nAI is processing...")

            response = agent.process_request(request)

            print("\n========== AI RESPONSE ==========")
            print(response)

            save_to_history(request, response)

            print("\nRequest saved to history.txt")

        except Exception as error:
            print("\nSomething went wrong.")
            print(f"Error: {error}")


if __name__ == "__main__":
    main()