import csv
import os
from pathlib import Path

from dotenv import load_dotenv
import config

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

PATHS = config.PATHS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVICE_ACCOUNT_PATH = PROJECT_ROOT / "flightdata-service-account.json"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_RANGE = "Sheet1!A1"


class GoogleSheetsConfigurationError(RuntimeError):
  """Raised when Sheets or service-account configuration is incomplete."""


def read_flight_data():
  with open(PATHS["flight_data"], "r", newline="", encoding="utf-8") as file:
    return list(csv.reader(file))


def get_credentials():
  configured_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
  credentials_path = (
      Path(configured_path).expanduser()
      if configured_path
      else DEFAULT_SERVICE_ACCOUNT_PATH
  )

  if not credentials_path.is_absolute():
    credentials_path = PROJECT_ROOT / credentials_path

  if not credentials_path.is_file():
    raise GoogleSheetsConfigurationError(
        "Service-account credentials were not found at "
        f"{credentials_path}. Set GOOGLE_APPLICATION_CREDENTIALS to the "
        "service-account JSON file."
    )

  try:
    return service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES,
    )
  except (OSError, ValueError) as err:
    raise GoogleSheetsConfigurationError(
        f"Could not load service-account credentials from {credentials_path}."
    ) from err


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
      service_account_email = getattr(creds, "service_account_email", "unknown")
      raise GoogleSheetsConfigurationError(
          "Google Sheets could not access the configured spreadsheet. Confirm "
          "that SPREADSHEET_ID is correct, the Sheets API is enabled, and the "
          f"spreadsheet is shared with {service_account_email} as an Editor."
      ) from err
    raise

  print("Data exported to Google Sheets Successfully")


if __name__ == "__main__":
  main()
