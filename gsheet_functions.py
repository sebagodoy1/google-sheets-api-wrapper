import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread.utils import ValueInputOption
from datetime import datetime
from typing import Optional, List, Any

class GoogleSheetsFunctions:
    """
    Wrapper to interact with Google Sheets using service account credentials.
    """
    def __init__(self, credentials_file: str, sheet_name: str):
        """
        Args:
            credentials_file: Name of the JSON file (must be in the same directory)
            sheet_name: Name of the spreadsheet in Google Drive
        """
        script_dir = os.path.dirname(os.path.realpath(__file__))
        key_path = os.path.join(script_dir, credentials_file)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name)

    def get_worksheet(self, index: int = 0) -> gspread.Worksheet:
        """Gets a worksheet by index (0 by default)"""
        return self.sheet.get_worksheet(index)

    def clear_sheet(self, worksheet: gspread.Worksheet) -> None:
        """Clears all data from A2 to the end of the sheet"""
        existing_data = worksheet.get_all_values()
        if not existing_data:
            return
        num_cols = len(existing_data[0])
        last_col_letter = gspread.utils.rowcol_to_a1(1, num_cols).replace('1', '')
        range_to_clear = f'A2:{last_col_letter}'
        worksheet.batch_clear([range_to_clear])

    def append_from_last_row(self, worksheet: gspread.Worksheet, df: pd.DataFrame) -> None:
        """Appends rows to the end of the sheet"""
        existing_rows = len(worksheet.get_all_values())
        data_to_append = df.values.tolist()
        worksheet.insert_rows(data_to_append, row=existing_rows + 1, value_input_option=ValueInputOption.user_entered)

    def update_worksheet(self, worksheet: gspread.Worksheet, df: pd.DataFrame,
                         clear_existing: bool = False, update_cell: str = 'J2') -> None:
        """
        Updates the sheet: if clear_existing=True it replaces everything from A2,
        otherwise it appends to the end. Also writes the update date.
        """
        data_to_insert = df.values.tolist()
        if clear_existing:
            existing_data = worksheet.get_all_values()
            if existing_data:
                num_cols = len(existing_data[0])
                last_col_letter = gspread.utils.rowcol_to_a1(1, num_cols).replace('1', '')
                worksheet.batch_clear([f'A2:{last_col_letter}'])
            worksheet.update('A2', data_to_insert, value_input_option='USER_ENTERED')
        else:
            start_row = len(worksheet.get_all_values()) + 1
            worksheet.update(f'A{start_row}', data_to_insert, value_input_option='USER_ENTERED')

        now = datetime.now().strftime("%d/%m/%Y")
        worksheet.update(update_cell, [[f"Updated on {now}"]])
