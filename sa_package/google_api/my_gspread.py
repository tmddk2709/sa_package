from __future__ import annotations

import re
import json
import gspread
import pandas as pd

from gspread.exceptions import APIError, WorksheetNotFound

from googleapiclient.discovery import build

from oauth2client.service_account import ServiceAccountCredentials


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
                print("gserviceaccount에 액세스 권한이 필요합니다")

            elif err.args[0]["code"] == 404:
                print("잘못된 시트 ID 입니다")

        except Exception as e:
            print(e)


    def get_sheet_id(self):

        return self.__sh_id

    def get_creds(self):

        return self.__creds

    def get_spreadsheet(self):

        return self.__spreadsheet



    def worksheet_exists(self, worksheet_name:str) -> bool|None:

        """
        check whether a worksheet exists or not with the worksheet name
        """

        try:
            _ = self.__spreadsheet.worksheet(worksheet_name)
            return True
        
        except WorksheetNotFound:
            return False
        
        except Exception as e:
            print(e)
            return None


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

        # 시트가 없는 경우
        if not self.worksheet_exists(worksheet_name=worksheet_name):
            
            print(f"{self.get_worksheet.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")

            if if_not_exist == "fail":
                return None
            
            # 새로 워크시트 생성
            else:
                _ = self.create_worksheet(worksheet_name)
        

        return self.__spreadsheet.worksheet(worksheet_name)



    def get_all_worksheets(self):

        return self.__spreadsheet.worksheets()
    


    def create_worksheet(self, worksheet_name:str, row_count:int=1000, col_count:int=10, index:int=0, hidden:bool=False, frozen_row_count:int=None, frozen_column_count:int=None):
        """
        새 워크시트 만들기
        """

        if self.worksheet_exists(worksheet_name=worksheet_name):
            print(f"{self.create_worksheet.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 이미 존재합니다")
            return None


        service = build("sheets", "v4", credentials=self.get_creds())

        # set grid properties
        grid_properties = {
            "rowCount":row_count,
            "columnCount":col_count
        }
        if frozen_row_count is not None:
            grid_properties["frozenRowCount"] = frozen_row_count

        if frozen_column_count is not None:
            grid_properties["frozenColumnCount"] = frozen_column_count


        request_body = {
            "requests": [{
                "addSheet": {
                    "properties": {
                        "title": worksheet_name,
                        "index": index,
                        "hidden": hidden,
                        "gridProperties": grid_properties,
                    }
                }
            }]
        }

        sheet = service.spreadsheets()
        response = sheet.batchUpdate(
            spreadsheetId=self.get_sheet_id(),
            body=request_body
        ).execute()

        return response



    def duplicate_worksheet(self, worksheet_name, dup_sheet_name):
        """
        기존 워크시트 복제하기
        """
        
        # 복제할 시트가 없는 경우
        if not self.worksheet_exists(worksheet_name=dup_sheet_name):
        
            print(f"{self.duplicate_worksheet.__qualname__} 실패 :: <{dup_sheet_name}> 이름의 시트가 존재하지 않습니다")
            return None
        
        # 결과 시트 이름이 이미존재하는 경우
        if self.worksheet_exists(worksheet_name=worksheet_name):

            print(f"{self.duplicate_worksheet.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 이미 존재합니다")
            return None


        dup_worksheet = self.get_worksheet(worksheet_name=dup_sheet_name)

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



    def delete_worksheet(self, worksheet_name):

        if not self.worksheet_exists(worksheet_name=worksheet_name):
            print(f"{self.delete_worksheet.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None
        

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


    
    def update_worksheet_properties(self, worksheet_name, properties):
        """
        워크시트 속성 변경하기
        """

        if not self.worksheet_exists(worksheet_name=worksheet_name):
            print(f"{self.update_worksheet_properties.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None


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



    def set_cell_format(self, worksheet_name:str, set_range:str, fontfamily:str=None, fontsize:int=None, bold:bool=None, italic:bool=None, color:dict=None, horizontal_alignment:str=None, vertical_alignment:str=None, wrap_strategy:str=None, number_format:str=None, number_pattern:str=None, background_color:dict=None):

        """
        Parameter
        ---------

        color : dict type
            {
                "red":int,
                "blue":int,
                "green":int
            }

        horizontal_alignment : {"LEFT", "RIGHT", "CENTER"}

        vertical_alignment : {"TOP", "MIDDLE", "BOTTOM"}

        wrap_strategy : {"OVERFLOW_CELL", "LEGACY_WRAP", "CLIP", "WRAP"}

        number_Format : {"TEXT", "NUMBER", "PERCENT", "CURRENCY", "DATE", "TIME", "DATE_TIME", "SCIENTIFIC"}

        background_color : dict type
            {
                "red":int,
                "blue":int,
                "green":int
            }
        """


        if not self.worksheet_exists(worksheet_name=worksheet_name):
            print(f"{self.set_cell_format.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None


        worksheet = self.get_worksheet(worksheet_name=worksheet_name)

        body = {}

        ## textFormat
        text_format = {}
        if fontfamily is not None:
            text_format["fontFamily"] = fontfamily

        if fontsize is not None:
            text_format["fontSize"] = fontsize

        if bold is not None:
            text_format["bold"] = bold
        
        if italic is not None:
            text_format["italic"] = italic

        if color is not None:
            text_format["foregroundColorStyle"] = {"rgbColor":color}

        if len(text_format) > 0:
            body["textFormat"] = text_format


        if horizontal_alignment is not None:
            body["horizontalAlignment"] = horizontal_alignment

        if vertical_alignment is not None:
            body["verticalAlignment"] = vertical_alignment

        if wrap_strategy is not None:
            body["wrapStrategy"] = wrap_strategy

        if number_format is not None:
            body["numberFormat"] = {
                "type":number_format,
                "pattern":number_pattern
                }

        if background_color is not None:
            body["backgroundColorSyle"] = {"rgbColor":background_color}
        

        worksheet.format(
            set_range,
            format=body
        )



    def append_rows(self, worksheet_name:str, append_row_num:int):

        if not self.worksheet_exists(worksheet_name=worksheet_name):
            print(f"{self.update_worksheet_properties.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None

        worksheet = self.get_worksheet(worksheet_name=worksheet_name)
        worksheet.add_rows(append_row_num)



    def write_values_to_sh(self, values, worksheet_name:str, start_cell:str, if_not_exist:str="fail"):

        """
        Parameter
        ----------
        
        if_not_exist: {"create", "fail"}

            How to behave if the worksheet named 'worksheet_name' is not exist
            - create : create a new worksheet named 'worksheet_name' and write values to it
            - fail : raise a ValueError
            default value is "fail"
        """

        assert if_not_exist in ["create", "fail"], "if_not_exist에 잘못된 값 입력 / create, fail 중 하나로 입력해주세요"

        if not self.worksheet_exists(worksheet_name=worksheet_name):

            if if_not_exist == "fail":
                print(f"{self.write_values_to_sh.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
                return None
            
            else:
                
                print(f"<{worksheet_name}> 이름의 시트가 존재하지 않습니다")
                self.create_worksheet(worksheet_name=worksheet_name)
                print(f"<{worksheet_name}> 시트 생성 완료")
        


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



    def write_df_to_sh(self, df, worksheet_name, include_header=False, start_cell=None, date_columns=[], datetime_columns=[], to_str_columns=[], if_not_exist:str="fail"):
        """
        write data to worksheet of which name is "worksheet_name"
        데이터 프레임 구글 시트에 기록하기

        Parameter
        ----------
        
        if_not_exist: {"create", "fail"}

            How to behave if the worksheet named 'worksheet_name' is not exist
            - create : create a new worksheet named 'worksheet_name' and write values to it
            - fail : raise a ValueError
            default value is "fail"
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

            response = self.write_values_to_sh(values, worksheet_name, start_cell, if_not_exist=if_not_exist)
            return response

        except Exception as e:
            print(e)



    def clear_values(self, worksheet_name:str, clear_range:str):

        if not self.worksheet_exists(worksheet_name=worksheet_name):

            print(f"{self.clear_values.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None
        
        service = build("sheets", "v4", credentials=self.get_creds())
        sheet = service.spreadsheets()

        response = sheet.values().clear(
            spreadsheetId=self.get_sheet_id(), 
            range=f"{worksheet_name}!{clear_range}"
            ).execute()
        
        return response
        


    def get_df_from_gspread(self, worksheet_name:str, read_range:str, header:list=None):

        if not self.worksheet_exists(worksheet_name=worksheet_name):

            print(f"{self.get_df_from_gspread.__qualname__} 실패 :: <{worksheet_name}> 이름의 시트가 존재하지 않습니다")
            return None
        

        service = build("sheets", "v4", credentials=self.get_creds())
        sheet = service.spreadsheets()

        response = sheet.values().get(
            spreadsheetId=self.get_sheet_id(),
            range=f"{worksheet_name}!{read_range}"
        ).execute()
        values = response.get("values", [])


        if not values:
            print("데이터가 존재하지 않습니다")
            return None

        if header is None:
            df = pd.DataFrame(columns=values[0], data=values[1:])
        else:
            df = pd.DataFrame(columns=header, data=values)

        return df




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



