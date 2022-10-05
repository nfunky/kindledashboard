import datetime
import json
import requests

#place the calendars you want to display here
CALENDERIDS=['primary','de.german#holiday@group.v.calendar.google.com']
CALENDERURL='https://www.googleapis.com/calendar/v3/calendars/{calendarid}/events'

weekdayMap = {	0:'Mo.',
				1:'Di.',
				2:'Mi.',
				3:'Do.',
				4:'Fr.',
				5:'Sa.',
				6:'So.'
			}

def getNewAccessTokenUsingRefreshToken():
    credentialdata = json.load(open('googlecalendar/credentials.json'))
    data = {
        "client_id": credentialdata['client_id'],
        "client_secret": credentialdata['client_secret'],
        "refresh_token": credentialdata['refresh_token'],
        "grant_type": "refresh_token"
    }
    accesstokenrequest=requests.post(url=credentialdata['token_uri'],data=data)
    print(accesstokenrequest.json())
    if "access_token" in accesstokenrequest.json():
        return accesstokenrequest.json()["access_token"]
    else:
        raise Exception('Missing Google API access_token: '+accesstokenrequest.text)

def getEvents(): 
    accessToken=getNewAccessTokenUsingRefreshToken()
    payload = {
        'timeMin': datetime.datetime.utcnow().date().isoformat() + 'T00:00:00.000000Z',
        'maxResults':6,
        'orderBy':'startTime',
        'singleEvents': True
    }
    events=[]
    for calendarid in CALENDERIDS:
        calendar_url=CALENDERURL.replace('{calendarid}',requests.utils.quote(calendarid))
        eventrequest=requests.get(calendar_url,params=payload,headers={'Authorization': 'Bearer {}'.format(accessToken)})
        if 'application/json' in eventrequest.headers.get('content-type'):
            events.extend(eventrequest.json()['items'])
            print('found %s upcoming event(s)'%len(events))
        if not events:
            print('No upcoming events found.')
            return
        
    allevents=[]
    for event in events:
         start = event['start'].get('dateTime', event['start'].get('date'))
         startdatetime=datetime.datetime.fromisoformat(start)
         weekday=getWeekdayForDate(datetime.datetime.timestamp(startdatetime))+' '
         start_formatted=startdatetime.strftime('%d.%m.%Y')
         if len(start)>10:  #with hour timestamp
             start_formatted=datetime.datetime.fromisoformat(start).strftime('%d.%m.%Y %H:%M')
         event_title=event['summary']
         if len(event_title)>24:
            event_title=event_title[:24]+'...'
         allevents.append({"date": weekday+start_formatted,
                            "startiso":start,
                            "day": getLabelForIcon(event_title,start_formatted[:2]),
                            "title": event_title,
                            "icon": getIconForTitle(event_title)})
    allevents=sorted(allevents, key=lambda k: k['startiso'])[:6]
    return allevents   

def render(replacementstring,output):
    svgcontent=open("googlecalendar/ui.svg","r").read()
    output=output.replace(replacementstring,str(svgcontent))
    events=getEvents()
    if events:
        if len(events)>0:
            output = output.replace("$CAL1", events[0]['day'])
            output = output.replace("$CLD1", events[0]['date'])
            output = output.replace("$CLT1", events[0]['title'])
            output = output.replace("$clicon1", events[0]['icon'])
        if len(events)>1:
            output = output.replace("$CAL2", events[1]['day'])
            output = output.replace("$CLD2", events[1]['date'])
            output = output.replace("$CLT2", events[1]['title'])
            output = output.replace("$clicon2", events[1]['icon'])
        if len(events)>2:
            output = output.replace("$CAL3", events[2]['day'])
            output = output.replace("$CLD3", events[2]['date'])
            output = output.replace("$CLT3", events[2]['title'])
            output = output.replace("$clicon3", events[2]['icon'])
        if len(events)>3:
            output = output.replace("$CAL4", events[3]['day'])
            output = output.replace("$CLD4", events[3]['date'])
            output = output.replace("$CLT4", events[3]['title'])
            output = output.replace("$clicon4", events[3]['icon'])
        if len(events)>4:
            output = output.replace("$CAL5", events[4]['day'])
            output = output.replace("$CLD5", events[4]['date'])
            output = output.replace("$CLT5", events[4]['title'])
            output = output.replace("$clicon5", events[4]['icon'])
        if len(events)>5:
            output = output.replace("$CAL6", events[5]['day'])
            output = output.replace("$CLD6", events[5]['date'])
            output = output.replace("$CLT6", events[5]['title'])
            output = output.replace("$clicon6", events[5]['icon'])
        output=hideAllUnusedCalendars(len(events),output)
    return output

def hideAllUnusedCalendars(eventcount,output):
    for i in range(6):
        if(i>eventcount-1):
            output = output.replace("$CAL"+str(i+1), '')
            output = output.replace("$CLD"+str(i+1), '')
            output = output.replace("$CLT"+str(i+1), '')
            output = output.replace("$clicon"+str(i+1), '')
    return output

def getIconForTitle(title):
    if any(x in title.lower() for x in ['birthday','geburtstag','cumple']):
        return "birthday"
    elif any(x in title.lower() for x in ['flight','stay at','flug']):
        return "travel"
    else:
        return "calendar"

def getWeekdayForDate(datetimestamp):
	weekday=weekdayMap[datetime.datetime.fromtimestamp(datetimestamp).weekday()]
	return weekday

def getLabelForIcon(title,label):
    if any(x in title.lower() for x in ['birthday','geburtstag']):
        return ""
    else:
        return label