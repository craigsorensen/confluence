#!/usr/bin/env python3

"""
    Written by: Craig Sorensen

    This code is a proof of concept and is writen without warranty. Please test before using in production.

    This script is used to find the next on scheduled oncall user, on an oncall calendar hosted in Confluence.
"""

import getpass
import os
import yaml
import requests
import urllib
import json

from datetime import timedelta,datetime,date


# Variables
config_file = os.path.join(os.path.expanduser("~"), ".config", "set_oncall", "config.yaml")
username = None
password = None
confluence_url = "YOUR_CONFLUENCE_INSTANCE"
CONFLUENCE_SUBCALENDAR_ID = "YOUR_SUB_CALENAR_ID"


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def get_systems_oncall_events(start_date):
    start = urllib.parse.quote_plus(f'{start_date}Z')
    end = urllib.parse.quote_plus(f'{start_date}Z')

    reqUrl = f'{confluence_url}/rest/calendar-services/1.0/calendar/events.json?subCalendarId={CONFLUENCE_SUBCALENDAR_ID}&userTimeZoneId=US%2FPacific&start={start}&end={end}'

    r = requests.get(url=reqUrl,auth=(username,password))

    return json.loads(r.text)

next_monday = next_weekday(date.today(), 0)
#print(f'Next Monday: {next_monday.year}')

# convert to the correct time format - ref: https://pynative.com/python-iso-8601-datetime/
dt = datetime.now()
dt = dt.replace(year=next_monday.year, month=next_monday.month, day=next_monday.day,microsecond=0).isoformat()

# check if API credentials have already been supplied, if not get them
if username is None and password is None:
    try:
        with open(config_file) as f:
            creds = yaml.safe_load(f)
            username = creds['user']
            password = creds['password']
    except:
        print(f"Unable to open config file: {config_file}")
        username = input("Please enter confluence service account: ")
        password = getpass.getpass

events = get_systems_oncall_events(dt)
next_oncall_event = events['events'][0]


#verify first event is next Monday's oncall event
if next_oncall_event['localizedStartDate'] == next_monday.strftime('%d-%b-%Y'):
    print(f"Next on-call is: {next_oncall_event['invitees'][0]['name']}")
