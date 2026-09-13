import csv
import config

import google.auth
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


PATHS = config.PATHS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = config.SPREADSHEET_ID
SHEET_RANGE = "Sheet1!A1"


class GoogleSheetsConfigurationError(RuntimeError):
  """Raised when Sheets or service-account configuration is incomplete."""


def read_flight_data():
  with open(PATHS["flight_data"], "r", newline="", encoding="utf-8") as file:
    return list(csv.reader(file))


def get_credentials():
  try:
    credentials, _ = google.auth.default(scopes=SCOPES)
    return credentials
  except DefaultCredentialsError as exc:
    raise GoogleSheetsConfigurationError(   
      "Google credentials were not found. On Google Cloud, attach a "
      "service account to the VM. For local development, configure ADC "
      "or set GOOGLE_APPLICATION_CREDENTIALS."
    ) from exc


def main():
  """Append the latest flight observations to the configured Google Sheet."""
  if not SPREADSHEET_ID:
    raise GoogleSheetsConfigurationError(
      "SPREADSHEET_ID is not configured in the environment."
    )

  creds = get_credentials()
  service = build("sheets", "v4", credentials=creds)

  value_data = read_flight_data()
  sheet = service.spreadsheets()
  try:
    (
    sheet.values()
      .append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption="USER_ENTERED",
        body={"values": value_data},
    )
      .execute()
    )
  except HttpError as err:
    if err.resp.status in (401, 403, 404):
      raise GoogleSheetsConfigurationError(
        "Google Sheets could not access the spreadsheet. Confirm that "
        "SPREADSHEET_ID is correct, the Sheets API is enabled, and the "
        "spreadsheet is shared with "
        "flightscript-sheets-writer@flightdata-465603."
        "iam.gserviceaccount.com as an Editor."
      ) from err
    raise

  print("Data exported to Google Sheets Successfully")


if __name__ == "__main__":
  main()
