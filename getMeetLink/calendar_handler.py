import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

class Calendar:
    def __init__(self):
        creds = self.check_cred()
        if not creds:
            print("[Calendar] __init__ cred fail")
            return
        self.service = build('calendar', 'v3', credentials=creds)

    def insert(self, event):
        if not self.service:
            print("[Calendar] insert init service fail")
            return None
        
        try:
            events_result = self.service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
            print("[insert] insert event success")
            return events_result['hangoutLink']
        except Exception as e:
            print("[insert] insert event fail with error ", str(e))
            return None

    def check_cred(self):
        creds = None
        if os.path.exists('token.json'):
            print('get token.')
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print(creds)
        # If there are no (valid) credentials available, let the user log in.
        print('get no token.')
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('/tmp/token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds