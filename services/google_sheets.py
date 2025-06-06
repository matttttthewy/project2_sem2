import aiohttp
import json
from google.oauth2 import service_account
import google.auth.transport.requests
from typing import Callable
from .convert_functions import convert_pricing, convert_room_capacities

# Базовый класс для работы с Google Sheets
class BasicGoogleSheetsAsyncClient:
    def __init__(self, creds_path: str, spreadsheet_id: str):
        self.creds_path = creds_path
        self.spreadsheet_id = spreadsheet_id
        self._access_token = None

    def _refresh_token(self):
        creds = service_account.Credentials.from_service_account_file(
            self.creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        creds.refresh(google.auth.transport.requests.Request())
        self._access_token = creds.token

    async def append_row(self, range_name: str, values: list):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}:append"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "valueInputOption": "USER_ENTERED"
        }
        body = {
            "values": [values],
            "majorDimension": "ROWS"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                return await resp.json()

    async def read_range(self, range_name: str):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}"
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                return await resp.json()
    
    async def get_all_sheets(self):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}"
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                data = await resp.json()
                sheets = data.get("sheets", [])
                return [sheet["properties"]["title"] for sheet in sheets]




class GoogleSheetsManager(BasicGoogleSheetsAsyncClient):
    def __init__(self, creds_path: str, spreadsheet_id: str):
        super().__init__(creds_path, spreadsheet_id)
    
    async def get_sheet_data(self, sheet_name: str, convert_function: Callable):
        sheet_data = await self.read_range(f"{sheet_name}")
        print(sheet_data)
        return convert_function(sheet_data["values"], sheet_name)


if __name__ == "__main__":
    async def main():
        client = GoogleSheetsManager(
            creds_path="google_credentials.json",
            spreadsheet_id="1lbaJHS02L1eY1VNXCHJx8HQuJZMFo_jZcn2g6LdD_Co"
        )
        
        sheet_data = await client.get_sheet_data("Прайс 2 мест", convert_pricing)
        date = input()
        print(sheet_data.get_price(date, True))

    import asyncio
    asyncio.run(main())