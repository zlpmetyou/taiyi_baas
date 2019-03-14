# # # from flask import Flask
# # # from flask_jwt import JWT, jwt_required, current_identity
# # # from werkzeug.security import safe_str_cmp
# # # import json
# # #
# # #
# # # class User(object):
# # #     def __init__(self, id, username, password):
# # #         self.id = id
# # #         self.username = username
# # #         self.password = password
# # #
# # #     def __str__(self):
# # #         return "User(id='%s')" % self.id
# # #
# # #
# # # users = [
# # #     User(1, 'user1', 'abcxyz'),
# # #     User(2, 'user2', 'abcxyz'),
# # # ]
# # # username_table = {u.username: u for u in users}
# # # userid_table = {u.id: u for u in users}
# # #
# # #
# # # def authenticate(username, password):
# # #     user = username_table.get(username, None)
# # #     if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
# # #         return user
# # #
# # #
# # # def identity(payload):
# # #     user_id = payload['identity']
# # #     return userid_table.get(user_id)
# # #
# # #
# # # app = Flask(__name__)
# # # app.debug = True
# # # app.config['SECRET_KEY'] = 'super - secret'
# # # app.config["JWT_AUTH_USERNAME_KEY"] = 'mobile'
# # # # app.config["JWT_AUTH_PASSWORD_KEY"] = 'password'
# # #
# # # jwt = JWT(app, authenticate, identity)
# # #
# # #
# # # @app.route('/protected')
# # # @jwt_required()
# # # def protected():
# # #     print("this protected is successed!!!")
# # #     return ' % s' % current_identity
# # #
# # #
# # # if __name__ == '__main__':
# # #     print(app.config['JWT_AUTH_USERNAME_KEY'])
# # #     print(app.config['JWT_AUTH_PASSWORD_KEY'])
# # #     app.run()
# # #
# # # DO_NOTHING NULLIFY CASCADE DENY PULL
# # # import datetime
# # # # #
# # from mongoengine import *
# # connect('test', host='127.0.0.1', port=27017)
# # # connect('test', host='120.27.22.25', port=27019)
# # #
# # #
# # class School(Document):
# #     id = StringField(default="", primary_key=True)
# #     name = StringField()
# #     address = StringField()
# # #     # users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
# # #     # Users = DictField(ReferenceField)
# # #
# #
# # class User(Document):
# #     name = StringField()
# # #     # age = IntField()
# # #     # gender = IntField()
# # #     # school = ReferenceField(School, reverse_delete_rule=CASCADE)
# # #     cs_time = DateTimeField(default=datetime.datetime.now())
# # #
# # #
# # # user1 = User('zlp')
# #
# # # user = User.objects.get(name='zlp')
# # # school = School.objects.get(id='1')
# # # user = User.objects(school=school)
# # # print(user)
# # # print(dir(user))
# # # print(user.cs_time+datetime.timedelta(hours=8))
# # # print(type(user.cs_time))
# # school = School('1', '北大','北京')
# # school.save()
# # user1 = User('zlp', 18,  12, school)
# # # user2 = User('zzz', 11, 10, school)
# # user1.save()
# # # user2.save()
# # # School.objects(id='1').first().delete()
# # # user1 = User.objects.get(name='zlp')
# # # user2 = User.objects.get(name='zzz')
# # # user1.delete()
# # # user2.delete()
# #
# # # school = School('1','aa','北京',{'net':'22','age':33})
# # # school.save()
# # # school = School.objects.get(id='1')
# # # print(school.Users)
# # # print(type(school.Users))
# # # print(school.Users.get('net'))
# # # users = User.objects()
# # # school1 = School('1','北大','北京',users)
# # # school1.save()
# # # user = User('ss2',11,11)
# # # user.save()
# # # School.objects.get(name='北大').update(add_to_set__Users=user)
# # # user = User.objects(age=11)
# # # user.delete()
# # # host_count = User.objects.all().count()
# # # hosts = User.objects.skip(1).limit(1).order_by('-age')
# # # #
# # # print(host_count,hosts)
# # # school = School.objects(name='北大')
# # # school.delete()
# # # # school.update(name='复旦')
# # # user = User.objects(name='zlp')
# # # user.update(school=school)
# # # user = User.objects(age='18')
# # # print(user)
# # # #
# # # user.delete()
# # #
# # # user = User('zlp1','18','nv','xx','asdf')
# # # user.save()
# # # # print(users)
# # # # # school2 = School('2','清华','北京')
# # # school2.save()
# # # school = School.objects.get(id='1')
# # # print(school.Users)
# #
# # # # school = School.objects.get(name='北大')
# # # # user = User.objects.get(school=school)
# # # # # user = User.objects.get(name='zlp')
# # # # print(user.school.name)
# # # user = User('zlp', '18', 'nv', school, 'asdf')
# # # user.save()
# # # User.objects(id="5bcd3e221d41c81d479d8066").delete(school)
# # # # userid = user.id
# # # user = User.objects.get(id='5bab396c1d41c83657704cb8')
# # # print(user.id)
# # # # user.name = 'zzz'
# # # user.update(set__users='zha', upsert=True)
# # # print(user.name)
# # # a={'name':'zlp','age':'13','gender':'nan','school':'aaaa','class':'null'}
# # # b = { i:a[i] for i in a if (a[i] and i!='age')}
# # # print(b)
# # # print(dir(a))
# # # User.objects(id='5bab37f01d41c8359ca9d306').update(**a)
# # # dic = {'name':'zlp','age':13,'gender':'nan'}
# # # print(hasattr(dic,'name'))
# # # # print(dic['school'])
# # #
# # #
# # # class User:
# # #     haha = 3123
# # #
# # #     def __init__(self,age,username=None):
# # #         self.gla = 123
# # #         self.username = username
# # #         self.age = age
# # #     def get_id(self,id):
# # #
# # #         self.id = id
# # #         self.name = 'zz'
# # #         self.age = '12'
# # #
# # #     def caca(self):
# # #         print('a')
# # # user =User('zlp')
# # # print(user.age)
# # # import random
# # # # a = random.random('z')
# # # # print(a)
# # # import string
# # #
# # #
# # # s = string.ascii_letters
# # # r = random.choice(s)
# # # print(r)
# # # # user = User()
# # # # print(user.name)
# # # # user.get_id(12)
# # # # print(user.name)
# # # # print(User.__dict__)
# # # # print(dir(User))
# # # # print(user.__dict__)
# # # # print(dir(user))
# # # # print(hasattr(User,'zz'))
# # # # print(callable(getattr(User,'get_id')))
# # # a = random.sample(range(100) , 50)
# # # print(a)
# # # a = """
# # # for i in range(10):
# # #     print('hello')
# # #     """
# # # b = "b'asdfjalkdsjfla'"
# # #
# # # print(b)
# #
# # # import random
# # # import string
# # # #第一种方法
# # # seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# # # sa = []
# # # for i in range(8):
# # #   sa.append(random.choice(seed))
# # # salt = ''.join(sa)
# # # print(salt)
# # # #运行结果：l7VSbNEG
# # # #第二种方法
# # # salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
# # # print(salt)
# # # #运行结果：VOuCtHZs
# # # from datetime import datetime
# # # # 2018-10-09 19:32:44.834823
# # # # 2018-10-09 11:33:06.754079
# # # a = datetime.utcnow()
# # # print(a)
# # # print(type.__class__)
# # # print(object.__class__)
# # # print([].__class__)
# # #
# # # print(type.__bases__)
# # # print(object.__bases__)
# # # from marshmallow import Schema, fields
# # #
# # #
# # # class HostSchema(Schema):
# # #     id = fields.String()
# # #     name = fields.String()
# # #
# # #
# # # class User:
# # #     name = 'zzz'
# # #     id = '1'
# # #
# # #
# # # user = User()
# # #
# # #
# # # a = HostSchema(many=False)
# # # b = a.dump(user)
# # # print(b)
# # #
# # # #
# # # # import sys
# # #
# # # a = dir(sys)
# # # b = sys.version
# # # print(b)
# # # from d
# #
# # # net_names = [x["Name"] for x in client.networks()]
# # # print(net_names)
# # # info = client.info()['Swarm']
# # # print(info)
# # # from urllib.parse import urlparse
# # #
# # # url = urlparse("tcp://120.27.20.114:2375")
# # # print(url)
# # # a = {'name':'1'}
# # # b = {}
# # # a.update(b)
# # # print(a+'\n')
# # #
# # # class A(object):
# # #     def __init__(self):
# # #         self.name = 'z'
# # #
# # #     def __getattr__(self, item):
# # #         return self[item]
# # #
# # # a = A()
# # # print(a.get('name'))
# #
# # # print(bool([1]))
# # # from urllib.parse import urlparse
# # # from docker import APIClient
# # # url = 'tcp://120.27.20.11:2375'
# # # # url = urlparse('tcp://127.0.0.1:8080/v1?a=1')
# # # # print(url)
# # # APIClient(base_url=url, version="auto", timeout=3)
# # # # print(client)
# # import os
# # import random
# # import string
# # #
# # # cluster_schema = ClusterSchema(many=many)
# # # return cluster_schema.dump(doc).data
# # #
# # # #
# # # import requests, json
# # #
# # # url = 'http://192.168.1.88:9001/baasServer/getToken'
# # # data = {
# # #     'UserId':'haifeng',
# # #     'Passwd':'123456'
# # # }
# # # # data = json.dumps(data)
# # # r = requests.post(url, json=data)
# # # result = r.text
# # # # result= json.loads(result)
# # # print(result.get('Token'))
# # # # # print(type(result.get('Token')))
# # # # print(result.get('Token'))
# # # from http import client
# # # import urllib
# # #
# # # conn = client.HTTPSConnection('192.168.1.95', port=9001, timeout=5)
# # # conn.request("POST", '/baasServer/getToken', data)
# # # response = conn.getresponse()
# # # response_str = response.read()
# # # conn.close()
# # # print(response_str)
# #
# # # a = 'a'
# # # b = 'b'
# # # print(a + os.sep + b)
# # # print(a.split(":"))
# # #
# # # a = {'{}'.format():'{}'}
# # # a.format('a','b')
# # # salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
# # # print(salt)if (ca_num== 1) else ''
# #
# # # a = 'ca{}'.format(1)
# # # print(a)
# # # ca_num = 1
# # # ca_list = ['ca{}'.format(i) if (ca_num != 1) else '' for i in range(ca_num) ]
# # # print(ca_list)
# # # import werkzeug
# # # from flask import Flask
# # # import tarfile
# # # from flask_restful import Resource, Api, reqparse
# # # from werkzeug.datastructures import FileStorage
# # # from werkzeug.utils import secure_filename
# # #
# # # app = Flask(__name__)
# # # api = Api(app)
# # #
# # #
# # # parser = reqparse.RequestParser()
# # # parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')
# # #
# # #
# # # class HelloWorld(Resource):
# # #     def post(self):
# # #         args = parser.parse_args()
# # #         content = args.get('picture')
# # #         print(content)
# # #         print(dir(content))
# # #         filename = secure_filename(content.filename)
# # #         print(filename)
# # #         content.save(os.path.join('/home/zlp/', filename))
# # #
# # #         def extract(tar_path, target_path):
# # #             try:
# # #                 tar = tarfile.open(tar_path, "r:gz")
# # #                 file_names = tar.getnames()
# # #                 for file_name in file_names:
# # #                     tar.extract(file_name, target_path)
# # #                 tar.close()
# # #             except Exception as e:
# # #                 raise e
# # #         extract('/home/zlp/{}'.format(filename), '/home/zlp/result')
# # #         return {'hello': 'world'}
# # #
# # #
# # # api.add_resource(HelloWorld, '/')
# # #
# # # if __name__ == '__main__':
# # #     app.run(debug=True)
# # import tarfile
# # #
# # # # 创建压缩包名
# # # from time import sleep
# #
# # # tar = tarfile.open("/home/zlp/zlp.tar.gz", "w:gz")
# # # print(os.fwalk("/home/zlp/result/"))
# # # 创建压缩包
# # # for i in os.walk("/home/zlp/result/"):
# # #     print(i)
# # # sleep(10)
# # # for file in files:
# # #     # print(root, )
# # #     # print(file)
# # #     # sleep(5)
# # #     fullpath = os.path.join('', file)
# # #     # print(fullpath)
# # #     # sleep(5)
# # #     tar.add(fullpath)
# # # tar.close()
# # # path = '/home/sy/zz/zz/aa/boys'
# # # result = os.path.dirname(path)
# # # result2 = os.path.split(path)
# # # print(result2)
# # # print(os.getcwd())
# # # import os, tarfile
# # # #一次性打包整个根目录。空子目录会被打包。
# # # #如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
# #
# # #
# # # def make_targz(output_filename, source_dir):
# # #     with tarfile.open(output_filename, "w:gz") as tar:
# # #         for dir in source_dir:
# # #             tar.add(dir, arcname=os.path.basename(dir))
# # #     return tar.name
# #
# # # import os
# # # a = os.path.basename('/home/zlp/zlp.tar.gz')
# # # b = os.path.dirname('/home/zlp/zlp.tar.gz')
# # # c = os.path.split('/home/zlp/zlp.tar.gz')
# # # d = os.getcwd()
# # # e = os.environ
# # # print(a,b,c,d,e)
# #
# # # from zipfile import ZipFile
# # # from os import listdir
# # # from os.path import isfile, isdir, join
# # #
# # #
# # # def addFileIntoZipfile(srcDir, fp):
# # #     for subpath in listdir(srcDir):
# # #         subpath = join(srcDir, subpath)
# # #         if isfile(subpath):
# # #             fp.write(subpath)
# # #         elif isdir(subpath):
# # #             fp.write(subpath)
# # #             addFileIntoZipfile(subpath, fp)
# # #
# # #
# # # def zipCompress(srcDir, desZipfile):
# # #
# # #     fp = ZipFile(desZipfile, mode='a')
# # #     addFileIntoZipfile(srcDir, fp)
# # #     fp.close()
# # #
# # # paths = ['/home/zlp/result', '/home/zlp/Desktop/teston2']
# # # for path in paths:
# # #     zipCompress(path, 'test.zip')
# #
# #
# # # if __name__ == '__main__':
# # #      m = make_targz('zlp.tar.gz', ['/home/zlp/result/channel-artifacts','/home/zlp/result/crypto-config'])
# # # # print(dir(m))
# # # print(m)
# # # # print(m.name)
# # # def func(name, age=12, *, gender=1):
# # #     print(name,age,gender)
# # #
# # # func(1,2,4)
# #
# # # import requests
# # # from urllib3 import encode_multipart_formdata
# # #
# # # data = {}
# # # data['file'] = ('config', open('/home/zlp/zlp.tar.gz', 'rb').read())
# # # encode_data = encode_multipart_formdata(data)
# # # print(encode_data)
# # # data = encode_data[1]
# # # print(data)
# #
# # # a = '13834369467'
# # # b = a[-6:]
# # # print(b)
# # # print(__file__)
# # # 'localhost', 1024
# # # a =  {1:2}
# # # print()
# # # import socket
# # # socket.setdefaulttimeout(3)
# # # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # # result = s.connect_ex(('120.27.20.114', 2375))
# # # print(result)
# #
# #
# # # class A(dict):
# # #
# # #     # name = 1
# # #     # age = 2
# # #     def __init__(self,name,age, **kwargs):
# # #         self.name = name
# # #         self.age = age
# # #         # print(kwargs)
# # #         for k,v in kwargs.items():
# # #             setattr(self,k,v)
# # #         super(A, self).__init__()
# # #
# # #     def __getattr__(self, name):
# # #         try:
# # #             return self[name]
# # #         except KeyError as e:
# # #             raise AttributeError(e)
# # #
# # #     def __setattr__(self, name, value):
# # #         self[name] = value
# # #
# # #     def get_data(self):
# # #         """
# # #         Get the configuration data for the blockchain network
# # #         Returns: data dict
# # #         """
# # #         return dict(self)
# # # #
# # #
# # # a = A('zlp',15, gender=1,ca=1,cc=2)
# # # # print(a.gender)
# # # print(a.get_data())
# # # print(dict(a))
# # # a.gender = 111
# # # print(a.__dict__)
# # # print(type(a.__dict__))
# # # b = {}
# # # import datetime
# # # print(8/5)
# # # import time
# # # a = datetime.datetime.now()
# # # # time.sleep(5)
# # # b = datetime.datetime(2018, 12, 19, 11, 24, 49, 987171)
# # # remaining_time = b - a
# # # # print(remaining_time.)
# # # # print(datetime.datetime.tzname())
# # # print(str(remaining_time))
# # # print('%sd%dh' % (remaining_time.days, remaining_time.seconds / 60 / 60))
# # # # print(datetime.datetime.strptime(str(remaining_time),'%d%H'))
# # # print(remaining_time.__str__())
# # # print(type(remaining_time))
# # # print(dir(a))
# # # print(isinstance(b,dict))
# #
# # # print(dict.fromkeys([1,2,3],'a'))
# # # a = zip([1,2,3],['a','b'])
# # # # print(a)
# # # for i in a:
# # #     print(i)
# #
# # # a = {1:2,3:4}
# # # print(a.keys())
# # # def unit_to_word(u):
# # #     convert_table = {
# # #         0: "zero",
# # #         1: "one",
# # #         2: "two",
# # #         3: "three",
# # #         4: "four",
# # #         5: "five",
# # #         6: "six",
# # #         7: "seven",
# # #         8: "eight",
# # #         9: "nine",
# # #     }
# # #     return convert_table[u]
# # # def tens_to_word(t):
# # #     convert_table = {
# # #         0: "",
# # #         10: "ten",
# # #         11: "eleven",
# # #         12: "twelve",
# # #         13: "thirteen",
# # #         14: "fourteen",
# # #         15: "fifteen",
# # #         16: "sixteen",
# # #         17: "seventeen",
# # #         18: "eighteen",
# # #         19: "nineteen",
# # #         2: "twenty",
# # #         3: "thirty",
# # #         4: "forty",
# # #         5: "fifty",
# # #         6: "sixty",
# # #         7: "seventy",
# # #         8: "eighty",
# # #         9: "ninety",
# # #     }
# # #     if 9 < t < 20:
# # #         return convert_table[t]
# # #     else:
# # #         tens = convert_table[t/10] + " " + unit_to_word(t%10)
# # #         return tens
# # # def hundreds_to_word(h):
# # #     if h > 99:
# # #         word = unit_to_word(h/100) + " hundred"
# # #         tens = h % 100
# # #         if tens == 0:
# # #             return word
# # #         else:
# # #             return word + " and " + tens_to_word(tens)
# # #     else:
# # #         return tens_to_word(h)
# # # for test in [0, 5, 19, 23, 100, 700, 711, 729]:
# # #     print(test, "=>", hundreds_to_word(test))
# # #
# # # a = [1, 2]
# # # b = [3, 4]
# # # c = a + b
# # # print(id(a))
# # # print(id(b))
# # # print(id(c))
# # # print(id(a+b))
# # # a.append(3)
# # #
# # # print(id(a))
# # # a = {1:2}
# # # b = {2:3}
# # # c = {5:6}
# # # a.update(b)
# # # a.update(c)
# # # print(a)
# # # a = ["${COMPOSE_PROJECT_PATH}/solo/channel-artifacts/orderer.genesis.block:"
# # #             "/var/hyperledger/orderer/orderer.genesis.block" ]
# # # print(a)
# # # list1 = ['a', 'b', 'c']
# # # b = ' '.join(list1)
# # # a = 'bash {}'.format(' '.join(list1))
# # # print(a)
# # # a = {1:2}
# # # print(len(a))
# # # print(a.values())
# # # a = 'a.com.cn'
# # # b = a.split('.')
# # # print(b)
# # # a = {
# # #     "version":"3.2",
# # #     "services":{
# # #         "ca.org1.example.com":{
# # #             "command":"sh -c 'fabric-ca-server start -b admin:adminpw -d'",
# # #             "volumes":[
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/ca/:/etc/hyperledger/fabric-ca-server-config"
# # #             ],
# # #             "container_name":"${COMPOSE_PROJECT_NAME}_ca_org1",
# # #             "image":"hyperledger/fabric-ca:1.1.0",
# # #             "environment":[
# # #                 "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
# # #                 "FABRIC_CA_SERVER_CA_NAME=ca_peerOrg1",
# # #                 "FABRIC_CA_SERVER_CA_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem",
# # #                 "FABRIC_CA_SERVER_CA_KEYFILE=/etc/hyperledger/fabric-ca-server-config/c6f2705be38be4bd9dd418e4796ee2275ae7edf204eb2b3eb180046a7830a43c_sk",
# # #                 "FABRIC_CA_SERVER_TLS_ENABLED=false",
# # #                 "FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org1.example.com-cert.pem",
# # #                 "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/c6f2705be38be4bd9dd418e4796ee2275ae7edf204eb2b3eb180046a7830a43c_sk"
# # #             ],
# # #             "ports":[
# # #                 "${CA_ORG1_ECAP_PORT}:7054"
# # #             ]
# # #         },
# # #         "orderer.example.com":{
# # #             "command":"orderer",
# # #             "container_name":"${COMPOSE_PROJECT_NAME}_orderer",
# # #             "ports":[
# # #                 "${ORDERER_PORT}:7050"
# # #             ],
# # #             "external_links":[
# # #                 "${COMPOSE_PROJECT_NAME}_peer0.org1.example.com:peer0.org1.example.com",
# # #                 "${COMPOSE_PROJECT_NAME}_peer1.org1.example.com:peer1.org1.example.com"
# # #             ],
# # #             "volumes":[
# # #                 "${COMPOSE_PROJECT_PATH}/solo/channel-artifacts/orderer.genesis.block:/var/hyperledger/orderer/orderer.genesis.block",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp:/var/hyperledger/orderer/msp",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/:/var/hyperledger/orderer/tls"
# # #             ],
# # #             "restart":"always",
# # #             "image":"hyperledger/fabric-orderer:1.1.0",
# # #             "environment":[
# # #                 "ORDERER_GENERAL_LOGLEVEL=DEBUG",
# # #                 "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0",
# # #                 "ORDERER_GENERAL_GENESISMETHOD=file",
# # #                 "ORDERER_GENERAL_GENESISFILE=/var/hyperledger/orderer/orderer.genesis.block",
# # #                 "ORDERER_GENERAL_LOCALMSPID=OrdererMSP",
# # #                 "ORDERER_GENERAL_LOCALMSPDIR=/var/hyperledger/orderer/msp",
# # #                 "ORDERER_GENERAL_TLS_ENABLED=false",
# # #                 "ORDERER_GENERAL_TLS_PRIVATEKEY=/var/hyperledger/orderer/tls/server.key",
# # #                 "ORDERER_GENERAL_TLS_CERTIFICATE=/var/hyperledger/orderer/tls/server.crt",
# # #                 "ORDERER_GENERAL_TLS_ROOTCAS=[/var/hyperledger/orderer/tls/ca.crt]"
# # #             ]
# # #         },
# # #         "cli":{
# # #             "command":"bash -c 'cd /tmp; bash check_port.sh ${CA_ORG1_ECAP_PORT} ${ORDERER_PORT} ${PEER0_ORG1_GRPC_PORT} ${PEER0_ORG1_EVENT_PORT} ${PEER1_ORG1_GRPC_PORT} ${PEER1_ORG1_EVENT_PORT} source scripts/func.sh; bash scripts/test_channel_create.sh; bash scripts/test_channel_join.sh; bash scripts/test_cc_install.sh; while true; do sleep 20180101; done'",
# # #             "hostname":"cli",
# # #             "depends_on":[
# # #                 "orderer.example.com",
# # #                 "peer0.org1.example.com",
# # #                 "peer1.org1.example.com"
# # #             ],
# # #             "tty":true,
# # #             "container_name":"${COMPOSE_PROJECT_NAME}_cli",
# # #             "volumes":[
# # #                 "${COMPOSE_PROJECT_PATH}/scripts:/tmp/scripts",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config.yaml:/etc/hyperledger/fabric/crypto-config.yaml",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config:/etc/hyperledger/fabric/crypto-config",
# # #                 "${COMPOSE_PROJECT_PATH}/solo/configtx.yaml:/etc/hyperledger/fabric/configtx.yaml",
# # #                 "${COMPOSE_PROJECT_PATH}/solo/channel-artifacts:/tmp/channel-artifacts",
# # #                 "${COMPOSE_PROJECT_PATH}/examples:/opt/gopath/src/examples"
# # #             ],
# # #             "restart":"always",
# # #             "image":"foodchainbaas/fabric-tools:chainfood-1.1.0",
# # #             "working_dir":"/opt/gopath/src/github.com/hyperledger/fabric/peer",
# # #             "environment":[
# # #                 "CORE_LOGGING_LEVEL=DEBUG",
# # #                 "CORE_LOGGING_FORMAT=%{color}[%{id:03x} %{time:01-02 15:04:05.00 MST}] [%{longpkg}] %{callpath} -> %{level:.4s}%{color:reset} %{message}",
# # #                 "CORE_PEER_TLS_ENABLED=false",
# # #                 "ORDERER_CA=/etc/hyperledger/fabric/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"
# # #             ]
# # #         },
# # #         "peer0.org1.example.com":{
# # #             "command":"peer node start",
# # #             "depends_on":[
# # #                 "orderer.example.com"
# # #             ],
# # #             "container_name":"${COMPOSE_PROJECT_NAME}_peer0_org1",
# # #             "ports":[
# # #                 "${PEER0_ORG1_GRPC_PORT}:7051",
# # #                 "${PEER0_ORG1_EVENT_PORT}:7053"
# # #             ],
# # #             "volumes":[
# # #                 "/var/run/docker.sock:/var/run/docker.sock",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/msp:/etc/hyperledger/fabric/msp",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls:/etc/hyperledger/fabric/tls"
# # #             ],
# # #             "restart":"always",
# # #             "image":"foodchainbaas/fabric-peer:chainfood-1.1",
# # #             "working_dir":"/opt/gopath/src/github.com/hyperledger/fabric/peer",
# # #             "environment":[
# # #                 "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_default",
# # #                 "CORE_LOGGING_LEVEL=DEBUG",
# # #                 "CORE_PEER_GOSSIP_USELEADERELECTION=true",
# # #                 "CORE_PEER_GOSSIP_ORGLEADER=false",
# # #                 "CORE_PEER_GOSSIP_SKIPHANDSHAKE=true",
# # #                 "CORE_PEER_TLS_ENABLED=false",
# # #                 "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
# # #                 "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
# # #                 "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
# # #                 "CORE_VM_DOCKER_HOSTCONFIG_MEMORY=268435456",
# # #                 "CORE_PEER_ID=peer0.org1.example.com",
# # #                 "CORE_PEER_LOCALMSPID=Org1MSP",
# # #                 "CORE_PEER_ADDRESS=peer0.org1.example.com:7051"
# # #             ]
# # #         },
# # #         "peer1.org1.example.com":{
# # #             "command":"peer node start",
# # #             "depends_on":[
# # #                 "orderer.example.com"
# # #             ],
# # #             "container_name":"${COMPOSE_PROJECT_NAME}_peer1_org1",
# # #             "environment":[
# # #                 "CORE_PEER_ID=peer1.org1.example.com",
# # #                 "CORE_PEER_LOCALMSPID=Org1MSP",
# # #                 "CORE_PEER_ADDRESS=peer1.org1.example.com:7051",
# # #                 "CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_default",
# # #                 "CORE_LOGGING_LEVEL=DEBUG",
# # #                 "CORE_PEER_GOSSIP_USELEADERELECTION=true",
# # #                 "CORE_PEER_GOSSIP_ORGLEADER=false",
# # #                 "CORE_PEER_GOSSIP_SKIPHANDSHAKE=true",
# # #                 "CORE_PEER_TLS_ENABLED=false",
# # #                 "CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt",
# # #                 "CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key",
# # #                 "CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt",
# # #                 "CORE_VM_DOCKER_HOSTCONFIG_MEMORY=268435456"
# # #             ],
# # #             "volumes":[
# # #                 "/var/run/docker.sock:/var/run/docker.sock",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/msp:/etc/hyperledger/fabric/msp",
# # #                 "${COMPOSE_PROJECT_PATH}/crypto-config/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls:/etc/hyperledger/fabric/tls"
# # #             ],
# # #             "restart":"always",
# # #             "image":"foodchainbaas/fabric-peer:chainfood-1.1",
# # #             "working_dir":"/opt/gopath/src/github.com/hyperledger/fabric/peer",
# # #             "ports":[
# # #                 "${PEER1_ORG1_GRPC_PORT}:7051",
# # #                 "${PEER1_ORG1_EVENT_PORT}:7053"
# # #             ]
# # #         }
# # #     }
# # # }
# #
# # # class B(object):
# # #     def __init__(self,name ,age,gender):
# # #         self.name = name
# # #         self.age = age
# # #         self.gender = gender
# # #
# # #
# # # b = B(
# # #     name='asdfadsfasdfasfdadsfadsfa',
# # #     age='adfasdfsadfadsfsafd',
# # #     gender='dsfasdfa/sadfasdfsadf/asdfadsf',
# # # )
# # # print(b.__dict__)
# # # print(os.path.dirname(__file__))
# #
# # # a = [1,2,3]
# # # a.append([5,6,7])
# # # print(a)
# # # a = '111'.capitalize()
# # # a = ['a','abc','def']
# # # a.append('abc')
# # # print(a)
# # # b = list(set(a))
# # # print(b)
# # #
# # # list1 = ['a', 'b']
# # # # print(' '.join(list1))
# # # class A(object):
# # #
# # #     def __init__(self):
# # #         self.orgs = {}
# # #
# # #     def generate_orgs(self):
# # #         # self.orgs = {1: 2}
# # #         setattr(self,'orgs',{1:2})
# # #     def start(self):
# # #         self.generate_orgs()
# # #         print(self.orgs)
# # #
# # #
# # # a = A()
# # # a.start()
# # # print(getattr(a,'org', 'cc'))
# # # # print(a.org)
# # #
# # # import time
# # # print(time.time())
# # # print(time.strftime('%Y-%m-%d, %H-%M-%S',time.localtime(time.time())))
# #
# # import json
# #
# # # a = ["{'name': 'orderer', 'domain': 'example.com', 'node': '3'}"]
# # # for i in a:
# # #     # b = json.loads(i)
# # #     # print(b)
# # #     print('name' in i)
# #
# # # a = {'a':{1: 2, 3: 4}}
# # # a.update({3: 5})
# # # # a[3] = 6
# # # # print(a)
# # # b = {'result': a}
# # # print(b)
# # # a =1
# # # b=2
# # # print({a:b})
# # # print(a.values())
# # # a = [1,2]
# # # b = {'a':{1: 2, 3: 4}}
# # # # a.append(b)
# # # list1 = a + list(b.values())
# # # print(list1)
# # from demjson import decode
# # # a = "{'domain': 'safd.com', 'name': 'order1'}"
# # # # b = 3
# # # # print(a.replace('aaa.',''))
# # #
# # # b = decode(a)
# # # # b = dict(a)
# # # print(type(b))
# # # class A(object):
# # #
# # #     def __init__(self,name):
# # #         self.name = name
# # #
# # #     def __new__(cls, *args, **kwargs):
# # #         if not hasattr(cls, '_instance'):
# # #             cls._instance = super(A, cls).__new__(cls)
# # #             cls._instance.age = 18
# # #         return cls._instance
# # #
# # #     def __del__(self):
# # #         print('dle')
# # # a = A('zlp')
# # # print(a.name)
# # # print(id(a))
# # # b = A('zzz')
# # # print(id(b))
# # # print(b.name)
# # # import json
# # #
# # # a = {'ChannelId': 'aa', 'BlockchainSign': '0a28ab9877244936b8c33471d711d444', 'BlockchainName': 'zz', 'Algorithm': 'solo', 'CreateTime': '20190112174629', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'aa', 'ChannelConfigName': 'aa.tx', 'Orderers': ['orderer.bb.com'], 'Orgs': [{'OrgId': 'cc', 'Peers': ['peer0.cc.bb.com', 'peer1.cc.bb.com']}]}], 'Orgs': [{'OrgId': '5c39b775957089000c5c47be', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'bb.com', 'MspId': 'OrdererOrg', 'Orderers': [{'Name': 'orderer.bb.com', 'Url': '172.31.239.245:7050'}]}, {'OrgId': '5c39b775957089000c5c47bf', 'Name': 'cc', 'Type': 'peer', 'Domain': 'bb.com', 'MspId': 'CcMSP', 'Peers': [{'Name': 'peer0.cc.bb.com', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer1.cc.bb.com', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca.cc.bb.com', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerCc'}]}]}
# # # b = json.dumps(a)
# # # print(b)
# # # a = '56adfa'
# # # b = a.capitalize()
# # # print(b)
#
# # from mongoengine import *
# # connect('test', host='127.0.0.1', port=27017)
# # a = [1]
# # b = [2,1]
# # print(a in b)
# # import uuid
# # print(uuid.uuid1().hex)
# # print(uuid.uuid4().hex)
# import time
# import random
# # import uuid
# # print(int(time.time())+random.randint(1, 100))
# # print(int(time.time())+random.randint(1, 100))
# # print(int(time.time())+random.randint(1, 100))
# # print('node_'+uuid.uuid4().hex)
# # print('node_'+uuid.uuid4().hex)
# # print('node_'+uuid.uuid4().hex)
# # print('node_'+uuid.uuid4().hex)
# # print('node_'+uuid.uuid4().hex)
# # from docker import APIClien
# # from docker import APIClient as Client
# # client = Client(base_url='tcp://120.27.20.114:2375', version="auto", timeout=5)
# # containers = client.containers(all=True)
# # print(containers)
# # import json
# # a={'ChannelId': 'channel1b4cb3e5601b470a845ea670bcce55fb', 'BlockchainSign': 'e46e8e1a2917478096601676d41897f6', 'BlockchainName': 'ce', 'Algorithm': 'solo', 'CreateTime': '20190117170652', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channel1b4cb3e5601b470a845ea670bcce55fb', 'ChannelName': 'a', 'ChannelConfigName': 'channel1b4cb3e5601b470a845ea670bcce55fb.tx', 'Orderers': ['ordererc2ed1672c46741729d848dfe7deb706d'], 'Orgs': [{'OrgId': 'org7322faaed37a4cf1b41aa7ae7626383b', 'Peers': ['peer2957f039dd794e98bfe895ea698f8397', 'peera498f2c86c0d44f7a71a9ec845028b92']}, {'OrgId': 'org988765eabfdd4391946ae399f3dbbc40', 'Peers': ['peer0ccbac0a35084b198cb7ff390f11e654', 'peer2ef065060ef4478b9597768f89068264']}]}], 'Orgs': [{'OrgId': 'orgb6dc178ced05410fa6bf00e4b85359fb', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'b.com', 'MspId': 'Orgb6dc178ced05410fa6bf00e4b85359fbMSP', 'Orderers': [{'Name': 'ordererc2ed1672c46741729d848dfe7deb706d', 'Url': '172.31.239.245:7650'}]}, {'OrgId': 'org7322faaed37a4cf1b41aa7ae7626383b', 'Name': 'c', 'Type': 'peer', 'Domain': 'b.com', 'MspId': 'Org7322faaed37a4cf1b41aa7ae7626383bMSP', 'Peers': [{'Name': 'peer2957f039dd794e98bfe895ea698f8397', 'Url': '172.31.239.245:7750', 'EventUrl': '172.31.239.245:7850'}, {'Name': 'peera498f2c86c0d44f7a71a9ec845028b92', 'Url': '172.31.239.245:7950', 'EventUrl': '172.31.239.245:8050'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:8550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrg7322faaed37a4cf1b41aa7ae7626383b'}]}, {'OrgId': 'org988765eabfdd4391946ae399f3dbbc40', 'Name': 'd', 'Type': 'peer', 'Domain': 'b.com', 'MspId': 'Org988765eabfdd4391946ae399f3dbbc40MSP', 'Peers': [{'Name': 'peer0ccbac0a35084b198cb7ff390f11e654', 'Url': '172.31.239.245:8150', 'EventUrl': '172.31.239.245:8250'}, {'Name': 'peer2ef065060ef4478b9597768f89068264', 'Url': '172.31.239.245:8350', 'EventUrl': '172.31.239.245:8450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:8650', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrg988765eabfdd4391946ae399f3dbbc40'}]}]}
# # a= {'ChannelId': 'channelc31f75b5dee84eb593dd9709d251edfb', 'BlockchainSign': 'c3d0291613ab4412bdc849acaaed0e02', 'BlockchainName': 'zz', 'Algorithm': 'solo', 'CreateTime': '20190117144406', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channelc31f75b5dee84eb593dd9709d251edfb', 'ChannelName': 'aa', 'ChannelConfigName': 'channelc31f75b5dee84eb593dd9709d251edfb.tx', 'Orderers': ['orderer8239719120a043e6b311a5c88bc45615'], 'Orgs': [{'OrgId': 'orga814867ea5144de6b7bf4d08a13a134a', 'Peers': ['peerf6e45c54838b4cfca8eda15baed2bece', 'peer3039a119ffdc44a9b4596d2382489333']}]}], 'Orgs': [{'OrgId': 'org13f40ea3376f4700bf710b119e4ef1b9', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'bb.com', 'MspId': 'Org13f40ea3376f4700bf710b119e4ef1b9MSP', 'Orderers': [{'Name': 'orderer8239719120a043e6b311a5c88bc45615', 'Url': '172.31.239.245:7050'}]}, {'OrgId': 'orga814867ea5144de6b7bf4d08a13a134a', 'Name': 'cc', 'Type': 'peer', 'Domain': 'bb.com', 'MspId': 'Orga814867ea5144de6b7bf4d08a13a134aMSP', 'Peers': [{'Name': 'peerf6e45c54838b4cfca8eda15baed2bece', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer3039a119ffdc44a9b4596d2382489333', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrga814867ea5144de6b7bf4d08a13a134a'}]}]}
# # a = {'ChannelId': 'channele0d0a757e3054a2299a62aa030afac69', 'BlockchainSign': '5a3c3a05a3b5426d90234c15b7bbd937', 'BlockchainName': 'aa', 'Algorithm': 'solo', 'CreateTime': '20190117140806', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channele0d0a757e3054a2299a62aa030afac69', 'ChannelConfigName': 'channele0d0a757e3054a2299a62aa030afac69.tx', 'Orderers': ['orderer0ee0c345c4664df0a504bd5e0159c546'], 'Orgs': [{'OrgId': 'orgd947978b579a4a008bf4565f5ba0b995', 'Peers': ['peere68e74e61b354008be08fa692dcaea13', 'peer077be60b514346bcb6c3c029100845f5']}]}], 'Orgs': [{'OrgId': 'orgb8a98f0449c9446bb02659d286710b35', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'cc.com', 'MspId': 'Orgb8a98f0449c9446bb02659d286710b35MSP', 'Orderers': [{'Name': 'orderer0ee0c345c4664df0a504bd5e0159c546', 'Url': '172.31.239.245:7050'}]}, {'OrgId': 'orgd947978b579a4a008bf4565f5ba0b995', 'Name': 'dd', 'Type': 'peer', 'Domain': 'cc.com', 'MspId': 'Orgd947978b579a4a008bf4565f5ba0b995MSP', 'Peers': [{'Name': 'peere68e74e61b354008be08fa692dcaea13', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer077be60b514346bcb6c3c029100845f5', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrgd947978b579a4a008bf4565f5ba0b995'}]}]}
# # a={'ChannelId': 'channelfbf647f6b3f14a2f9e11f87026ccacd3', 'BlockchainSign': '3cee3f1b5e134d9c9de2a857c0b70433', 'BlockchainName': 'zz', 'Algorithm': 'solo', 'CreateTime': '20190117140334', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channelfbf647f6b3f14a2f9e11f87026ccacd3', 'ChannelConfigName': 'channelfbf647f6b3f14a2f9e11f87026ccacd3.tx', 'Orderers': ['orderer794b1747ffe84fe2aafd811f9215ccea'], 'Orgs': [{'OrgId': 'org567cc76a74064e6d96719aa51697cac2', 'Peers': ['peerf011671d0ed0405a8f2f510ddc7760d6', 'peer22a2bc263582469aa6b227d234b68448']}]}], 'Orgs': [{'OrgId': 'org5911031a2fd940838fb2241702901d95', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'bb.com', 'MspId': 'Org5911031a2fd940838fb2241702901d95Org', 'Orderers': [{'Name': 'orderer794b1747ffe84fe2aafd811f9215ccea', 'Url': '172.31.239.245:7050'}]}, {'OrgId': 'org567cc76a74064e6d96719aa51697cac2', 'Name': 'cc', 'Type': 'peer', 'Domain': 'bb.com', 'MspId': 'Org567cc76a74064e6d96719aa51697cac2MSP', 'Peers': [{'Name': 'peerf011671d0ed0405a8f2f510ddc7760d6', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer22a2bc263582469aa6b227d234b68448', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrg567cc76a74064e6d96719aa51697cac2'}]}]}
# # a = {'ChannelId': 'channel19471794ffba4644b1cca24feb896bcf', 'BlockchainSign': '73dff0addad744e4984866b77194f389', 'BlockchainName': 'zz', 'Algorithm': 'solo', 'CreateTime': '20190117135417', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channel19471794ffba4644b1cca24feb896bcf', 'ChannelConfigName': 'channel19471794ffba4644b1cca24feb896bcf.tx', 'Orderers': ['orderer9b23b10dd55d487b8962008ae9eb1f92'], 'Orgs': [{'OrgId': 'org02772974f95b43ba95a3e44f424b9213', 'Peers': ['peerd5e37cb7c1c841f9b7124938939a7935', 'peer38eb77a56ce44d8fbe103e37e4c54e0d']}]}], 'Orgs': [{'OrgId': 'orgee406ee830e44e9fb07ed64623c71160', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'bb.com', 'MspId': 'Orgee406ee830e44e9fb07ed64623c71160Org', 'Orderers': [{'Name': 'orderer9b23b10dd55d487b8962008ae9eb1f92', 'Url': '172.31.239.245:7050'}]}, {'OrgId': 'org02772974f95b43ba95a3e44f424b9213', 'Name': 'cc', 'Type': 'peer', 'Domain': 'bb.com', 'MspId': 'Org02772974f95b43ba95a3e44f424b9213MSP', 'Peers': [{'Name': 'peerd5e37cb7c1c841f9b7124938939a7935', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer38eb77a56ce44d8fbe103e37e4c54e0d', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerCa'}]}]}
# # a = {'ChannelId': 'channele3f8b066ed8548eab8d2215c33c53516', 'BlockchainSign': '70dd6a8a932e493398b2189ab6536d2c', 'BlockchainName': 'zz', 'Algorithm': 'solo', 'CreateTime': '20190117113418', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channele3f8b066ed8548eab8d2215c33c53516', 'ChannelConfigName': 'channele3f8b066ed8548eab8d2215c33c53516.tx', 'Orderers': ['orderer33b276d0c828436c835b2b5338564703'], 'Orgs': [{'OrgId': 'org1a4796cb032f41b2b54b7943e54bd033', 'Peers': ['peera3e8fa188ed6400690b2932e2053d904', 'peer6e79d6b2bb6d42f79171eac528620512']}]}], 'Orgs': [{'OrgId': 'org7cbea60494804288bd163b61c6d4eeb4', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'bb.com', 'MspId': 'OrdererOrg', 'Orderers': [{'Name': 'orderer33b276d0c828436c835b2b5338564703', 'Url': '172.31.239.245:7050'}]}, {'OrgId': 'org1a4796cb032f41b2b54b7943e54bd033', 'Name': 'cc', 'Type': 'peer', 'Domain': 'bb.com', 'MspId': 'CcMSP', 'Peers': [{'Name': 'peera3e8fa188ed6400690b2932e2053d904', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer6e79d6b2bb6d42f79171eac528620512', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerCa'}]}]}
# # print(json.dumps(a))
# # class A(object):
# #
# #     def __init__(self):
# #         self.name = 5
# #         self.age = 6
# #
# #     def show(self):
# #         print('aa')
# #
# #
# # class B(A):
# #
# #     def __init__(self):
# #         self.school = 7
# #         super(B, self).__init__()
# #
# #     def show(self):
# #         print('bb')
# #         super(B, self).show()
# #
# # b = B()
# # print(b.school)
# # print(b.name)
# # b.show()
#
# # a = {1:2}
# # print(a.update({2:3}))
#
# # a = ['org1', 'org2', 'org11']
# # c = []
# # for i in a:
# #     b = int(i.lstrip('org'))
# #     c.append(b)
# # print(c)
# # print(max(c))
# # start = 1
# # b = start if start else ''
# # print(b)
# # import os
# # print(os.path.dirname(__file__))
# # a = '/a'
# # b = 'c'
# # c = os.path.join(a,b)
# # print(c)
# # print(os.path.exists('/home/zlp/PycharmProjects/baas_test'))
# a = {}
# # print(a)
# # a.update({1:2})
# # print(a)
# # a.items()
# from mongoengine import *
# connect('test', host='localhost', port=27017)
#
#
# class Student(Document):
#     name = StringField()
#
#
# class School(Document):
#     name = StringField()
#     students = ListField(ReferenceField(Student, reverse_delete_rule=PULL))


# s1 = Student('zhang')
# s2 = Student('wang')
# s1.save()
# s2.save()
# school = School('beida', students=[s1, s2])
# school.save()
# sc = School.objects.get(name='beida')
# students = sc.students
# for st in students:
#     st.delete()
# print(students)
# # school = School('1', '北大',['zhangsan'])
# # school.save()
# school = School.objects()
# school.delete()
# school.update(add_to_set__students=['li','wang','yang'])
# import json
# a = {'ChannelId': 'channel1', 'BlockchainSign': '02e3cdb03171455db605ef070c8102a7', 'BlockchainName': 'a', 'Algorithm': 'solo', 'CreateTime': '20190311141608', 'BlockChainCertPath': 'zz', 'TlsEnable': False, 'Channels': [{'ChannelId': 'channel1', 'ChannelName': 'b', 'ChannelConfigName': 'channel1.tx', 'Orderers': ['orderer.c.com'], 'Orgs': [{'OrgId': 'org1', 'Peers': ['peer0.org1.c.com', 'peer1.org1.c.com']}]}], 'Orgs': [{'OrgId': 'orderer', 'Name': 'orderer', 'Type': 'orderer', 'Domain': 'c.com', 'MspId': 'OrdererMSP', 'Orderers': [{'Name': 'orderer', 'Url': 'orderer.c.com:7050'}]}, {'OrgId': 'org1', 'Name': 'd', 'Type': 'peer', 'Domain': 'c.com', 'MspId': 'Org1MSP', 'Peers': [{'Name': 'peer0.org1.c.com', 'Url': '172.31.239.245:7150', 'EventUrl': '172.31.239.245:7250'}, {'Name': 'peer1.org1.c.com', 'Url': '172.31.239.245:7350', 'EventUrl': '172.31.239.245:7450'}], 'Cas': [{'Name': 'ca.org1.c.com', 'Url': '172.31.239.245:7550', 'EnrollId': 'admin', 'EnrollSecret': 'adminpw', 'ContainerName': 'ca_peerOrg1'}]}]}
# print(json.dumps(a))

# a = [7050+(10*i) for i in range(13)]
# # print(a)
# a = [1,2]
# b = [3]
# a.append(b)
# print(a)
# a = {1: 2, 3: 4}
# b = a.values()
# for _ in b:
#     print(_)
# print(type(b))
# import docker
# client = docker.APIClient(base_url="tcp://120.27.20.114:2375", version="auto", timeout=5)
# containers = client.containers()
# for container in containers:
#     container.get('a82faf3d3f38')

# import socket
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# c = []
# print(id(c))
# a = [2, 3, 5]
#
# c.extend(a)
# print(id(c))
# print(c)
# b = [2, 4, 5]
#
# c.extend(b)
# print(id(c))
#
# print(c)
#
# [7050, 7060, 7070, 7080, 7090, 7100]
# [7110, 7120, 7130, 7140, 7150, 7160]

# a = 0 and 0 or 6
# print(a)