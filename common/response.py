#!/usr/bin/python

# coding=utf-8
CODE_OK = 200
CODE_CREATED = 201
CODE_NO_CONTENT = 204
CODE_BAD_REQUEST = 400
CODE_FORBIDDEN = 403
CODE_NOT_FOUND = 404
CODE_METHOD_NOT_ALLOWED = 405
CODE_NOT_ACCEPTABLE = 406
CODE_CONFLICT = 409

response_ok = {
    "stat": CODE_OK,
    "msg": "成功",
    "data": {}
}

response_fail = {
    "stat": CODE_BAD_REQUEST,
    "msg": "",
    "data": {}
}


def make_ok_resp(data=""):
    response_ok["data"] = data
    return response_ok, CODE_OK


def make_fail_resp(error="Invalid request", data="", code=CODE_BAD_REQUEST):
    response_fail['stat'] = code
    response_fail["msg"] = error
    response_fail["data"] = data
    return response_fail, CODE_BAD_REQUEST
