import ollama

from prompt import SYSTEM_PROMPT
from tools import create_email, create_report, create_support_response


class BusinessAutomationAgent:

    def __init__(self):
        self.name = "AI Business Automation Agent"
        self.system_prompt = SYSTEM_PROMPT

    def process_request(
        self,
        request,
        receiver=None,
        subject=None,
        report_title=None,
        customer_name=None
    ):

        # STEP 1: Detect user intent using AI
        intent_prompt = f"""
Classify this business request into exactly ONE category.

EMAIL:
Use this when the user asks to write, draft, compose, or send an email.
Example: "Write an email to a customer that their order has shipped."

REPORT:
Use this when the user asks to create a report, analysis, summary, or sales report.

CUSTOMER_SUPPORT:
Use this only when a customer problem, complaint, refund, return,
or help request needs a support reply.
Example: "My order is late. Help me write a reply to the customer."

GENERAL:
Use this for anything else.

Important:
If the user explicitly asks to write an email, always choose EMAIL,
even if the email is about an order, shipment, or customer.

Request:
{request}

Return only one word:
EMAIL
REPORT
CUSTOMER_SUPPORT
GENERAL
"""

        intent_response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": "You are a business task classification assistant."
                },
                {
                    "role": "user",
                    "content": intent_prompt
                }
            ]
        )

        intent = intent_response["message"]["content"].strip().upper()

        print(f"\nDetected Intent: {intent}")

        # STEP 2: Email Automation
        if intent == "EMAIL":

            email_prompt = f"""
Create the body of a professional business email
based on this request:

{request}

Rules:
- Do NOT write a subject line.
- Start directly with the email greeting.
- Do NOT add a signature or closing.
- Keep it concise and professional.
"""

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": email_prompt
                    }
                ]
            )

            ai_message = response["message"]["content"]

            if not receiver:
                receiver = input("\nEnter receiver email address: ")

            if not subject:
                subject = input("Enter email subject: ")

            return create_email(
                receiver,
                subject,
                ai_message
            )

        # STEP 3: Report Automation
        elif intent == "REPORT":

            report_prompt = f"""
Create a structured business report based on this request:

{request}

Include:

1. Executive Summary
2. Key Information
3. Analysis
4. Recommendations

Keep the report clear, structured and professional.

Do not invent important business information.
Use only the information provided by the user.
"""

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": report_prompt
                    }
                ]
            )

            ai_message = response["message"]["content"]

            if not report_title:
                report_title = input("\nEnter report title: ")

            return create_report(
                report_title,
                ai_message
            )

        # STEP 4: Customer Support Automation
        elif intent == "CUSTOMER_SUPPORT":

            support_prompt = f"""
Generate a professional customer support response
based on this request:

{request}

Rules:
- Be polite and professional.
- Understand the customer's issue.
- Apologize if appropriate.
- Provide a helpful solution.
- Do not invent company policies or information.
- Keep the response concise.
"""

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": support_prompt
                    }
                ]
            )

            ai_message = response["message"]["content"]

            if not customer_name:
                customer_name = input("\nEnter customer name: ")

            return create_support_response(
                customer_name,
                request,
                ai_message
            )

        # STEP 5: General AI Request
        else:

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": request
                    }
                ]
            )

            return response["message"]["content"]