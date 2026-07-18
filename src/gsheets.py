import os
from pathlib import Path

from dotenv import load_dotenv
import config

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

PATHS = config.PATHS
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = PROJECT_ROOT / "token.json"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SAMPLE_RANGE_NAME = "Sheet1!A1"


class GoogleSheetsAuthenticationError(RuntimeError):
  """Raised when the saved Google credentials can no longer be used."""


def readText():
  data = []
  with open(PATHS["flight_data"], "r") as f:
    lines = f.readlines()
    for item in lines:
      data.append(item.split(','))
    f.close()
    return data


def get_credentials():
  creds = None

  if TOKEN_PATH.exists():
    try:
      creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    except (KeyError, TypeError, ValueError) as err:
      raise GoogleSheetsAuthenticationError(
          f"Could not read the saved Google token at {TOKEN_PATH}."
      ) from err

  if creds and creds.valid:
    return creds

  if creds and creds.expired and creds.refresh_token:
    try:
      creds.refresh(Request())
    except RefreshError as err:
      raise GoogleSheetsAuthenticationError(
          "Google rejected the saved refresh token."
      ) from err
  else:
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH, SCOPES
    )
    # This opens the user's browser and handles the OAuth callback locally.
    creds = flow.run_local_server(
        port=3000,
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

  TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
  return creds


def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = get_credentials()
  service = build("sheets", "v4", credentials=creds)

  # Call the Sheets API
  valueData = readText()
  sheet = service.spreadsheets()
  try:
    (
        sheet.values()
        .append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption="USER_ENTERED", body={"values": valueData})
        .execute()
    )
  except HttpError as err:
    if err.resp.status == 401:
      raise GoogleSheetsAuthenticationError(
          "Google Sheets rejected the saved credentials."
      ) from err
    raise

  print("Data exported to Google Sheets Successfully")


if __name__ == "__main__":
  main()
