#!/usr/bin/python3

from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The ID of the spreadsheet.
from data import SPREADSHEET_ID

import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']



def login():
    # cd to where crediatials are stored

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    # os.chdir(cwd)
    return creds

creds = login()

def read_sheet(SPREADSHEET_ID='1iDE4SvDQFVPWnecllMPMQZlZceX4okxAJzf2Dc_Vtd0', 
               RANGE_NAME='Sheet1!B2:ZZ32'): # H999
    '''
    try 
    except HttpError as err:
        print(err)
    '''
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    df = pd.DataFrame(data=result['values'])
    return df


def get_long_expenses():
    import sys
    sys.path.insert(0, '../')
    import expenses as xp
    _, _, data_folder, _ = xp.get_folders()
    df = xp.get_expenses_list(data_folder)
    return df