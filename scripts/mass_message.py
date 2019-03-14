from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
import urllib.parse

from common import API_KEY, TEMPLATE_ID

PI_KEY = '77d482b5060dc4bf56bc16b2ce2b6752'
# TEMPLATE_ID = '2647048'


def send_sms(mobile):
    client = YunpianClient(apikey=API_KEY)
    # tpl_value = urllib.parse.urlencode({'#domain#': 'http://baas.cnfoodchain.com', '#password#': password})   # 注意此处不要用sdk中的解码方法，超级傻逼
    param = {YC.MOBILE: mobile, YC.TPL_ID: '2647048', YC.TPL_VALUE: {}}
    result = client.sms().tpl_single_send(param)
    return result


if __name__ == '__main__':
    result = send_sms(18932891818)
    print(result.detail())
