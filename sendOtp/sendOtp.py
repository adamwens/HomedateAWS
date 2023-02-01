import re
import json
from datetime import datetime, timedelta
import random
from urllib.parse import quote
from urllib.request import urlopen
import base64

regex = '(^\+[0-9 ]{1,31}$)'

OTP_MSG = "［HOMEDATE］會員驗證碼為{}，請於有效時間內完成驗證即可開始約會。若有疑問請加官方Line詢問！搜尋ID:@homedate"
smsAccount = 'homedate168'
smsPassword = 'Homedate888'
OTP_LENGTH = 6

def check_phone(phone):
    if not phone:
        return False
    elif type(phone) != str:
        return False
    return True

def send_sms(phone, otp):
    sendSuccess = False
    try:
        message = OTP_MSG.format(otp)
        print(message)
        message = quote(message)
        print(message)
        
        msg = 'username=' + smsAccount
        msg += '&password=' + smsPassword
        msg += '&mobile=' + phone
        msg += '&message=' + message
        url = 'http://api.twsms.com/json/sms_send.php?' + msg
        
        response = urlopen(url).read()
        print(str(response))
        ret = json.loads(response.decode('utf-8'))
        retCode = ret.get('code', '')
        if retCode == '00000':
            sendSuccess = True
    except:
        pass
    
    return sendSuccess

def do_send(phone):
    otp = ''.join(random.choice('0123456789') for x in range(OTP_LENGTH))
    print('generate otp: ' + otp)
    exTime = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    if not send_sms(phone, otp):
        print('send sms failed.')
        return 2, ''
    print('send sms ok.')
    
    return 0, str(base64.b64encode(otp.encode('utf8')))

def lambda_handler(event, context):
    try:
        bodyParam = json.loads(event['body'])
        print(str(bodyParam))
        phone = bodyParam.get('phone', '')
        if not check_phone(phone):
            context = {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'status': 'Bad Request', 'message': 'The parameter is incorrect.'})
            }
            return context
    except:
        context = {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'status': 'Bad Request', 'message': 'The parameter is incorrect.'})
        }
        return context
    
    sendRet = 1    # 0/1/2 => pass/unknown/sendFailed
    try:
        sendRet, data = do_send(phone)
    except:
        pass
    
    if sendRet == 1:
        context = {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'status': 'Forbidden', 'message': 'Temporary error. Please try again later.'})
        }
        return context
    elif sendRet == 2:
        context = {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'status': 'Forbidden', 'message': 'Send SMS failed. Please check your phone number of try again later.'})
        }
        return context
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'data': data})
    }
