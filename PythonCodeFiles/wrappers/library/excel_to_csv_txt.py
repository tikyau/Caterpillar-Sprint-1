import os
import sys
import fnmatch
import xlrd
import csv
import datetime
from datetime import time

#Function to convert excel files to txt/csv files
def csv_from_excel(loc_dest, filename, sheetname, delimiter, skip_starting_rows, skip_footer_rows):
    try:
        loc_dest_path = os.path.join(os.getcwd(),loc_dest)
        file_names = filename.split(',')
        returnFileList = []
        for Dir_File in os.listdir(loc_dest_path):

            for file_pattern in file_names:
                if not os.path.isdir(os.path.join(loc_dest_path,Dir_File)):
                    if fnmatch.fnmatch(Dir_File.lower(), file_pattern.strip().lower()):
                        if Dir_File.endswith('.xls') or Dir_File.endswith('.xlsx'):
                            print('converting ' + Dir_File + " at location - " + loc_dest_path)
                            excel_file_path = os.path.join(loc_dest_path,Dir_File)

                            wb = xlrd.open_workbook(excel_file_path)
                            if sheetname is not None and sheetname.strip() != '':
                                sh = wb.sheet_by_name(sheetname)
                            elif sheetname is None or sheetname.strip() == '':
                                sh = wb.sheet_by_index(0)
                            name, ext = os.path.splitext(Dir_File)
                            if delimiter == ',':
                                extension = '.csv'
                            else:
                                extension = '.txt'
                            csv_file_name = name+extension
                            csv_file_path = os.path.join(loc_dest_path,csv_file_name)
                            if sys.version_info[0] < 3:
                                csv_file = open(csv_file_path, 'wb')
                            else:
                                csv_file = open(csv_file_path, 'w', newline='',encoding='utf-8')
                            try:
                                wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL, delimiter=str(delimiter))
                            except Exception as e:
                                if str(e) == '"delimiter" must be an 1-character string':
                                    wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL, delimiter='\t')
                            for rownum in range(int(skip_starting_rows), int(sh.nrows)-int(skip_footer_rows)):
                                excel_row = []
                                colindex = 0
                                for colnum in range(0, sh.ncols):
                                
                                    # Handling Newline character in the header
                                    if rownum == int(skip_starting_rows) and "\n" in sh.cell(rownum, colnum).value:
                                        excel_column_value = sh.cell(rownum, colnum).value.replace("\n", "")

                                    # Check if header column name is empty, if so assign a name
                                    elif rownum == int(skip_starting_rows) and sh.cell(rownum, colnum).value == "":
                                        excel_column_value = "Column" + str(colindex)
                                        colindex += 1

                                    # Removes all leading and trailing whitespaces
                                    elif rownum == int(skip_starting_rows) and sh.cell(rownum, colnum).value != '':
                                        excel_column_value = sh.cell(rownum, colnum).value.strip()

                                    elif sh.cell(rownum, colnum).ctype == xlrd.XL_CELL_DATE:
                                        try:
                                            excel_column_value = str(datetime.datetime(
                                                *xlrd.xldate_as_tuple(sh.cell(rownum, colnum).value, wb.datemode)))
                                        except:
                                            date_values = xlrd.xldate_as_tuple(sh.cell(rownum, colnum).value,
                                                                               wb.datemode)
                                            excel_column_value = time(*date_values[3:])

                                    elif sh.cell(rownum, colnum).ctype == xlrd.XL_CELL_NUMBER:
                                        if sh.cell(rownum, colnum).value.is_integer():
                                            excel_column_value = int(sh.cell(rownum, colnum).value)
                                        else:
                                            excel_column_value = sh.cell(rownum, colnum).value

                                    elif sh.cell(rownum, colnum).ctype == xlrd.XL_CELL_ERROR:
                                        excel_column_value = xlrd.error_text_from_code[sh.cell(rownum, colnum).value]

                                    else:
                                        if sys.version_info[0] < 3:
                                            excel_column_value = sh.cell(rownum, colnum).value.encode('utf-8')
                                        else:
                                            excel_column_value = sh.cell(rownum, colnum).value

                                    excel_row.append(excel_column_value)

                                wr.writerow(excel_row)
                            returnFileList.append(csv_file_name)
                            os.remove(excel_file_path)
        return returnFileList,'Excel to csv file conversion successful!!!', 'Success'
    except Exception as e:
        if fnmatch.fnmatch(str(e), '*Unsupported format, or corrupt file: Expected BOF record;*'):
            pass
        else:
            return None,'Error converting Excel to csv :' + str(e), 'Failure'

