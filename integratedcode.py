
# ################################################
# import os.path
# import base64
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from datetime import datetime
# import zipfile
# import io
# from collections import defaultdict
# import re
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

# def save_attachment(attachment_data, filename, folder_path):
#     """Save attachment to the specified folder."""
#     file_path = os.path.join(folder_path, filename)
#     if filename.lower().endswith('.zip'):
#         # If the attachment is a zip file, extract its contents
#         with zipfile.ZipFile(io.BytesIO(attachment_data)) as zip_ref:
#             zip_ref.extractall(folder_path)
#         print(f"Zip attachment '{filename}' extracted and saved to '{folder_path}'.")
#     else:
#         # Otherwise, save the attachment as is
#         with open(file_path, "wb") as f:
#             f.write(attachment_data)
#         print(f"Attachment '{filename}' saved to '{folder_path}'.")

# def get_label_id(service, user_id, label_name):
#     """Get the ID of the specified label."""
#     labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
#     for label in labels:
#         if label["name"] == label_name:
#             return label["id"]
#     return None

# def count_emails_per_day(service, user_id):
#     """Count the number of emails received per day."""
#     # Dictionary to store count of emails received per day
#     email_counts = defaultdict(int)

#     try:
#         # Get all messages from the mailbox
#         results = service.users().messages().list(userId=user_id).execute()
#         messages = results.get("messages", [])

#         # Iterate through each message and extract the date received
#         for message in messages:
#             msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
#             headers = msg["payload"]["headers"]
#             date = next((header["value"] for header in headers if header["name"] == "Date"), None)
#             if date:
#                 # Try parsing the date string using multiple formats
#                 for date_format in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
#                     try:
#                         dt = datetime.strptime(date, date_format)
#                         # Convert to UTC timezone for consistency
#                         dt = dt.astimezone(pytz.utc)
#                         day = dt.date()
#                         email_counts[day] += 1
#                         break  # Exit the loop if parsing succeeds
#                     except ValueError:
#                         pass  # Continue to the next format if parsing fails

#         # Print the counts of emails received per day
#         print("Emails received per day:")
#         for day, count in sorted(email_counts.items()):
#             print(f"{day}: {count} emails")

#     except HttpError as error:
#         print(f"An error occurred: {error}")

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
#     filters_label_id = get_label_id(service, user_id, "test2")
#     if not filters_label_id:
#         filters_label_id = create_label(service, user_id, "test2")
    
#     # Count emails per day
#     count_emails_per_day(service, user_id)

#     try:
#         # Define date range for filtering emails (May 13, 2024, to May 14, 2024)
#         start_date = datetime(2024, 5, 13).strftime('%Y/%m/%d')
#         end_date = datetime(2024, 5, 15).strftime('%Y/%m/%d')  # Note: We specify the day after the end date
#         query = f"after:{start_date} before:{end_date}"

#         # Get the user's messages filtered by date range
#         page_token = None
#         while True:
#             results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
#             messages = results.get("messages", [])
#             if not messages:
#                 print("No more messages.")
#                 break

#             print("Messages:")
#             for message in messages:
#                 msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
#                 headers = msg["payload"]["headers"]
#                 subject = next(header["value"] for header in headers if header["name"] == "Subject")
                
#                 # Apply label "filters" to the filtered messages
#                 service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [filters_label_id]}).execute()
#                 print(f"Message with subject '{subject}' filtered and labeled as 'filters'.")

#                 # Check if there are any attachments
#                 if "parts" in msg["payload"]:
#                     for part in msg["payload"]["parts"]:
#                         if part.get("filename") and part.get("body") and part["body"].get("attachmentId"):
#                             attachment = service.users().messages().attachments().get(
#                                 userId=user_id, messageId=message["id"], id=part["body"]["attachmentId"]
#                             ).execute()
#                             attachment_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
#                             filename = part["filename"]
#                             # Save attachment to a local folder named "attachments"
#                             save_attachment(attachment_data, filename, "attachments")
            
#             page_token = results.get("nextPageToken")
#             if not page_token:
#                 print("No more pages.")
#                 break

#     except HttpError as error:
#         print(f"An error occurred: {error}")

# if __name__ == "__main__":
#     main()
# # ######################################################


################################################
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import zipfile
import io
from collections import defaultdict
import re
import pytz

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

def get_label_id(service, user_id, label_name):
    """Get the ID of the specified label."""
    labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
    for label in labels:
        if label["name"] == label_name:
            return label["id"]
    return None

def count_emails_per_day(service, user_id, start_date, end_date):
    """Count the number of emails received per day within the specified date range."""
    # Dictionary to store count of emails received per day
    email_counts = defaultdict(int)

    try:
        # Define the query string for the date range
        query = f"after:{start_date} before:{end_date}"

        # Get all messages from the mailbox within the specified date range
        messages = []
        page_token = None

        while True:
            results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        # Iterate through each message and extract the date received
        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
            headers = msg["payload"]["headers"]
            date = next((header["value"] for header in headers if header["name"] == "Date"), None)
            if date:
                # Try parsing the date string using multiple formats
                for date_format in ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]:
                    try:
                        dt = datetime.strptime(date, date_format)
                        # Convert to UTC timezone for consistency
                        dt = dt.astimezone(pytz.utc)
                        day = dt.date()
                        email_counts[day] += 1
                        break  # Exit the loop if parsing succeeds
                    except ValueError:
                        pass  # Continue to the next format if parsing fails

        # Print the counts of emails received per day
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
                "/Users/finkraft/dev/GmailApi/client_secret_605315136561-t9ll05u1bpg2ctudm94u3crt69lr8kt0.apps.googleusercontent.com.json", SCOPES
            )
            creds = flow.run_local_server(port=54543)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    user_id = "me"
    
    # Check if label "filters" exists, if not, create it
    filters_label_id = get_label_id(service, user_id, "six")
    if not filters_label_id:
        filters_label_id = create_label(service, user_id, "six")
    
    # Count emails per day
    start_date = datetime(2024, 5, 13).strftime('%Y-%m-%d')
    end_date = datetime(2024, 5, 14).strftime('%Y-%m-%d')  # Note: We specify the day after the end date
    count_emails_per_day(service, user_id, start_date, end_date)

    try:
        # Define date range for filtering emails (May 13, 2024, to May 14, 2024)
        start_date = datetime(2024, 5, 13).strftime('%Y-%m-%d')
        end_date = datetime(2024, 5, 14).strftime('%Y-%m-%d')  # Note: We specify the day after the end date
        query = f"after:{start_date} before:{end_date}"

        # Get the user's messages filtered by date range
        page_token = None
        while True:
            results = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages = results.get("messages", [])
            if not messages:
                print("No more messages.")
                break

            print("Messages:")
            for message in messages:
                msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
                headers = msg["payload"]["headers"]
                subject = next(header["value"] for header in headers if header["name"] == "Subject")
                
                # Apply label "filters" to the filtered messages
                service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [filters_label_id]}).execute()
                print(f"Message with subject '{subject}' filtered and labeled as 'filters'.")

                # Check if there are any attachments
                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part.get("filename") and part.get("body") and part["body"].get("attachmentId"):
                            attachment = service.users().messages().attachments().get(
                                userId=user_id, messageId=message["id"], id=part["body"]["attachmentId"]
                            ).execute()
                            attachment_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                            filename = part["filename"]
                            # Save attachment to a local folder named "attachments"
                            save_attachment(attachment_data, filename, "attachments")
            
            page_token = results.get("nextPageToken")
            if not page_token:
                print("No more pages.")
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()

# ######################################################



