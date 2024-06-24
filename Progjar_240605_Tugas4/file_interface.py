import os
import json
import base64
import requests
from glob import glob


class FileInterface:
    def __init__(self, base_dir='/app/files'):
        self.base_dir = base_dir
        os.chdir(self.base_dir)

    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def post(self, local_filepath, destination_filename):
        try:
            with open(local_filepath, 'rb') as fp:
                file_content = fp.read()
            
            encoded_content = base64.b64encode(file_content).decode()
            if destination_filename == '' or encoded_content == '':
                return dict(status='ERROR', data='Invalid parameters')
            
            file_data = base64.b64decode(encoded_content)
            with open(destination_filename, 'wb') as fp:
                fp.write(file_data)
            
            return dict(status='OK', data=f'File {destination_filename} uploaded successfully')
        except Exception as e:
            return dict(status='ERROR', data=str(e))



if __name__=='__main__':
    f = FileInterface()
    # local_filepath = '/app/files/tes_unggah_progjar.txt'  # Path within the container
    # destination_filename = 'tes_unggah_progjar.txt'
    # result = f.post(local_filepath, destination_filename)
    # print(result)

    # print(f.list())
    # print(f.get(['tes_unggah_progjar.txt']))
    # print(f.post('/app/files/tes_unggah_progjar.txt', 'tes_unggah_progjar.txt'))
