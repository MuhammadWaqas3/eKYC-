import re

bot_reply = "[DATA_COLLECTED] Name: John Doe, Email: john@example.com, Phone: +923001234567, Account Type: Savings"

name_match = re.search(r"Name: (.*?),", bot_reply)
email_match = re.search(r"Email: (.*?),", bot_reply)
phone_match = re.search(r"Phone: (.*?),", bot_reply)
account_match = re.search(r"Account Type: (.*)", bot_reply)

if name_match and email_match and phone_match and account_match:
    print("Name:", name_match.group(1).strip())
    print("Email:", email_match.group(1).strip())
    print("Phone:", phone_match.group(1).strip())
    print("Account Type:", account_match.group(1).strip())
else:
    print("Extraction failed")
