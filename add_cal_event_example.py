#!/usr/bin/env python3

import requests
import getpass
import urllib
import json

from datetime import datetime

## Functions ##
def get_confluence_user_id(user):
    r = requests.get(f"{CONFLUENCE_URL}/rest/api/user?username={user}", auth=(username,password))
    user_dict = json.loads(r.text)
    return user_dict['userKey']


def add_oncall_event_to_calender(payload):
    reqUrl = f'{CONFLUENCE_URL}/rest/calendar-services/1.0/calendar/events.json'

    what = urllib.parse.quote_plus(payload['what'])
    startDate = urllib.parse.quote_plus(payload['startDate']) # must be in DD-MMM-YYYY format
    startTime= '' #urllib.parse.quote_plus(arrow.utcnow().format('h:MM A'))
    endDate = urllib.parse.quote_plus(payload['startDate'])
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
    print(res.text)

## End Functions


## Main ##

# Variables
CONFLUENCE_URL= "YOUR_CONFLUENCE_URL"
CONFLUENCE_SUBCALENDAR_ID = "YOUR_SUB_CAL_ID"

start_date = input("Please enter event start date (YYYY-MM-DD): ")
event_title = input("Please enter event title: ")
event_description = input("Please enter event description: ")
assigned_user = input("Please enter who the event is assigned to(must be valid concluence user): ")

username = input("Please enter confluence account: ")
password = getpass.getpass()

# Get dates from user, in YYYY-MM-DD format. Will be converted to confluence friendly date later
start_date_obj = (datetime.strptime(start_date, '%Y-%m-%d'))
end_date_obj = (datetime.strptime(start_date, '%Y-%m-%d'))

payload = {
    'what':event_title,
    'startDate':(start_date_obj).strftime('%d-%b-%Y'),
    #'endDate':(end_date_obj).strftime('%d-%b-%Y'),
    'description':event_description,
    'person':get_confluence_user_id(assigned_user),
    'subCalendarId':CONFLUENCE_SUBCALENDAR_ID
}
print(f"Scheduling event for {assigned_user}")
#Add event to calendar
add_oncall_event_to_calender(payload)
