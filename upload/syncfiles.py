import os
import paramiko
# from . import Settings
import platform
from datetime import datetime


class Settings:
    
    REMOTE_HOST = '120.27.20.114'
    REMOTE_PORT = 7000
    REMOTE_USER = 'root'
    REMOTE_PWD = 'Food123456'
    REMOTE_PATH = '/opt/baas_test'
    LOCAL_PATH = './config_file'


class SyncFiles(object):
    """
    复制本机文件到远端
    """
    def __init__(self):
        self.f = open("existsfile.log", "a+")
        self.remote_host = Settings.REMOTE_HOST
        self.remote_port = Settings.REMOTE_PORT
        self.remote_user = Settings.REMOTE_USER
        self.remote_pwd = Settings.REMOTE_PWD
        if Settings.REMOTE_PATH[-1] == '/' or Settings.REMOTE_PATH[-1] == '\\':
            self.remote_path = Settings.REMOTE_PATH[0:-1]
        else:
            self.remote_path = Settings.REMOTE_PATH
        if Settings.LOCAL_PATH[-1] == '/' or Settings.LOCAL_PATH[-1] == '\\':
            self.local_path = Settings.LOCAL_PATH[0:-1]
        else:
            self.local_path = Settings.LOCAL_PATH

    def get_upload_files(self):
        """获取待上传的所有文件"""
        local_path_set = set()  # 本地文件
        file_transfered_set =set()  # 已经上传过的文件
        for root, dirs, files in os.walk(self.local_path):
            for file in files:
                local_file = os.path.join(root, file)  # 完整的文件路径：/A/B/C/1.txt

                local_path_set.add(local_file)

        self.f.seek(0,0)  # 将记录文件指针放在文件头，用于读文件

        for line in self.f.readlines():
            file_transfered = line.split("-")[-1].strip()

            file_transfered_set.add(file_transfered)

        ready_upload_set = local_path_set ^ file_transfered_set  # 待上传的文件
        return list(ready_upload_set)

    def record_log(self, path):

        now = datetime.now()
        # if platform.platform().startswith("Windows"):
        # self.f.write(now.strftime('%Y/%M/%d %H:%M:%S %A ') + ' -  ' + path + '\\r\\n')
        # else:
        self.f.write(now.strftime('%Y/%M/%d %H:%M:%S %A ') + ' -  ' + path + '\n')

    def transfile(self):
        """上传文件"""
        try:
            # 实例化Transport
            trans = paramiko.Transport((self.remote_host, self.remote_port))
            # 建立连接
            trans.connect(username=self.remote_user, password=self.remote_pwd)
            # 实例化一个sftp对象
            sftp = paramiko.SFTPClient.from_transport(trans)

            ready_upload_list = self.get_upload_files()

            already_dir = []  # 存放远端新建的目录
            if ready_upload_list:

                for local_file_path in ready_upload_list:

                    if platform.platform().startswith("Windows"):

                        file_need = local_file_path.replace(self.local_path, '').replace('\\','/')  # 取出本地路径后，需要同步到远端的部分:B/C/1.txt

                    else:
                        file_need = local_file_path.replace(self.local_path, '')
                    remote_file_path = self.remote_path + file_need

                    try:
                        # 上传文件,必须是文件的完整路径,远端的目录必须已经存在
                        sftp.put(localpath=local_file_path, remotepath=remote_file_path)
                        self.record_log(local_file_path)
                    except Exception as e:
                        # 如果目录不存在就创建，但是不支持递归创建

                        dir_need_list = os.path.split(file_need)[0].split("/")  # B、C
                        dir1 = ''
                        print(dir_need_list)
                        for dir in dir_need_list[1:]:
                            if dir not in already_dir:
                                # 目录存在会报错，所以把新建过的目录存在一个全局列表中
                                if platform.platform().startswith("Windows"):
                                    sftp.mkdir(os.path.join(self.remote_path, dir1, dir).replace('\\','/'))
                                else:
                                   sftp.mkdir(os.path.join(self.remote_path, dir1, dir))
                            dir1 = dir
                            already_dir.append(dir)  # 新建过的目录存在一个全局列表中
                            # 再次执行
                        sftp.put(localpath=local_file_path, remotepath=remote_file_path)
                        self.record_log(local_file_path)
        except Exception as e:
            pass
        finally:
            trans.close()

if __name__ == "__main__":
    sf = SyncFiles()
    sf.transfile()
