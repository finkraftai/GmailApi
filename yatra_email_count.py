import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import zipfile
import io 
from collections import defaultdict
import pytz  # Import pytz module to handle time zones
import re
import email.utils
from datetime import datetime, timedelta


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def create_label(service, user_id, label_name):
    """Create a new label."""
    label = {"name": label_name}
    try:
        label = service.users().labels().create(userId=user_id, body=label).execute()
        print("Label created: {}".format(label["name"]))
        return label["id"]  # Return the ID of the created label
    except HttpError as error:
        print(f"An error occurred while creating label: {error}")
        return None

def save_attachment(attachment_data, filename, folder_path):
    """Save attachment to the specified folder."""
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith('.zip'):
        # If the attachment is a zip file, extract its contents
        with zipfile.ZipFile(io.BytesIO(attachment_data)) as zip_ref:
            zip_ref.extractall(folder_path)
        print(f"Zip attachment '{filename}' extracted and saved to '{folder_path}'.")
    else:
        # Otherwise, save the attachment as is
        with open(file_path, "wb") as f:
            f.write(attachment_data)
        print(f"Attachment '{filename}' saved to '{folder_path}'.")

# def main():
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "/Users/finkraft/dev/GmailApi/client_secret_605315136561-t9ll05u1bpg2ctudm94u3crt69lr8kt0.apps.googleusercontent.com.json", SCOPES
#             )
#             creds = flow.run_local_server(port=54543)

#         with open("token.json", "w") as token:
#             token.write(creds.to_json())

#     service = build("gmail", "v1", credentials=creds)
#     user_id = "me"
    
#     # Dictionary to store count of emails received per day
#     email_count = 0

#     try:
#         # Get all messages from the mailbox
#         results = service.users().messages().list(userId=user_id).execute()
#         messages = results.get("messages", [])

#         # Specify the target date
#         target_date = datetime(year=2024, month=5, day=13).date()
#         print("Target Date:", target_date)

#         # Iterate through each message and extract the date received
#         for message in messages:
#             msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
#             headers = msg["payload"]["headers"]
#             date = next((header["value"] for header in headers if header["name"] == "Date"), None)
#             if date:
#                 # Remove the day of the week part and time zone information from the date string
#                 date_without_weekday = re.sub(r'^\w+,\s*', '', date)
#                 date_without_timezone = re.sub(r'\s+\(.+\)', '', date_without_weekday)
#                 # Remove the colon from the time zone offset
#                 date_without_timezone = re.sub(r'([+-])(\d{2}):(\d{2})', r'\1\2\3', date_without_timezone)
#                 # Extract the day from the date and check if it matches the target date
#                 dt = datetime.strptime(date_without_timezone, "%d %b %Y %H:%M:%S %z")
#                 msg_date = dt.date()
#                 print("Message Date:", msg_date)
#                 if (msg_date.year, msg_date.month, msg_date.day) == (target_date.year, target_date.month, target_date.day):
#                     email_count += 1

#         # Print the count of emails received on the target date
#         print(f"Emails received on {target_date}: {email_count}")

#     except HttpError as error:
#         print(f"An error occurred: {error}")
def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/finkraft/dev/GmailApi/client_secret_605315136561-t9ll05u1bpg2ctudm94u3crt69lr8kt0.apps.googleusercontent.com.json", SCOPES
            )
            creds = flow.run_local_server(port=54543)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    user_id = "me"
    
    # Variable to store count of emails received on the target date
    email_count = 0

    try:
        # Specify the target date
        target_date = datetime(year=2024, month=5, day=13).date()

        # Get all messages from the mailbox received on the target date
        query = f"after:{target_date} before:{target_date + timedelta(days=1)}"
        messages = []
        page_token = None

        while True:
            results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        # Count the number of messages retrieved
        email_count = len(messages)

        # Print the count of emails received on the target date
        print(f"Emails received on {target_date}: {email_count}")

    except HttpError as error:
        print(f"An error occurred: {error}")



if __name__ == "__main__":
    main()
