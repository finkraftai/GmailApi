import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "/Users/finkraft/dev/GmailApi/client_secret_605315136561-t9ll05u1bpg2ctudm94u3crt69lr8kt0.apps.googleusercontent.com.json", SCOPES
      )
      creds = flow.run_local_server(port=54543)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())


  try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # Get the user's messages
        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        print("Messages:")
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            # print(msg)
            print("Message snippet: {}".format(msg["snippet"]))

  except HttpError as error:
        # Handle errors from Gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()