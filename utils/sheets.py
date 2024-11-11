import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsHelper:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.spreadsheet_id = "1_pBYksEt9uOoPLnNZs-ZIlQ0C1ECfuCTZhIswjmMb7A"
        self.range_name = "bierliste!A2:B"
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.creds = None
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def upload_to_sheets(self, values):
        try:
            service = build("sheets", "v4", credentials=self.creds)
            body = {"values": values}

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .update(spreadsheetId=self.spreadsheet_id,
                    range=self.range_name,
                    valueInputOption="RAW",
                    body=body,)
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
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
            return result.get("values", [])
        except HttpError as err:
            print(err)

