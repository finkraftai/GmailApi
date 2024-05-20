import os.path
import base64
import re
import csv
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import zipfile
import io
import email
from extract_msg import Message
from collections import defaultdict

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

def save_msg_attachment(attachment_data, filename, folder_path):
    """Save MSG attachment to the specified folder."""
    try:
        msg = Message(io.BytesIO(attachment_data))
        msg.save(customPath=folder_path)
        print(f"MSG attachment '{filename}' extracted and saved to '{folder_path}'.")
    except Exception as e:
        print(f"Error saving MSG attachment '{filename}': {e}")    


def save_eml_attachments(msg, folder_path):
    """Extract and save attachments from an EML message object."""
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        attachment_name = part.get_filename()
        if attachment_name:
            attachment_data = part.get_payload(decode=True)
            attachment_name = os.path.basename(attachment_name)  # Ensure filename is just the name, not the path
            save_attachment(attachment_data, attachment_name, folder_path)
            

def save_attachment(attachment_data, filename, folder_path):
    """Save attachment to the specified folder."""
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(attachment_data)) as zip_ref:
            zip_ref.extractall(folder_path)
        print(f"Zip attachment '{filename}' extracted and saved to '{folder_path}'.")
    elif filename.lower().endswith('.eml'):
        with open(file_path, 'wb') as f:
            f.write(attachment_data)
        print(f"EML attachment '{filename}' saved to '{folder_path}'. Extracting nested attachments...")
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f)
            save_eml_attachments(msg, folder_path)
    elif filename.lower().endswith('.msg'):
        save_msg_attachment(attachment_data, filename, folder_path)
    else:
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(folder_path, f"{base}_{counter}{extension}")
            counter += 1
        with open(file_path, "wb") as f:
            f.write(attachment_data)
        print(f"Attachment '{filename}' saved to '{file_path}'.")

def get_label_id(service, user_id, label_name):
    """Get the ID of the specified label."""
    labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
    for label in labels:
        if label["name"] == label_name:
            return label["id"]
    return None

def count_emails_per_day(service, user_id, start_date, end_date):
    """Count the number of emails received per day within the specified date range."""
    email_counts = defaultdict(int)
    try:
        query = f"after:{start_date} before:{end_date}"
        messages = []
        page_token = None
        while True:
            results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
            headers = msg["payload"]["headers"]
            date = next((header["value"] for header in headers if header["name"] == "Date"), None)
            if date:
                for date_format in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
                    try:
                        dt = datetime.strptime(date, date_format)
                        dt = dt.astimezone(pytz.utc)
                        day = dt.date()
                        email_counts[day] += 1
                        break
                    except ValueError:
                        pass
        print("Emails received per day:")
        for day, count in sorted(email_counts.items()):
            print(f"{day}: {count} emails")
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=54543)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    user_id = "me"
    
    filters_label_id = get_label_id(service, user_id, "n")
    if not filters_label_id:
        filters_label_id = create_label(service, user_id, "n")
    
    start_date = datetime(2024, 5, 13).strftime('%Y-%m-%d')
    end_date = datetime(2024, 5, 14).strftime('%Y-%m-%d')
    count_emails_per_day(service, user_id, start_date, end_date)

    try:
        query = f"after:{start_date} before:{end_date}"
        page_token = None
        messages = []
        while True:
            results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        print("Messages:")
        
        with open("emails.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["From", "To", "Subject", "Time", "noofattachments", "noofattachments_downloaded"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for message in messages:
                try:
                    msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
                    headers = msg["payload"]["headers"]
                    from_email = next((header["value"] for header in headers if header["name"] == "From"), None)
                    to_email = next((header["value"] for header in headers if header["name"] == "To"), None)
                    subject = next((header["value"] for header in headers if header["name"] == "Subject"), None)
                    date = next((header["value"] for header in headers if header["name"] == "Date"), None)
                    time = ""
                    if date:
                        for date_format in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
                            try:
                                dt = datetime.strptime(date, date_format)
                                dt = dt.astimezone(pytz.utc)
                                time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                                break
                            except ValueError:
                                pass
                    
                    service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [filters_label_id]}).execute()
                    print(f"Message with subject '{subject}' filtered and labeled as 'filters'.")

                    attachment_count = 0
                    downloaded_count = 0
                    if "parts" in msg["payload"]:
                        for part in msg["payload"]["parts"]:
                            if part.get("filename") and part.get("body") and part["body"].get("attachmentId"):
                                attachment_count += 1
                                attachment = service.users().messages().attachments().get(
                                    userId=user_id, messageId=message["id"], id=part["body"]["attachmentId"]
                                ).execute()
                                attachment_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                                filename = part["filename"]
                                save_attachment(attachment_data, filename, "attachments")
                                downloaded_count += 1
                    writer.writerow({"From": from_email, "To": to_email, "Subject": subject, "Time": time, "noofattachments": attachment_count, "noofattachments_downloaded": downloaded_count})
                except HttpError as error:
                    if error.resp.status == 400 and 'failedPrecondition' in str(error):
                        print(f"Skipping message with subject '{subject}' due to precondition failure.")
                    else:
                        raise error
        print("Email information saved to 'emails.csv'.")
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
