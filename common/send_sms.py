from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
import urllib.parse

from common import API_KEY, TEMPLATE_ID


def send_sms(mobile, password):
    client = YunpianClient(apikey=API_KEY)
    tpl_value = urllib.parse.urlencode({'#domain#': 'http://baas.cnfoodchain.com', '#password#': password})   # 注意此处不要用sdk中的解码方法，超级傻逼
    param = {YC.MOBILE: mobile, YC.TPL_ID: TEMPLATE_ID, YC.TPL_VALUE: tpl_value}
    result = client.sms().tpl_single_send(param)
    return result


if __name__ == '__main__':
    send_sms(18932891818, 'zlp11111')
