
# import os.path
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# def create_label(service, user_id, label_name):
#     """Create a new label."""
#     label = {"name": label_name}
#     try:
#         label = service.users().labels().create(userId=user_id, body=label).execute()
#         print("Label created: {}".format(label["name"]))
#     except HttpError as error:
#         print(f"An error occurred while creating label: {error}")

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

#     # Check if label "slack read" exists, if not, create it
#     labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
#     label_names = [label["name"] for label in labels]
#     if "Yatra test" not in label_names:
#         create_label(service, user_id, "Yatra test")

#     try:
#         # Get the user's messages
#         page_token = None
#         while True:
#             results = service.users().messages().list(userId=user_id, labelIds=["INBOX"], pageToken=page_token).execute()
#             messages = results.get("messages", [])
#             if not messages:
#                 print("No more messages.")
#                 break

#             print("Messages:")
#             for message in messages:
#                 msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
#                 headers = msg["payload"]["headers"]
#                 subject = next(header["value"] for header in headers if header["name"] == "Subject")
#                 # Check if message subject contains "[Slack] "
#                 if "TaxInvoice " in subject:
#                     # Copy message to label "slack read"
#                     service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": ["Label_2"]}).execute()
#                     print(f"Message with subject '{subject}' copied to 'slack read' label.")
#                 else:
#                     print(f"Message with subject '{subject}' does not contain 'TaxInvoice'.")
            
#             page_token = results.get("nextPageToken")
#             if not page_token:
#                 print("No more pages.")
#                 break

#     except HttpError as error:
#         print(f"An error occurred: {error}")

# if __name__ == "__main__":
#     main()


import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def create_label(service, user_id, label_name):
    """Create a new label."""
    label = {"name": label_name}
    try:
        label = service.users().labels().create(userId=user_id, body=label).execute()
        print("Label created: {}".format(label["name"]))
    except HttpError as error:
        print(f"An error occurred while creating label: {error}")

def get_label_id(service, user_id, label_name):
    """Get the ID of the specified label."""
    labels = service.users().labels().list(userId=user_id).execute().get("labels", [])
    for label in labels:
        if label["name"] == label_name:
            return label["id"]
    return None

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

    # Check if label "Yatra test" exists, if not, create it
    if not get_label_id(service, user_id, "Yatra test2"):
        create_label(service, user_id, "Yatra test2")

    label_id = get_label_id(service, user_id, "Yatra test2")

    try:
        # Get the user's messages
        page_token = None
        while True:
            results = service.users().messages().list(userId=user_id, labelIds=["INBOX"], pageToken=page_token).execute()
            messages = results.get("messages", [])
            if not messages:
                print("No more messages.")
                break

            print("Messages:")
            for message in messages:
                msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
                headers = msg["payload"]["headers"]
                subject = next(header["value"] for header in headers if header["name"] == "Subject")
                # Check if message subject contains "TaxInvoice"
                if "TaxInvoice " in subject:
                    # Copy message to label "Yatra test"
                    service.users().messages().modify(userId=user_id, id=message["id"], body={"addLabelIds": [label_id]}).execute()
                    print(f"Message with subject '{subject}' copied to 'Yatra test2' label.")
                else:
                    print(f"Message with subject '{subject}' does not contain 'TaxInvoice'.")
            
            page_token = results.get("nextPageToken")
            if not page_token:
                print("No more pages.")
                break

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
