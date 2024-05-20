# import os.path
# import base64
# import csv
# import re
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from datetime import datetime
# import pytz

# SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# def create_label(service, user_id, label_name):
#     """Create a new label."""
#     label = {"name": label_name}
#     try:
#         label = service.users().labels().create(userId=user_id, body=label).execute()
#         print("Label created: {}".format(label["name"]))
#         return label["id"]  # Return the ID of the created label
#     except HttpError as error:
#         print(f"An error occurred while creating label: {error}")
#         return None

# def save_attachment(attachment, message_id, folder_path):
#     """Save attachment to the specified folder."""
#     attachment_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
#     filename = attachment.get("filename", f"attachment_{message_id}")
#     file_path = os.path.join(folder_path, filename)
#     with open(file_path, "wb") as f:
#         f.write(attachment_data)
#     print(f"Attachment '{filename}' saved to '{folder_path}'.")

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

#     # Check if label "filters" exists, if not, create it
#     labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
#     filters_label_id = None
#     for label in labels:
#         if label["name"] == "filters":
#             filters_label_id = label["id"]
#             break
#     if not filters_label_id:
#         filters_label_id = create_label(service, user_id, "filters")

#     try:
#         # Get all messages from the mailbox
#         results = service.users().messages().list(userId=user_id).execute()
#         messages = results.get("messages", [])

#         # Initialize CSV writer
#         with open("emails.csv", "w", newline="", encoding="utf-8") as csvfile:
#             fieldnames = ["From", "To", "Subject", "Time"]
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()

#             # Iterate through each message and extract information
#             for message in messages:
#                 msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
#                 headers = msg["payload"]["headers"]
#                 from_email = next((header["value"] for header in headers if header["name"] == "From"), None)
#                 to_email = next((header["value"] for header in headers if header["name"] == "To"), None)
#                 subject = next((header["value"] for header in headers if header["name"] == "Subject"), None)
#                 date = next((header["value"] for header in headers if header["name"] == "Date"), None)
#                 if date:
#                     # Remove time zone information from the date string
#                     date_without_timezone = re.sub(r'\s+\(.+\)', '', date)
#                     # Convert date string to datetime object and format it
#                     dt = datetime.strptime(date_without_timezone, "%a, %d %b %Y %H:%M:%S %z")
#                     dt = dt.astimezone(pytz.utc)
#                     time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
#                 else:
#                     time = ""
                
#                 # Write extracted information to CSV
#                 writer.writerow({"From": from_email, "To": to_email, "Subject": subject, "Time": time})

#                 # Apply label "filters" to the message
#                 service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [filters_label_id]}).execute()

#         print("Email information saved to 'emails.csv'.")

#     except HttpError as error:
#         print(f"An error occurred: {error}")

# if __name__ == "__main__":
#     main()




###################################################
import os.path
import base64
import re
import csv
import pytz
import mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

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

def save_attachment(attachment, message_id, folder_path):
    """Save attachment to the specified folder."""
    attachment_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
    filename = attachment.get("filename", f"attachment_{message_id}")
    # Use filename to determine extension
    _, file_extension = os.path.splitext(filename)
    # If filename doesn't have an extension, attempt to guess from MIME type
    if not file_extension:
        content_type, _ = mimetypes.guess_type(filename)
        if content_type:
            file_extension = mimetypes.guess_extension(content_type)
            if file_extension:
                file_extension = file_extension.lower()
    file_name = f"{filename}{file_extension}"
    file_path = os.path.join(folder_path, file_name)
    # Append a counter to the filename if there are multiple attachments with the same name
    counter = 1
    while os.path.exists(file_path):
        counter += 1
        file_name = f"{filename}_{counter}{file_extension}"
        file_path = os.path.join(folder_path, file_name)
    with open(file_path, "wb") as f:
        f.write(attachment_data)
    print(f"Attachment '{file_name}' saved to '{folder_path}'.")

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

    # Check if label "filters" exists, if not, create it
    labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
    filters_label_id = None
    for label in labels:
        if label["name"] == "filters":
            filters_label_id = label["id"]
            break
    if not filters_label_id:
        filters_label_id = create_label(service, user_id, "filters")

    try:
        # Define date range for filtering emails (May 10, 2024, to May 13, 2024)
        start_date = datetime(2024, 5, 10).strftime('%Y/%m/%d')
        end_date = datetime(2024, 5, 15).strftime('%Y/%m/%d')  # Note: We specify the day after the end date
        query = f"after:{start_date} before:{end_date}"

        # Get all messages from the mailbox within the specified date range
        results = service.users().messages().list(userId=user_id, q=query).execute()
        messages = results.get("messages", [])

        # Initialize CSV writer
        with open("emails.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["From", "To", "Subject", "Time", "Attachments"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Iterate through each message and extract information
            for message in messages:
                msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
                headers = msg["payload"]["headers"]
                from_email = next((header["value"] for header in headers if header["name"] == "From"), None)
                to_email = next((header["value"] for header in headers if header["name"] == "To"), None)
                subject = next((header["value"] for header in headers if header["name"] == "Subject"), None)
                date = next((header["value"] for header in headers if header["name"] == "Date"), None)
                if date:
                    # Remove time zone information from the date string
                    date_without_timezone = re.sub(r'\s+\(.+\)', '', date)
                    # Convert date string to datetime object and format it
                    dt = datetime.strptime(date_without_timezone, "%a, %d %b %Y %H:%M:%S %z")
                    dt = dt.astimezone(pytz.utc)
                    time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                else:
                    time = ""

                # Count the number of attachments
                attachment_count = 0
                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part.get("filename") and part.get("body") and part["body"].get("attachmentId"):
                            attachment_count += 1
                
                # Write extracted information to CSV
                writer.writerow({"From": from_email, "To": to_email, "Subject": subject, "Time": time, "Attachments": attachment_count})

                # Apply label "filters" to the message
                service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [filters_label_id]}).execute()

        print("Email information saved to 'emails.csv'.")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
