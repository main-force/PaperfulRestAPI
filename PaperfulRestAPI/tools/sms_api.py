# 2022년 6월 22일 기준
# naver Sens API 사용 기준 코드


import base64
import hashlib
import hmac
import time
import requests
from PaperfulRestAPI.config.sms_service import SERVICE_ID, SECRET_KEY, ACCESS_KEY, FROM_PHONE_NUMBER

CONTENT_TYPE_MATCH = {
    'common': 'COMM',
    'advertisement': 'AD'
}

class MessageAPI:
    messages_to = []

    def __init__(self, messages_to_list):
        self.messages_to = messages_to_list

    def request_send_sms(self,
                 content,
                 content_type='common',
                 country_code='82',
                 ):
        method = 'POST'
        uri = f'/sms/v2/services/{SERVICE_ID}/messages'
        url = f'https://sens.apigw.ntruss.com{uri}'
        message_type = 'SMS'
        content_type = CONTENT_TYPE_MATCH[content_type]
        messages = _get_default_messages_object(self.messages_to)

        body = {
            'type': message_type,
            'contentType': content_type,
            'countryCode': country_code,
            'from': FROM_PHONE_NUMBER,
            'content': content,
            'messages': messages
        }

        headers = _get_headers(method, uri)
        response = requests.post(url, json=body, headers=headers)
        return response


def _get_default_messages_object(messages_to_list):
    messages_object = []
    for phone_number in messages_to_list:

        to_dict = {'to': f'0{phone_number}'}
        messages_object.append(to_dict)
    return messages_object


def _get_headers(method, uri):
    print(time.time())
    timestamp = str(int(time.time() * 1000))
    secret_key = bytes(SECRET_KEY, 'UTF-8')

    message = method + " " + uri + "\n" + timestamp + "\n" + ACCESS_KEY
    message = bytes(message, 'UTF-8')

    signature = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': ACCESS_KEY,
        'x-ncp-apigw-signature-v2': signature
    }

    return headers
