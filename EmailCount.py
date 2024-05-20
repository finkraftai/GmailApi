
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
from datetime import datetime
import pytz  # Import pytz module to handle time zones
import re


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
    
    # Dictionary to store count of emails received per day
    email_counts = defaultdict(int)

    try:
        # Get all messages from the mailbox
        results = service.users().messages().list(userId=user_id).execute()
        messages = results.get("messages", [])

        # Iterate through each message and extract the date received
        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
            headers = msg["payload"]["headers"]
            date = next((header["value"] for header in headers if header["name"] == "Date"), None)
            if date:
                # Remove time zone information from the date string
                date_without_timezone = re.sub(r'\s+\(.+\)', '', date)
                # Extract the day from the date and increment the count
                dt = datetime.strptime(date_without_timezone, "%a, %d %b %Y %H:%M:%S %z")
                # Convert to UTC timezone for consistency
                dt = dt.astimezone(pytz.utc)
                day = dt.date()
                email_counts[day] += 1

        # Print the counts of emails received per day
        print("Emails received per day:")
        for day, count in sorted(email_counts.items()):
            print(f"{day}: {count} emails")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
