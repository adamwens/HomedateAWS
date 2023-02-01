import re
import json
from datetime import datetime, timedelta
import random
from urllib.parse import quote
from urllib.request import urlopen
import base64

regex = '(^\+[0-9 ]{1,31}$)'

OTP_MSG_MEMBER = "來自 HOMEDATE 的約會通知：{} 接受了你的邀約\n你們的視訊約會將在 {} 開始，請於約會時間前10分鐘加入下列連結，進行線上視訊約會：{}\n\n更多約會詳情，請至 https://homedate.tw/ 瞭解"
OTP_MSG_TARGET = "來自 HOMEDATE 的約會通知：你接受了 {} 的邀約\n你們的視訊約會將在 {} 開始，請於約會時間前10分鐘加入下列連結，進行線上視訊約會：{}\n\n更多約會詳情，請至 https://homedate.tw/ 瞭解"
smsAccount = 'homedate168'
smsPassword = 'Homedate888'

def check_string(testString):
    if not testString:
        return False
    elif type(testString) != str:
        return False
    return True

def convert_timestamp(testString):
    timeStr = ''
    
    if not testString:
        return ''
    
    try:
        dt = datetime.fromtimestamp(int(testString))
        timeStr = dt.strftime("%m月%d日 %H:%M")
    except:
        print('parse time string failed, timestamp: ' + testString)
        pass
    
    return timeStr


def send_sms(phone, name, dateTime, dateLink, isMember):
    sendSuccess = False
    try:
        if isMember:
            message = OTP_MSG_MEMBER.format(name, dateTime, dateLink)
        else:
            message = OTP_MSG_TARGET.format(name, dateTime, dateLink)
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

def do_send(memberPhone, memberName, targetPhone, targetName, receiveTimeStr, dateTimeStr, dateLink):
    if not send_sms(memberPhone, targetName, dateTimeStr, dateLink, True):
        print('send member sms failed.')
        return 2
    if not send_sms(targetPhone, memberName, dateTimeStr, dateLink, False):
        print('send target sms failed.')
        return 2
    print('send sms ok.')
    
    return 0

def lambda_handler(event, context):
    try:
        bodyParam = json.loads(event['body'])
        print(str(bodyParam))
        memberPhone = bodyParam.get('memberPhone', '')
        memberName = bodyParam.get('memberName', '')
        targetPhone = bodyParam.get('targetPhone', '')
        targetName = bodyParam.get('targetName', '')
        receiveTime = bodyParam.get('receiveTime', '')
        dateTime = bodyParam.get('dateTime', '')
        dateLink = bodyParam.get('dateLink', '')
        receiveTimeStr = convert_timestamp(receiveTime)
        dateTimeStr = convert_timestamp(dateTime)
        if not check_string(memberPhone) or not check_string(memberName) or not check_string(targetPhone) or not check_string(targetName) or not check_string(dateLink) or not receiveTimeStr or not dateTimeStr:
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
        sendRet = do_send(memberPhone, memberName, targetPhone, targetName, receiveTimeStr, dateTimeStr, dateLink)
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
        'body': json.dumps({})
    }
