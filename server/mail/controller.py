import datetime
import requests

HASSURL='http://192.168.178.63:8123/api/states/'
HASSTOKEN='YOUR_HASSREFRESHTOKEN'
HASSVARISMAIL="var.ismail"
HASSVARTIMESTAMP="var.mailtimestamp"

NOMAILSTRING='Keine Post'
MAILSTRING='Neue Post'

def getLatestMailStatus():    
    headers = {
        "Authorization": "Bearer "+HASSTOKEN,
        "content-type": "application/json",
    }
    response = requests.get(url=HASSURL+HASSVARISMAIL, headers=headers).json()
    ismail=response['state']
    timestamp=response['last_changed']
    return {
        "ismail":ismail,
        "timestamp":timestamp
    }


def render(replacementstring,output):
    svgcontent=open("mail/ui.svg","r").read()
    output=output.replace(replacementstring,str(svgcontent))
    mailstatus=getLatestMailStatus()
    mailstring=NOMAILSTRING
    mailicon="nomail"
    mailtimestamp=''
    stringprefix=''
    if mailstatus['ismail']=='True':
        mailicon="mail"
        mailstring=MAILSTRING
        stringprefix=""
    mailtimestamp=stringprefix+datetime.datetime.fromisoformat(mailstatus['timestamp']).strftime("%d.%m. %H:%M")

    output = output.replace("$MAILICON",mailicon)
    output = output.replace("$MAILSTATUSSTRING",mailstring)
    output = output.replace("$MAILTIMESTAMPSTRING",mailtimestamp)
    return output
