
class FileRequest(object):
    pass


class Requester(object):
    def __init__(self):
        pass

    def file_request(self, file, body, token=None, verify=False):
        json_data = json.dumps(body)
        data = MultipartEncoder(
            fields={
                'Body': json_data,
                'Files': (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')
            }
        )
        headers = {
            'Content-type': data.content_type,
            'Private-Header': 'token={};userId={}'.format(token, user_id),
        }

        try:
            response = requests.post(api, data=data, headers=headers, verify=False)
        except Exception as e:
            logger.error(e)
            return False
        content = response.text
        logger.info('content:' + content)
        obj_data = json.loads(content)
        return obj_data

    def json_request(self):
        pass


class Sender(object):
    def __init__(self):
        self.token = ''

    def get_token(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

    def add_user(self):
        pass

    def add_org(self):
        pass
