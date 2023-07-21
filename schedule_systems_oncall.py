#!/usr/bin/env python3

"""
    Written by: Craig Sorensen

    This code is a proof of concept and is writen without warranty. Please test before using in production.

    This script is used to schedule users in an oncall rotation, for one week. They are schedule from Monday to Sunday on
    a Confluence calendar.

"""

import argparse
import re
import requests
import yaml
import os
import getpass
import json
import urllib

from datetime import datetime,timedelta

## Functions ##

def validate_date_is_monday(date):
    '''Validate inputted date string is a Monday'''
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    parsed_weekday = date_obj.strftime('%A')

    if parsed_weekday.lower() == "monday":
        return True
    return False

def validate_date(date_string):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'

    if re.match(date_pattern, date_string):
        return True
    else:
        return False

def validate_confluence_user(user):
    return requests.get(f"{confluence_url}/rest/api/user?username={user}", auth=(username,password))

def add_oncall_event_to_calender(payload):
    reqUrl = f'{confluence_url}/rest/calendar-services/1.0/calendar/events.json'

    what = urllib.parse.quote_plus(payload['what'])
    startDate = urllib.parse.quote_plus(payload['startDate']) # must be in DD-MMM-YYYY format
    startTime= '' #urllib.parse.quote_plus(arrow.utcnow().format('h:MM A'))
    endDate = urllib.parse.quote_plus(payload['endDate'])
    endTime = '' #urllib.parse.quote_plus(arrow.utcnow().shift(hours=+1).format('h:MM A'))
    allDayEvent = urllib.parse.quote_plus('True')
    where = urllib.parse.quote_plus('')
    url = urllib.parse.quote_plus('')
    description = urllib.parse.quote_plus(payload['description'])
    customEventTypeId = urllib.parse.quote_plus('')
    person=urllib.parse.quote_plus(payload['person'])
    subCalendarId = urllib.parse.quote_plus(payload['subCalendarId'])

    data = f'confirmRemoveInvalidUsers=false&childSubCalendarId=&customEventTypeId={customEventTypeId}&eventType=custom&isSingleJiraDate=false&originalSubCalendarId=&originalStartDate=&originalEventType=&originalCustomEventTypeId=&recurrenceId=&subCalendarId={subCalendarId}&uid=&what={what}&startDate={startDate}&endDate={endDate}&startTime={startTime}&endtime={endTime}&allDayEvent={allDayEvent}&rruleStr=&until=&editAllInRecurrenceSeries=true&where={where}&url={url}&description={description}&person={person}&userTimeZoneId=America%2FLos_Angeles'

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = requests.put(url=reqUrl,data=data,headers=headers,auth=(username,password))

## End Functions


## Main ##

# Variables
oncall_rotation = "user1,user2,user3,user4,user5,user6,user7" #Must be valid confluence users!
oncall_start_date = ""  #must be a monday
oncall_end_date = "" #must be a sunday
config_file = os.path.join(os.path.expanduser("~"), ".config", "set_oncall", "config.yaml")
username = None
password = None
confluence_url = "YOUR_CONFLUENCE_INSTANCE"
CONFLUENCE_SUBCALENDAR_ID = "YOUR_SUB_CALENAR_ID"
EVENT_DESCRIPTION = 'Configured via on-call scheduling script'
users = {}

# Configure Argparse
parser = argparse.ArgumentParser(description="Schedule on-call rotation.")
parser.add_argument('--start_date','-s',nargs='?',type=str,help="Monday of the FIRST week to be scheduled. Must be entered in YYYY-MM-DD format.")
parser.add_argument('--end_date','-e',nargs='?',type=str,help="Monday of the LAST week to be scheduled. Must be entered in YYYY-MM-DD format.")
parser.add_argument('--first','-f',nargs='?',type=str,help="Username of the person to be scheduled on the first week.")
parser.add_argument('--rotation','-r',nargs='?',type=str,help="Comma separated list of users")

args = parser.parse_args()

# User input validations
# Have user verify the on-call list is correct and give them a chance to update
if not args.rotation:
    while True:
        print(f"Current rotation is: {oncall_rotation}")
        validate_rotation = input("Is this correct? (y/[N]): ").lower()

        if validate_rotation == 'n':
            oncall_rotation = input("Enter new comma separated rotation: ")
            continue
        elif validate_rotation == 'y':
            break
        else:
            print(f"{validate_rotation} is not a valid input!")
            continue

oncall_rotation = [x.strip() for x in oncall_rotation.lower().split(',')]

# Choose who is to be scheduled first out of the on-call rotation
while True:
    if args.first:
        first_user = args.first
    else:
        first_user = input("Which user should be scheduled first? ").lower()
    if first_user in oncall_rotation:
        #reorganize the list
        index = oncall_rotation.index(first_user)
        oncall_rotation = oncall_rotation[index:] + oncall_rotation[:index]
        break
    else:
        print(f"{first_user} is not in the oncall rotation list, please select a user from the list!")
        continue

# Verify the start and end dates specified by the user
while True:
    if args.start_date:
        oncall_start_date = args.start_date
    else:
        oncall_start_date = input("Enter the Monday of the FIRST week to start scheduling [YYYY-MM-DD]: ")

    if validate_date(oncall_start_date) and validate_date_is_monday(oncall_start_date):
        oncall_start_date_obj = datetime.strptime(oncall_start_date, '%Y-%m-%d')
        break
    elif not validate_date(oncall_start_date):
        print('Invalid date, please enter in YYYY-MM-DD format!')
        continue
    else:
        print(f'{oncall_start_date} is not a Monday!')
        continue

while True:
    if args.end_date:
        oncall_end_date = args.end_date
    else:
        oncall_end_date = input("Enter the Monday of the LAST week of scheduling [YYYY-MM-DD]: ")

    if validate_date(oncall_end_date) and validate_date_is_monday(oncall_end_date):
        oncall_end_date_obj = datetime.strptime(oncall_end_date, '%Y-%m-%d')
        delta = oncall_end_date_obj - oncall_start_date_obj

        if delta.days <= 0:
            print("Error: End date is before start date!")
            quit()
        break
    elif not validate_date(oncall_end_date):
        print('Invalid date, please enter in YYYY-MM-DD format!')
        continue
    else:
        print(f'{oncall_end_date} is not a Monday!')
        continue

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

# confirm users are valid in confluence and collect their details
for user in oncall_rotation:
    r = validate_confluence_user(user)
    user_dict = json.loads(r.text)

    if 'statusCode' in user_dict:
        print(user_dict)
        if user_dict['statusCode'] == 404:
            print(f"Error: '{user}' could not be located in Confluence!")
            quit()

    users.update({user_dict['username']:user_dict})
# End user input validations

# Start actually doing work to schedule
start_date_obj = (datetime.strptime(oncall_start_date, '%Y-%m-%d'))

weeks_to_schedule = (delta.days)//7 + 1 # add one day to schedule the last week specified by the yser
print(f'Will schedule {weeks_to_schedule} weeks')

dup_list_count = weeks_to_schedule // len(oncall_rotation) + 1 # Add one to ensure list has enough elements during iteration
joined_list = []

for _ in range(dup_list_count):
    joined_list = joined_list + oncall_rotation

count = 0
for i in range(weeks_to_schedule):

    dyn_startDate = (start_date_obj + timedelta(weeks=count))

    payload = {
        'what':'on-call',
        'startDate':(start_date_obj + timedelta(weeks=count)).strftime('%d-%b-%Y'),
        'endDate':(dyn_startDate + timedelta(days=6)).strftime('%d-%b-%Y'),
        'description':EVENT_DESCRIPTION,
        'person':users[joined_list[i]]['userKey'],
        'subCalendarId':CONFLUENCE_SUBCALENDAR_ID
    }

    print(f"Scheduling {joined_list[i]} for {(start_date_obj + timedelta(weeks=count)).strftime('%d-%b-%Y')} to {(dyn_startDate + timedelta(days=6)).strftime('%d-%b-%Y')}")

    #Add event to calendar
    add_oncall_event_to_calender(payload)
    count = count + 1
