import jwt
import datetime


SECRET = '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83'


# 生成jwt 信息
def jwt_encoding(some, aud='webkit'):
    datetimeInt = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    # print(datetimeInt)
    option = {
        'exp': datetimeInt,
        'aud': aud,
        'info': some,
        'id': some['id']
    }
    token = jwt.encode(option, SECRET, algorithm='HS256').decode()
    return token


# 解析jwt 信息
def jwt_decoding(token, aud='webkit'):
    # payload = None
    try:
        payload = jwt.decode(token, SECRET, audience=aud, algorithms='HS256')

    except jwt.ExpiredSignatureError:
        payload = {"error_msg": "is timeout !!", "some": None}

    except Exception:
        payload = {"error_msg": "noknow exception!!", "some": None}

    return payload

#
# if __name__ == '__main__':
#     datetimeInt = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
#     option = {
#         'exp': datetimeInt,
#         'aud': 'webkit',
#         'info': {
#             'id':'12',
#             'name':'zlp'
#                  }
#     }
#     token = jwt.encode(option, SECRET, algorithm='HS256').decode()
#     print(token)
#     jwt = jwt.decode(token, SECRET, audience='webkit', algorithms='HS256')
#     print(jwt)