import utils
import gspread
from oauth2client.service_account import ServiceAccountCredentials

folders = utils.list_folders_and_files()

# --- Configuration ---
SPREADSHEET_ID = "1sMwfSuQtPvOjp0IX5Fd5Mf_Hjhq3SjiShMrFzUw00Es"
CSV_FILE_PATH = "data.csv"  # Change this to your CSV file path

# --- Authenticate with Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("mtg-bigquery-data-fa3f617c4830.json", scope)
client = gspread.authorize(creds)

# --- Open Google Spreadsheet ---
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- Read CSV Data ---
for folder_path, files in folders.items():
    for file_name in files:
        file_path = f"{folder_path}\\{file_name}"

        utils.write_to_sheets(folder_path, file_path, spreadsheet)

print("✅ CSV data appended successfully to Google Sheets!")