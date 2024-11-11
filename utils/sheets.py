import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsHelper:
    def __init__(self, sheets_id, creds_path, token_path):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.spreadsheet_id = sheets_id
        self.range_name = "bierliste!A2:B"
        token_path = token_path
        creds_path = creds_path
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.creds = None
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, self.scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())

    def upload_to_sheets(self, values_d):
        try:
            service = build("sheets", "v4", credentials=self.creds)
            body = {"values": [[name, value] for name, value in values_d.items()]}

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .update(spreadsheetId=self.spreadsheet_id,
                    range=self.range_name,
                    valueInputOption="RAW",
                    body=body,)
                .execute()
            )
            print("Uploaded to sheets!")
        except HttpError as err:
            print(err)

    def dowload_from_sheets(self):
        try:
            service = build("sheets", "v4", credentials=self.creds)

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=self.range_name)
                .execute()
            )
            values = result.get("values", [])
            print("Downloaded values from sheets...")
            return {name : int(value) for name, value in values}
        except HttpError as err:
            print(err)

