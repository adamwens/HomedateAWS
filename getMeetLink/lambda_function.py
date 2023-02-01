import re
import json
import uuid
import random
from datetime import datetime, timedelta
from calendar_handler import Calendar

MEETING_INTERVAL = 40 # 40 mins

regex_phone = '(^\+[0-9 ]{1,31}$)'
regex_otp = '^[0-9]{6}$'

def check_name(name):
    if not name:
        return False
    if type(name) != str:
        return False
    if len(name) >= 256:
        return False
    return True
    
def check_time(time):
    if not time:
        return False
    elif type(time) != int:
        return False
    try:
        if datetime.utcfromtimestamp(time) <= datetime.now():
            return False
    except:
        return False
    return True

def generate_event(name, memberEmail, targetEmail, date_time: int):
    if not memberEmail or not targetEmail or not date_time:
        print("[generate_event] parameter is empty")
        return None
    
    request_id = str(uuid.uuid1())
    local_date = datetime.fromtimestamp(date_time)
    end_date = local_date + timedelta(minutes=MEETING_INTERVAL)
    local_str = datetime.strftime(local_date,"%Y-%m-%dT%H:%M:%S")
    end_str = datetime.strftime(end_date,"%Y-%m-%dT%H:%M:%S")

    title = '|HOMEDATE 視訊約會|'
    description = "歡迎加入官方Line帳號：@homedate\n"
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': local_str,
            'timeZone': 'Asia/Taipei',
        },
        'end': {
            'dateTime': end_str,
            'timeZone': 'Asia/Taipei',
        },
        'attendees': [],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'conferenceData': {
            'createRequest': {
                'requestId': request_id,
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        },
        'guestsCanSeeOtherGuests': False
    }
    
    event['attendees'].append({'email': memberEmail})
    event['attendees'].append({'email': targetEmail})
    
    return event

def do_get_meet_link(name, memberEmail, targetEmail, time):
    link = ''
    
    event = generate_event(name, memberEmail, targetEmail, time)
    
    if not event:
        print('event failed.')
        return 0, link
    print('event ok.')
    
    calendar = Calendar()
    print('calendar ok.')
    link = calendar.insert(event)
    print('calendar.insert ok, link: ' + str(link))
    if not link:
        return 0, link
    
    return 0, link

def lambda_handler(event, context):
    try:
        bodyParam = json.loads(event['body'])
        print(str(bodyParam))
        name = bodyParam.get('name', '')
        memberEmail = bodyParam.get('memberEmail', '')
        targetEmail = bodyParam.get('targetEmail', '')
        time = int(bodyParam.get('time', 0))
        if not check_time(time):
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
    
    getMeetLinkRet = 1    # 0/1 => pass/unknown
    link = ''
    try:
        getMeetLinkRet, link = do_get_meet_link(name, memberEmail, targetEmail, time)
    except:
        pass
    
    if getMeetLinkRet == 1 or not link:
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
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'dateLink': link})
    }
