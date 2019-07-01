import os
import uuid
import json
import sys
import glob


from blob_to_local import connectblobstorage,checkcontainerexists,downloadfromblob
from excel_to_csv_txt import csv_from_excel
from local_to_blob import uploadToBLOB,clearLocalPath
from blob_archive_file import archiveblob

def main():
    outputDict = {}
    processing_log = ''
    try:
        loc_dest = str(uuid.uuid4())
        local_dest_path = os.path.join(os.getcwd(), loc_dest)
        os.makedirs(loc_dest)


        read_linkedServices = open('linkedServices.json').read()
        json_linkedServices = json.loads(read_linkedServices)
        blob_connection_string = json_linkedServices[0]['properties']['typeProperties']['connectionString']

        read_activity = open('activity.json').read()
        json_activity = json.loads(read_activity)

        # Read extended property values into variables
        src_container = json_activity['typeProperties']['extendedProperties']['sourceContainer']
        outputDict['BlobContainer'] = src_container
        src_blob_location = json_activity['typeProperties']['extendedProperties']['excelSourcePath']
        outputDict['SourceBlobPath'] = src_blob_location

        
        filename = json_activity['typeProperties']['extendedProperties']['fileName']
        try:
            sheetname = json_activity['typeProperties']['extendedProperties']['sheetName']
        except Exception as e:
            sheetname = None
        outputFileDelimiter = json_activity['typeProperties']['extendedProperties']['outputFileDelimiter']
        try:
            skipHeaderRow = json_activity['typeProperties']['extendedProperties']['skipHeaderRow']
        except Exception as e:
            skipHeaderRow = 0
        try:
            skipTrailingRow = json_activity['typeProperties']['extendedProperties']['skipTrailingRow']
        except Exception as e:
            skipTrailingRow = 0

        dst_blob_location = json_activity['typeProperties']['extendedProperties']['uploadPath']
        outputDict['DestinationBlobPath'] = dst_blob_location
        archive_loc = json_activity['typeProperties']['extendedProperties']['excelArchivePath']
        outputDict['ArchiveBlobPath'] = archive_loc

        conn_src_blob_strg, connsrcblobstrgstatusmsg, connsrcblobstrgstatus = connectblobstorage(
            blob_connection_string, src_container)
        if connsrcblobstrgstatus == 'Failure':
            raise Exception(connsrcblobstrgstatusmsg)
        elif connsrcblobstrgstatus == 'Success':
            print(connsrcblobstrgstatusmsg)
            processing_log = processing_log + ' ' + connsrcblobstrgstatusmsg + ' -->'

        downloadedfilelist, downloadstatusmsg, dwnldfromblobstatus = downloadfromblob(conn_src_blob_strg, src_container, src_blob_location,
                                                                filename, loc_dest)
        if dwnldfromblobstatus == 'Failure':
            raise Exception(downloadstatusmsg)
        elif dwnldfromblobstatus == 'Success':
            print(downloadstatusmsg)
            outputDict['DownloadedFiles'] = downloadedfilelist
            processing_log = processing_log + ' ' + downloadstatusmsg + ' -->'
            

        convertedfilelist,csvstatusmsg, csvfromexcelstatus = csv_from_excel(loc_dest, filename, sheetname, outputFileDelimiter, skipHeaderRow, skipTrailingRow)
        if csvfromexcelstatus == 'Failure':
            raise Exception(csvstatusmsg)
        elif csvfromexcelstatus == 'Success':
            print(csvstatusmsg)
            outputdict['ConvertedFiles']= convertedfilelist
            processing_log = processing_log + ' ' + csvstatusmsg + ' -->'

        uploadedfilelist,uploadstatusmsg, uploadtoblobstatus = uploadToBLOB(src_container, conn_src_blob_strg,
                                                          dst_blob_location,local_dest_path)
        if uploadtoblobstatus == 'Failure':
            raise Exception(uploadstatusmsg)
        elif uploadtoblobstatus == 'Success':
            print(uploadstatusmsg)
            outputDict['UploadedFiles'] = uploadedfilelist
            processing_log = processing_log + ' ' + uploadstatusmsg + ' -->'



        archivedfilelist,archivestatusmsg, archiveblobstatus = archiveblob(conn_src_blob_strg, src_container, src_blob_location, filename,
                                                      archive_loc)

        if archiveblobstatus == 'Failure':
            raise Exception(archivestatusmsg)
        elif archiveblobstatus == 'Success':
            print(archivestatusmsg)
            outputDict['ArchivedFiles'] = archivedfilelist
            processing_log = processing_log + ' ' + archivestatusmsg

        clearlocalpathstatusmsg, clearlocalpathstatus = clearLocalPath(local_dest_path)
        if clearlocalpathstatus == 'Failure':
            raise Exception(clearlocalpathstatusmsg)
        elif clearlocalpathstatus == 'Success':
            print(clearlocalpathstatusmsg)

        os.rmdir(local_dest_path)

        outputDict['ProcessingLog'] = processing_log

        with open('outputs.json', 'w') as outfile:  # writing values to custom output
            json.dump(outputDict, outfile)


    except Exception as e:
        outputDict["Exception"] = str(e)
        with open('outputs.json', 'w') as outfilex:  # writing values to custom output
            json.dump(outputDict, outfilex)
        sys.exit(str(e))

main()