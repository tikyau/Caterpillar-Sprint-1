import os
import fnmatch
import glob
from azure.storage.blob import BlockBlobService, baseblobservice, PublicAccess

#Function to connect to blob storage
def connectblobstorage(connection_string, container_name):
    try:
        block_blob_service = BlockBlobService(connection_string=connection_string)
        if not checkcontainerexists(container_name, connection_string):
            raise Exception('Container does not exist!!')
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
        return block_blob_service, 'Connected to Azure BLOB storage successfully!!', 'Success'
    except Exception as e:
        return None, 'Error-Could not connect to Azure BLOB storage. Please verify credentials!! ' + str(e), 'Failure'

#Function to check for container existence
def checkcontainerexists(container_name, connection_string):
    blob_service = baseblobservice.BaseBlobService(connection_string=connection_string)
    containers = blob_service.list_containers()
    for c in containers:
        if c.name == container_name:
            return True

#Function to download blob from azure storage
def downloadfromblob(block_blob_service, container_name, src_blob_location, filename, loc_dest):
    try:
        count = 0
        filelist = []
        if src_blob_location is not None:
            src_blob_location = str.replace(str(src_blob_location), '\\', '/')
        generator = block_blob_service.list_blobs(container_name)
        file_names = filename.split(',')
        #print(filename)
        for blob in generator:
            head, tail = os.path.split("{}".format(blob.name))
            for file_name in file_names:
                if src_blob_location is not None and src_blob_location != '' and src_blob_location.strip('/') == head:

                    if fnmatch.fnmatch(tail.lower(),file_name.strip().lower()):
                        print('downloading ' + blob.name)
                        block_blob_service.get_blob_to_path(container_name, blob.name, loc_dest + "/" + tail)
                        filelist.append(tail)
                        count = count + 1

                elif src_blob_location is None or src_blob_location == '':
                    if fnmatch.fnmatch(tail.lower(), file_name.strip().lower()) and head == '':
                        print('downloading ' + blob.name)
                        block_blob_service.get_blob_to_path(container_name, blob.name, loc_dest + "/" + tail)
                        filelist.append(tail)
                        count = count + 1
                        
        if count != 0:
            return filelist,str(count)+' matching file(s) downloaded successfully from BLOB storage', 'Success'
        else:
            raise Exception('No matching file(s) found for given file name!!')
    except Exception as e:
        return None,'Failed to download files from BLOB storage : ' + str(e), 'Failure'

#Function to clear local path
def clearLocalPath(LOCAL_DESTINATION):
    try:
        if os.path.exists(LOCAL_DESTINATION):
            filelist = glob.glob(os.path.join(LOCAL_DESTINATION, "*.*"))
            for f in filelist:
                os.remove(f)
        else:
            os.makedirs(LOCAL_DESTINATION)
        return "Cleared local destination :" + LOCAL_DESTINATION,'Success'
    except Exception as e:
        return 'Error-Failed to clear local destination!! '+str(e),'Failure'

#Function to list the files in BLOB folder

def listFilesOnBlob(block_blob_service,container_name,blob_folder_path_prefix,filename):
    try:
        generator = block_blob_service.list_blobs(container_name, prefix=blob_folder_path_prefix)
        blob_files = []
        for blob in generator:
            head, tail = os.path.split("{}".format(blob.name))
            if blob_folder_path_prefix is not None and blob_folder_path_prefix != '' and blob_folder_path_prefix.strip('/') == head:
                if fnmatch.fnmatch(tail.lower(),filename.lower()):
                    blob_files.append(tail)
        if len(blob_files) != 0:
            return blob_files,'Blob file list has been created','Success'
        else:
            return None,'No matching file(s) found for given file name!!','Failure'
    except Exception as e:
        return  None,'Failed to list the files in given BLOB folder'+str(e),'Failure'