import json
import requests

ALL_TASKLISTS_URL='https://www.googleapis.com/tasks/v1/users/@me/lists'
ALL_TASKSFROMTASKLIST_URL='https://tasks.googleapis.com/tasks/v1/lists/{tasklist}/tasks'
TASKLISRNAME_URL='https://www.googleapis.com/tasks/v1/users/@me/lists/'
tasklistId='c2FCcFdSLVhmV2FGTlR2Sw'


def getNewAccessTokenUsingRefreshToken():
    credentialdata = json.load(open('notes/credentials.json'))
    data = {
        "client_id": credentialdata['client_id'],
        "client_secret": credentialdata['client_secret'],
        "refresh_token": credentialdata['refresh_token'],
        "grant_type": "refresh_token"
    }
    accesstokenrequest=requests.post(url=credentialdata['token_uri'],data=data)
    return accesstokenrequest.json()["access_token"]

def getTasklists():
    accessToken=getNewAccessTokenUsingRefreshToken()
    taskrequest=requests.get(ALL_TASKLISTS_URL,headers={'Authorization': 'Bearer {}'.format(accessToken)})
    tasklists=taskrequest.json()['items']
    return tasklists   

def getTaskslistName(tasklistId):
    url=TASKLISRNAME_URL+tasklistId
    accessToken=getNewAccessTokenUsingRefreshToken()
    taskrequest=requests.get(url,headers={'Authorization': 'Bearer {}'.format(accessToken)})
    name=taskrequest.json()['title']
    return name

def getTasksFromTasklists(tasklistId):    
    tasklisturl=ALL_TASKSFROMTASKLIST_URL.replace('{tasklist}',tasklistId)
    accessToken=getNewAccessTokenUsingRefreshToken()
    taskrequest=requests.get(tasklisturl,headers={'Authorization': 'Bearer {}'.format(accessToken)})
    tasks=taskrequest.json()['items']
    if not tasks:
        print('No tasks found.')
        return
    allTasks=[]
    for task in tasks:     
        if task['status']=='needsAction':
            allTasks.append({"lastupdated":task['updated'],
                             "title": task['title']})
    allTasks=sorted(allTasks, key=lambda i: i['lastupdated'])
    return allTasks   


def render(replacementstring,output):
    svgcontent=open("notes/ui.svg","r").read()
    output=output.replace(replacementstring,str(svgcontent))    
    listname=getTaskslistName(tasklistId)
    output = output.replace("$NOTE_TITLE",listname)
    tasks=getTasksFromTasklists(tasklistId)
    if tasks:
        if len(tasks)>0:
            output = output.replace("$NOTE1", tasks[0]['title'])
        if len(tasks)>1:
            output = output.replace("$NOTE2", tasks[1]['title'])
        if len(tasks)>2:
            output = output.replace("$NOTE3", tasks[2]['title'])            
        if len(tasks)>3:
            output = output.replace("$NOTE4", tasks[3]['title'])
        if len(tasks)>4:
            output = output.replace("$NOTE5", tasks[4]['title'])
        if len(tasks)>5:
            output = output.replace("$NOTE6", tasks[5]['title'])
        if len(tasks)>6:
            output = output.replace("$NOTE7", tasks[6]['title'])        
    nrOfTasks=0
    if not(tasks is None):
        nrOfTasks=len(tasks)
    output=hideAllUnusedTasks(nrOfTasks,output)
    return output

def hideAllUnusedTasks(taskcount,output):
    for i in range(7):
        if(i>taskcount-1):
            output = output.replace("$NOTE"+str(i+1), '')
    return output