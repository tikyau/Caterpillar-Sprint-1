import os
import glob
import fnmatch
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


#Function to upload files from local directory to azure storage
def uploadToBLOB(container_name, block_blob_service, BLOB_Location, LOCAL_DESTINATION):
    try:
        if BLOB_Location is None:
            BLOB_Location = ''
        if os.path.exists(LOCAL_DESTINATION):
            filelist = glob.glob(os.path.join(LOCAL_DESTINATION, "*"))
            returnfilelist = []
            for f in filelist:
                block_blob_service.create_blob_from_path(container_name,BLOB_Location.strip('/') + '/' + os.path.basename(f), f)
                returnfilelist.append(os.path.basename(f))

        return returnfilelist,','.join(returnfilelist) + ' uploaded successfully to -' + container_name + '/' + BLOB_Location, 'Success'
    except Exception as e:
        return None,'Error-Failed to upload file to BLOB storage ' + str(e), 'Failure'

#Function to upload specified files from BLOB to BLOB
def copyBLOB(block_blob_service, container_name, src_blob_location, filename, dst_blob_location):
    try:
        count = 0
        filelist = []
        upload_container = container_name                                    #comment this if archive container is different
        if src_blob_location is not None:
            src_blob_location = str.replace(str(src_blob_location), '\\', '/')
        generator = block_blob_service.list_blobs(container_name)
        file_names=[]
        if isinstance(filename,list):
            file_names = filename
        else:
            fileList = filename.split(',')
            for file in fileList:
                file_names.append(file)

        for blob in generator:
            head, tail = os.path.split("{}".format(blob.name))
            for file_name in file_names:
                if src_blob_location is not None and src_blob_location != '':
                    if fnmatch.fnmatch(tail, file_name.strip()) and head == src_blob_location.strip("/"):
                        print('uploading ' + blob.name)
                        blob_url = block_blob_service.make_blob_url(container_name, blob.name)
                        #blob_name,blob_ext =os.path.splitext(tail)

                        if dst_blob_location is None or dst_blob_location == '':
                            block_blob_service.copy_blob(upload_container, tail, blob_url)
                        else:
                            block_blob_service.copy_blob(upload_container, dst_blob_location.strip('\\') + '\\' + tail,
                                                         blob_url)

                        filelist.append(tail)
                        count = count + 1
                elif src_blob_location is None or src_blob_location == '':
                    if fnmatch.fnmatch(tail.lower(), file_name.strip().lower()) and (head is None or head == ''):
                        print('archiving ' + blob.name)
                        blob_url = block_blob_service.make_blob_url(container_name, blob.name)
                        #blob_name, blob_ext = os.path.splitext(tail)
                        if dst_blob_location is None or dst_blob_location == '':
                            block_blob_service.copy_blob(upload_container, tail,
                                                         blob_url)
                        else:
                            block_blob_service.copy_blob(upload_container, dst_blob_location.strip('\\') + '\\' + tail,
                                                         blob_url)

                        filelist.append(tail)
                        count = count + 1
        if count != 0:
            return filelist,str(count)+' matching file(s) uploaded successfully to -' + container_name + '/' + dst_blob_location, 'Success'
        else:
            return filelist,'No matching file(s) found for given file name!!', 'Success'
    except Exception as e:
        return None,'Failed to upload files : ' + str(e), 'Failure'

#Function to delete files from local path
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

