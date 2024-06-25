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

    def post(self,params=[]):
        try:
            local_filepath = params[0]
            destination_filename = f"/home/jovyan/work/progjar/progjar4a/{params[1]}"

            if local_filepath == '':
                return dict(status='ERROR', data='File not found')

            with open(local_filepath, 'rb') as fp:
                file_content = fp.read()
            
            encoded_content = base64.b64encode(file_content).decode()
            file_data = base64.b64decode(encoded_content)
            
            with open(destination_filename, 'wb') as fp:
                fp.write(file_data)
            
            return dict(status='OK', data=f'File {destination_filename} uploaded successfully')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fileaddr = f"/home/jovyan/work/progjar/progjar4a/files/{filename}"
            os.remove(fileaddr)
            return dict(status='OK', data=f"File {filename} deleted successfully")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

if __name__=='__main__':
    f = FileInterface()
    # print(f.list())
    # print(f.get(['unggah.txt']))
    # print(f.post('unggah.txt', 'berhasil.txt'))
    # print(f.delete(['pokijan3.jpg']))