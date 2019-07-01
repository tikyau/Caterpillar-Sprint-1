import os
import uuid
import json
import sys
import fnmatch

from blob_to_local import connectblobstorage,checkcontainerexists,downloadfromblob,listFilesOnBlob
from excel_to_csv_txt import csv_from_excel
from local_to_blob import uploadToBLOB,clearLocalPath
from file_processing import process_files

def main():
    outputDict = {}
    processing_log = ''
    try:
        #Create a local directory for file processing
        loc_dest = str(uuid.uuid4())
        local_dest_path = os.path.join(os.getcwd(), loc_dest)
        os.makedirs(loc_dest)


        read_linkedServices = open('linkedServices.json').read()
        json_linkedServices = json.loads(read_linkedServices)
        blob_connection_string = json_linkedServices[0]['properties']['typeProperties']['connectionString']

        read_activity = open('activity.json').read()
        json_activity = json.loads(read_activity)

        read_datasets = open('datasets.json').read()
        json_datasets = json.loads(read_datasets)

        for i in range(len(json_datasets)):
            if json_datasets[i]['properties']['type'] == 'AzureBlob':
                datasetIndex = i

        # read BlobContainer,BlobPath,File Name from datasets.json
        folderPath = json_datasets[datasetIndex]['properties']['typeProperties']['folderPath']
        container_name = folderPath.split('/')[datasetIndex]
        src_blob_location = folderPath.replace(container_name + "/", "")
        try:
            file_name = json_datasets[datasetIndex]['properties']['typeProperties']['fileName']
        except:
            file_name = None


        # Read extended property values into variables
        try:
            dst_blob_location = json_activity['typeProperties']['extendedProperties']['BlobFileUploadPath']
        except:
            dst_blob_location = src_blob_location
        
        #inputFileDelimiter is file delimiter used in input file
        inputFileDelimiter = json_activity['typeProperties']['extendedProperties']['inputFileDelimiter']
        try:
            skipTrailingRow = json_activity['typeProperties']['extendedProperties']['skipTrailingRow']
        except Exception as e:
            skipTrailingRow = 0

        try:
            sheetName = json_activity['typeProperties']['extendedProperties']['sheetName']
        except Exception as e:
            sheetName = None

        try:
            skipHeaderRow = json_activity['typeProperties']['extendedProperties']['skipHeaderRow']
        except Exception as e:
            skipHeaderRow = 0

        #Connect to BLOB storage
        conn_src_blob_strg, connsrcblobstrgstatusmsg, connsrcblobstrgstatus = connectblobstorage(
            blob_connection_string, container_name)
        if connsrcblobstrgstatus == 'Failure':
            raise Exception(connsrcblobstrgstatusmsg)

        processing_log = processing_log + ' ' + connsrcblobstrgstatusmsg + ' -->'

        #Filter files on BLOB matching the input file_name
        blob_file_list,statusMsg,status = listFilesOnBlob(conn_src_blob_strg,container_name,src_blob_location,file_name)

        if status =='Failure':
            raise Exception(statusMsg)


        raw_files_list = []
        converted_files_list =[]
        raw_files_to_archive = []

        #Process filtered files one by one from BLOB
        for blobFile in blob_file_list:

                #Download file from blob source path to local folder for further processing
                downloadedfilelist, downloadstatusmsg, dwnldfromblobstatus = downloadfromblob(conn_src_blob_strg, container_name,
                                                                                              src_blob_location,
                                                                                              blobFile, loc_dest)
                if dwnldfromblobstatus == 'Failure':
                    raise Exception(downloadstatusmsg)
                elif dwnldfromblobstatus == 'Success':
                    print(downloadstatusmsg)
                    processing_log = processing_log + ' ' + downloadstatusmsg + " ("+",".join(downloadedfilelist)+")"+" -->"

                #Process file based on its type (.xlsx/.xls/.csv/.zip/.txt)
                rawFileName,processed_files_list,archiveFileList,statusMsg,status = process_files(local_dest_path,blobFile,inputFileDelimiter,sheetName,skipHeaderRow,
                                  skipTrailingRow,local_dest_path)

                if status == 'Failure':
                    raise Exception(statusMsg)

                #rawFileName is original file name that has been processed
                raw_files_list.append(rawFileName)

                #converted_files_list is the list of converted files
                for fname in processed_files_list.split(","):
                    converted_files_list.append(fname)
                #raw_files_to_archive is the list of original files to be archived
                for fname in archiveFileList.split(","):
                    raw_files_to_archive.append(fname)


                #upload converted files to BLOB
                blobFileList,uploadstatusmsg, uploadtoblobstatus = uploadToBLOB(container_name, conn_src_blob_strg,
                                                                   dst_blob_location, local_dest_path)
                if uploadtoblobstatus == 'Failure':
                    raise Exception(uploadstatusmsg)
                elif uploadtoblobstatus == 'Success':
                    print(uploadstatusmsg)
                    processing_log = processing_log + ' ' + uploadstatusmsg +" -->"

                clearlocalpathstatusmsg, clearlocalpathstatus = clearLocalPath(local_dest_path)
                if clearlocalpathstatus == 'Failure':
                    raise Exception(clearlocalpathstatusmsg)
                elif clearlocalpathstatus == 'Success':
                    print(clearlocalpathstatusmsg)
                    

        os.rmdir(local_dest_path)
        processing_log = processing_log + ' ' + "File processing complete!!"
        outputDict['BlobContainer'] = container_name
        outputDict['BlobPath'] = dst_blob_location
        outputDict['RawFiles']=",".join(raw_files_list)
        outputDict['ConvertedFiles']=",".join(converted_files_list)
        outputDict['processingLog'] = processing_log

        # writing values to custom output
        with open('outputs.json', 'w') as outfile:
            json.dump(outputDict, outfile)


    except Exception as e:
        # writing values to custom output
        outputDict["wrapper Exception"] = str(e)
        with open('outputs.json', 'w') as outfilex:
            json.dump(outputDict, outfilex)
        sys.exit(str(e))

main()