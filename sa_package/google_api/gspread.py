import re
import gspread
import pandas as pd

from gspread.exceptions import APIError, WorksheetNotFound

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from urllib.error import HTTPError

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


class GspreadConnection:

    def __init__(self, key_path, scope=scope):
        self.__scope = scope
        self.__creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, self.__scope)

    
    def get_spreadsheet(self, sh_id):
        """
        스프레드시트 아이디로 스프레드시트 불러오기
        """
        return SpreadSheet(sh_id, self.__creds)



class SpreadSheet:

    def __init__(self, sh_id, creds):
        self.__sh_id = sh_id
        self.__creds = creds

        try:
            self.__spreadsheet = gspread.authorize(creds).open_by_key(sh_id)

        except APIError as err:

            if err.args[0]["code"] == 403:
                print(err.args[0]["message"])
                print("gserviceaccount에 액세스 권한이 필요합니다")

            elif err.args[0]["code"] == 404:
                print(err.args[0]["message"])
                print("잘못된 시트 ID 입니다")

        except Exception as e:
            print(e)


    def get_sheet_id(self):

        return self.__sh_id

    def get_creds(self):

        return self.__creds

    def get_spreadsheet(self):

        return self.__spreadsheet


    def get_worksheet(self, worksheet_name, if_not_exist:str="fail"):
        """
        구글 스프레드시트 워크시트 이름으로 워크시트 불러오기
        
        Parameter
        ----------
        
        if_not_exist: {"create", "fail"}

            How to behave if the worksheet named 'worksheet_name' is not exist
            - create : create a new worksheet named 'worksheet_name' and write values to it
            - fail : raise a ValueError
            default value is "fail"
        
        """

        assert if_not_exist in ["create", "fail"], "if_not_exist에 잘못된 값 입력 / create, fail 중 하나로 입력해주세요"

        try:
            worksheet = self.__spreadsheet.worksheet(worksheet_name)
            
        # 시트가 없는 경우
        except WorksheetNotFound:

            if if_not_exist == "fail":
                print(f"<{worksheet_name}> 이름의 시트가 존재하지 않습니다")
                worksheet = None
            
            else:
                print(f"<{worksheet_name}> 이름의 시트가 존재하지 않습니다")

                _ = self.create_worksheet(worksheet_name)
                worksheet = self.__spreadsheet.worksheet(worksheet_name)

        except Exception as e:
            print(e)
            worksheet = None

        return worksheet



    def create_worksheet(self, worksheet_name):
        """
        새 워크시트 만들기
        """
        try:
            service = build("sheets", "v4", credentials=self.get_creds())
            request_body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": worksheet_name,
                        }
                    }
                }]
            }

            sheet = service.spreadsheets()
            response = sheet.batchUpdate(
                spreadsheetId=self.get_sheet_id(),
                body=request_body
            ).execute()

            print(f"시트 <{worksheet_name}>가 생성되었습니다")
            return response

        except Exception as e:
            print(e)


    def duplicate_worksheet(self, worksheet_name, dup_sheet_name):
        """
        기존 워크시트 복제하기
        """

        try:
            dup_worksheet = self.get_worksheet(dup_sheet_name)

            service = build("sheets", "v4", credentials=self.get_creds())
            request_body = {
                "requests": [{
                    "duplicateSheet": {
                        "sourceSheetId": dup_worksheet.id,
                        "newSheetName": worksheet_name,
                    }
                }]
            }

            sheet = service.spreadsheets()
            response = sheet.batchUpdate(
                spreadsheetId=self.get_sheet_id(),
                body=request_body
            ).execute()
            return response

        except Exception as e:
            print(e)


    def delete_worksheet(self, worksheet_name):
        
        try:
            worksheet = self.get_worksheet(worksheet_name)

            service = build("sheets", "v4", credentials=self.get_creds())
            request_body = {
                "requests": [{
                    "deleteSheet": {
                        "sheetId": worksheet.id
                    }
                }]
            }

            sheet = service.spreadsheets()
            response = sheet.batchUpdate(
                spreadsheetId=self.get_sheet_id(),
                body=request_body,
            ).execute()
            return response

        except Exception as e:
            print(e)

    
    def update_worksheet_properties(self, worksheet_name, properties):
        """
        워크시트 속성 변경하기
        """
        try:
            worksheet = self.get_worksheet(worksheet_name)

            service = build("sheets", "v4", credentials=self.get_creds())
            properties.update({
                "sheetId": worksheet.id
            })

            request_body = {
                "requests": [{
                    "updateSheetProperties": {
                        "properties": properties,
                        'fields': (",").join(list(properties.keys()))
                    }
                }]
            }

            sheet = service.spreadsheets()
            response = sheet.batchUpdate(
                spreadsheetId=self.get_sheet_id(),
                body=request_body,
            ).execute()
            return response

        except Exception as e:
            print(e)


    def write_values_to_sh(self, values, worksheet_name, start_cell):

        try:
            service = build("sheets", "v4", credentials=self.get_creds())
            sheet = service.spreadsheets()

            request_body = {
                "values":values
            }
            response = sheet.values().update(
                spreadsheetId=self.get_sheet_id(),
                range=f"{worksheet_name}!{start_cell}",
                valueInputOption="USER_ENTERED",
                body=request_body,
            ).execute()

            return response

        except Exception as e:
            print(e)


    def write_df_to_sh(self, df, worksheet_name, include_header=False, start_cell=None, date_columns=[], datetime_columns=[], to_str_columns=[]):
        """
        write data to worksheet of which name is "worksheet_name"
        데이터 프레임 구글 시트에 기록하기
        """

        df = df.fillna("")
        
        for col in date_columns:
            df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d"))
        
        for col in datetime_columns:
            df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))

        for col in to_str_columns:
            df[col] = df[col].astype(str)
            
        try:
            if include_header:
                values = [df.columns.tolist()] + df.values.tolist()
                if start_cell is None:
                    start_cell = "A1"

            else:
                values = df.values.tolist()
                if start_cell is None:
                    start_cell = "A2"

            response = self.write_values_to_sh(values, worksheet_name, start_cell)
            return response

        except Exception as e:
            print(e)


    def clear_values(self, worksheet_name, clear_range):

        try:
            service = build("sheets", "v4", credentials=self.get_creds())
            sheet = service.spreadsheets()
        except Exception as e:
            print(e)

        try:
            response = sheet.values().clear(spreadsheetId=self.get_sheet_id(), range=f"{worksheet_name}!{clear_range}").execute()
            return response
        except Exception as e:
            print(e)


    def get_df_from_gspread(self, worksheet_name, read_range, header=None):

        try:
            service = build("sheets", "v4", credentials=self.get_creds())
            sheet = service.spreadsheets()

            response = sheet.values().get(
                spreadsheetId=self.get_sheet_id(),
                range=f"{worksheet_name}!{read_range}"
            ).execute()
            values = response.get("values", [])

            if not values:
                print("No data found.")
                return None

            if header is None:
                df = pd.DataFrame(columns=values[0], data=values[1:])
            else:
                df = pd.DataFrame(columns=header, data=values)
            return df

        except Exception as e:
            print(e)
            return None


def convert_column_alphabet_to_num(col_alphabet):
    """
    A : 1
    """
    
    digit = 0
    col_num = 0

    for x in col_alphabet[::-1]:
        col_num += (ord(x) - 64) * (26 ** digit)
        digit += 1

    return col_num


def convert_alphabet_range_to_num_index(alphabet_range):

    alphabet_regex = re.compile("[A-Z]")
    number_reges = re.compile("[0-9]")

    start_range, end_range = alphabet_range.split(":")

    start_col = "".join(alphabet_regex.findall(start_range))
    start_col = convert_column_alphabet_to_num(start_col)-1

    start_row = int("".join(number_reges.findall(start_range))) - 1

    end_col = "".join(alphabet_regex.findall(end_range))
    end_col = None if len(end_col) == 0 else convert_column_alphabet_to_num(end_col) 
    end_row = "".join(number_reges.findall(end_range))
    end_row = None if len(end_row) == 0 else int(end_row)

    return start_col, start_row, end_col, end_row

