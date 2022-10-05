from msilib.schema import Error
from flask import Flask,request,send_file,Response
import requests
import os
import datetime
import locale
import codecs
import traceback
import googlecalendar.controller
# import mail.controller 	uncomment this if you want to display your smart home information 
import notes.controller

locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")

app = Flask(__name__)

SVG_FILE = "kindledashboard_preprocess.svg" 
SVG_OUTPUT = "kindledashboard_output.svg" 
TMP_OUTPUT = "kindledashboard_tmp.png"
OUTPUT = "kindledashboard.png"
CITY="Düsseldorf"
LOC="Kitchen"

SCRIPTFILE="dashboardscript.sh"
LOGFILE="logs.log"

WEATHERENDPOINT="https://api.openweathermap.org/data/2.5/onecall"

payload = {	'lat': 51.212843, 
			'lon': 6.765367,
			'appid': '3d797b5917cf843f4c9dbc4af1790ec0',	#update your app key generated on openweathermap.org, this one will not work
			'units': 'metric',
			'exclude': 'minutely',
			'lang':'de'
			}

def _exec(cmd):
    rc = os.system(cmd)
    if (rc != 0):
        print("`%s` failed with error %d" % (cmd, rc))
        exit(rc)

def getWeatherdata():
	return requests.get(WEATHERENDPOINT,params=payload).json()

def getBattery(clientname):
    battery="100%"
    batteryline=""
    if os.path.isfile(LOGFILE):
        with open(LOGFILE, 'r',encoding="utf-8") as file:
            for line in file:
                line=line.rstrip()
                print(line)
                if "Batteriezustand:" in line and clientname in line:
                    batteryline=line
                if len(batteryline)>2:
                    battery=batteryline[-4:]
    return battery

weekdayMap = {	0:'Mo.',
				1:'Di.',
				2:'Mi.',
				3:'Do.',
				4:'Fr.',
				5:'Sa.',
				6:'So.'
			}
clientToLocMap = {	'kt2-kitchen':'Küche',
					'kindle-office':'Büro'
			}
iconMap = {		"11d":'Thunder',
				'09d':'Clouds',
				'10d':'Rain',
				'10n':'Rain',
				'09d':'Rain',
				'09n':'Rain',
				'13d':'Snow',
				'13n':'Snow',
				'50d':'Fog',
				'50n':'Fog',
				'01d':'Clear',
				'01n':'ClearNight',
				'02d':'FewClouds',
				'02n':'FewCloudsNight',
				'03d':'Clouds',
				'03n':'Clouds',
				'04d':'Clouds',
				'04n':'Clouds',
			}

def getWeekdayForDate(datetimestamp):
	weekday=weekdayMap[datetime.datetime.fromtimestamp(datetimestamp).weekday()]
	return weekday

def getNextHours(weatherdata):
	temps=[]
	for weatherhour in weatherdata['hourly'][:11]:
		rainqty=0
		if 'rain' in weatherhour:
			rainqty=weatherhour['rain']['1h']
		temps.append({'time':weatherhour['dt'],'temp':weatherhour['temp'],'rain':rainqty})
	return temps

def getIconsForNextHours(weatherdata):
	icons=list(map(lambda hour:iconMap.get(hour['weather'][0]['icon']),weatherdata['hourly'][:11]))	
	return icons

def getAlerts(weatherdata):
	results=''
	if 'alerts' in weatherdata:
		alerts=list(map(lambda alert:alert['event'].capitalize(),weatherdata['alerts']))
		results=", ".join(alerts)
	return results

def getReadableLocation(client):
	loc='Küche'	
	if client is not None:
		loc=clientToLocMap.get(client)
		if loc is None:
			loc='Küche'
	return loc

def refreshDashboard(client):
	try:
		print("Starting new file generation at "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		output = codecs.open(SVG_FILE, "r", encoding="utf-8").read()	
		weatherdata=getWeatherdata()	
		battery=getBattery(client)	
		output = output.replace("$TEMP", str(round(weatherdata["current"]["temp"],1))+'°C')
		output = output.replace("$WEATHERCONDITION", str(weatherdata["current"]["weather"][0]["description"]))
		output = output.replace("$ID0", iconMap.get(weatherdata["current"]["weather"][0]["icon"]))
		output = output.replace("$wind", str(int(round(weatherdata["current"]["wind_speed"]*3.6,0))))	#convert to km/h
		output = output.replace("$humidity", str(weatherdata["current"]["humidity"])+'%')
		rainmm="0 mm"
		if "rain" in weatherdata['daily'][0]:
			rainmm=str(weatherdata['daily'][0]["rain"])+' mm'
		output = output.replace("$rain", rainmm)
		output = output.replace("$SRT", datetime.datetime.fromtimestamp(weatherdata["current"]["sunrise"]).strftime("%H:%M"))
		output = output.replace("$SST",  datetime.datetime.fromtimestamp(weatherdata["current"]["sunset"]).strftime("%H:%M"))
		output = output.replace("$TIME", datetime.datetime.fromtimestamp(weatherdata["current"]["dt"]).strftime("%H:%M"))
		output = output.replace("$CITY", CITY)

		#chart for next hours
		temps=getNextHours(weatherdata)
		iconsNextHours=getIconsForNextHours(weatherdata)
		mintemp=min(temps,key=lambda x:x['temp'])
		pixelPerTemperature=3

		pathhour0=(temps[0]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour1=(temps[1]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour2=(temps[2]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour3=(temps[3]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour4=(temps[4]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour5=(temps[5]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour6=(temps[6]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour7=(temps[7]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour8=(temps[8]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour9=(temps[9]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)
		pathhour10=(temps[10]['temp']*pixelPerTemperature-mintemp['temp']*pixelPerTemperature*0.7)*(-1)

		rainpathhour0=temps[0]['rain']*(10)
		rainpathhour1=temps[1]['rain']*(10)
		rainpathhour2=temps[2]['rain']*(10)
		rainpathhour3=temps[3]['rain']*(10)
		rainpathhour4=temps[4]['rain']*(10)
		rainpathhour5=temps[5]['rain']*(10)
		rainpathhour6=temps[6]['rain']*(10)
		rainpathhour7=temps[7]['rain']*(10)
		rainpathhour8=temps[8]['rain']*(10)
		rainpathhour9=temps[9]['rain']*(10)
		rainpathhour10=temps[10]['rain']*(10)

		output = output.replace("$PTHHOURLY0", str(pathhour0))
		output = output.replace("$PTHHOURLY1", str(pathhour1))
		output = output.replace("$PTHHOURLY2", str(pathhour2))
		output = output.replace("$PTHHOURLY3", str(pathhour3))
		output = output.replace("$PTHHOURLY4", str(pathhour4))
		output = output.replace("$PTHHOURLY5", str(pathhour5))
		output = output.replace("$PTHHOURLY6", str(pathhour6))
		output = output.replace("$PTHHOURLY7", str(pathhour7))
		output = output.replace("$PTHHOURLY8", str(pathhour8))
		output = output.replace("$PTHHOURLY9", str(pathhour9))
		output = output.replace("$PTHHOURLYX", str(pathhour10))

		output = output.replace("$RAINPTHHOURLY0", str(rainpathhour0))
		output = output.replace("$RAINPTHHOURLY1", str(rainpathhour1))
		output = output.replace("$RAINPTHHOURLY2", str(rainpathhour2))
		output = output.replace("$RAINPTHHOURLY3", str(rainpathhour3))
		output = output.replace("$RAINPTHHOURLY4", str(rainpathhour4))
		output = output.replace("$RAINPTHHOURLY5", str(rainpathhour5))
		output = output.replace("$RAINPTHHOURLY6", str(rainpathhour6))
		output = output.replace("$RAINPTHHOURLY7", str(rainpathhour7))
		output = output.replace("$RAINPTHHOURLY8", str(rainpathhour8))
		output = output.replace("$RAINPTHHOURLY9", str(rainpathhour9))
		output = output.replace("$RAINPTHHOURLYX", str(rainpathhour10))

		output = output.replace("$POSTEMPHOURLY1", str(pathhour0+10))
		output = output.replace("$POSTEMPHOURLY2", str(pathhour1+10))
		output = output.replace("$POSTEMPHOURLY3", str(pathhour2+10))
		output = output.replace("$POSTEMPHOURLY4", str(pathhour3+10))
		output = output.replace("$POSTEMPHOURLY5", str(pathhour4+10))
		output = output.replace("$POSTEMPHOURLY6", str(pathhour5+10))
		output = output.replace("$POSTEMPHOURLY7", str(pathhour6+10))
		output = output.replace("$POSTEMPHOURLY8", str(pathhour7+10))
		output = output.replace("$POSTEMPHOURLY9", str(pathhour8+10))
		output = output.replace("$POSTEMPHOURLYX", str(pathhour9+10))	

		output = output.replace("$PTHTEMPHOURLY0", str(int(round(temps[0]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY1", str(int(round(temps[1]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY2", str(int(round(temps[2]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY3", str(int(round(temps[3]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY4", str(int(round(temps[4]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY5", str(int(round(temps[5]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY6", str(int(round(temps[6]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY7", str(int(round(temps[7]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY8", str(int(round(temps[8]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLY9", str(int(round(temps[9]['temp'],1))))
		output = output.replace("$PTHTEMPHOURLYX", str(int(round(temps[10]['temp'],1))))

		output = output.replace("$HOUR1", datetime.datetime.fromtimestamp(temps[0]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR2", datetime.datetime.fromtimestamp(temps[1]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR3", datetime.datetime.fromtimestamp(temps[2]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR4", datetime.datetime.fromtimestamp(temps[3]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR5", datetime.datetime.fromtimestamp(temps[4]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR6", datetime.datetime.fromtimestamp(temps[5]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR7", datetime.datetime.fromtimestamp(temps[6]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR8", datetime.datetime.fromtimestamp(temps[7]['time']).strftime("%H:%M"))
		output = output.replace("$HOUR9", datetime.datetime.fromtimestamp(temps[8]['time']).strftime("%H:%M"))

		#icons per hour
		output = output.replace("$ICONHR1", iconsNextHours[0])
		output = output.replace("$ICONHR2", iconsNextHours[1])
		output = output.replace("$ICONHR3", iconsNextHours[2])
		output = output.replace("$ICONHR4", iconsNextHours[3])
		output = output.replace("$ICONHR5", iconsNextHours[4])
		output = output.replace("$ICONHR6", iconsNextHours[5])
		output = output.replace("$ICONHR7", iconsNextHours[6])
		output = output.replace("$ICONHR8", iconsNextHours[6])
		output = output.replace("$ICONHR9", iconsNextHours[7])

		#alerts
		alerts=getAlerts(weatherdata)
		output = output.replace("$alertlist", alerts)
		if len(alerts)>0:
			output = output.replace("$isAlert", 'Alert')

		#day1
		output = output.replace("$TD1", str(round(weatherdata['daily'][0]["temp"]["day"],1))+'°C')
		output = output.replace("$WT1", getWeekdayForDate(weatherdata['daily'][0]["dt"]))
		output = output.replace("$TLD1", str(round(weatherdata['daily'][0]["temp"]["night"],1))+'°C')
		output = output.replace("$D1", datetime.datetime.fromtimestamp(weatherdata['daily'][0]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID1", iconMap.get(weatherdata["daily"][0]["weather"][0]["icon"]))

		#day2
		output = output.replace("$TD2", str(round(weatherdata['daily'][1]["temp"]["day"],1))+'°C')
		output = output.replace("$WT2", getWeekdayForDate(weatherdata['daily'][1]["dt"]))
		output = output.replace("$TLD2", str(round(weatherdata['daily'][1]["temp"]["night"],1))+'°C')
		output = output.replace("$D2", datetime.datetime.fromtimestamp(weatherdata['daily'][1]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID2", iconMap.get(weatherdata["daily"][1]["weather"][0]["icon"]))

		#day3
		output = output.replace("$TD3", str(round(weatherdata['daily'][2]["temp"]["day"],1))+'°C')
		output = output.replace("$WT3", getWeekdayForDate(weatherdata['daily'][2]["dt"]))
		output = output.replace("$TLD3", str(round(weatherdata['daily'][2]["temp"]["night"],1))+'°C')
		output = output.replace("$D3", datetime.datetime.fromtimestamp(weatherdata['daily'][2]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID3", iconMap.get(weatherdata["daily"][2]["weather"][0]["icon"]))
		#day4
		output = output.replace("$TD4", str(round(weatherdata['daily'][3]["temp"]["day"],1))+'°C')
		output = output.replace("$WT4", getWeekdayForDate(weatherdata['daily'][3]["dt"]))
		output = output.replace("$TLD4", str(round(weatherdata['daily'][3]["temp"]["night"],1))+'°C')
		output = output.replace("$D4", datetime.datetime.fromtimestamp(weatherdata['daily'][3]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID4", iconMap.get(weatherdata["daily"][3]["weather"][0]["icon"]))

		#day5
		output = output.replace("$TD5", str(round(weatherdata['daily'][4]["temp"]["day"],1))+'°C')
		output = output.replace("$WT5", getWeekdayForDate(weatherdata['daily'][4]["dt"]))
		output = output.replace("$TLD5", str(round(weatherdata['daily'][4]["temp"]["night"],1))+'°C')
		output = output.replace("$D5", datetime.datetime.fromtimestamp(weatherdata['daily'][4]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID5", iconMap.get(weatherdata["daily"][4]["weather"][0]["icon"]))

		#day6
		output = output.replace("$TD6", str(round(weatherdata['daily'][5]["temp"]["day"],1))+'°C')
		output = output.replace("$WT6", getWeekdayForDate(weatherdata['daily'][5]["dt"]))
		output = output.replace("$TLD6", str(round(weatherdata['daily'][5]["temp"]["night"],1))+'°C')
		output = output.replace("$D6", datetime.datetime.fromtimestamp(weatherdata['daily'][5]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID6", iconMap.get(weatherdata["daily"][5]["weather"][0]["icon"]))

		#day5
		output = output.replace("$TD7", str(round(weatherdata['daily'][6]["temp"]["day"],1))+'°C')
		output = output.replace("$WT7", getWeekdayForDate(weatherdata['daily'][6]["dt"]))
		output = output.replace("$TLD7", str(round(weatherdata['daily'][6]["temp"]["night"],1))+'°C')
		output = output.replace("$D7", datetime.datetime.fromtimestamp(weatherdata['daily'][6]["dt"]).strftime("%d.%m."))
		output = output.replace("$ID7", iconMap.get(weatherdata["daily"][6]["weather"][0]["icon"]))

		#calendar
		print('rendering calendar')
		output=googlecalendar.controller.render('$GOOGLECALENDAR',output)	
		#mail - disabled by default, adjust the settings to your setup before uncommenting the following 2 lines
		#print('rendering mail')
		#output=mail.controller.render('$MAILNOTIFICATION',output)	
		#notes
		print('rendering notes')
		output=notes.controller.render('$NOTES',output)
		
		
		output = output.replace("$TSTMP", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))	
		output = output.replace("$LOC", getReadableLocation(client))
		output = output.replace("$BTRY", battery)
		codecs.open(SVG_OUTPUT, "w", encoding="utf-8").write(output)
		print("Generating new file at "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		#_exec("inkscape --export-width=600 --export-height=800 --export-background=WHITE --export-type=png --export-filename=%s %s" % (TMP_OUTPUT, SVG_OUTPUT))
		_exec("inkscape --without-gui --export-width 600 --export-height 800 --export-background=WHITE --export-png %s %s 1>/dev/null 2>&1" % (TMP_OUTPUT, SVG_OUTPUT))
		print("Generated temporal file")
		_exec("pngcrush -c 0 -ow %s 1>/dev/null 2>&1" % TMP_OUTPUT)
		_exec("mv -f '%s' '%s'" % (TMP_OUTPUT, OUTPUT))
		_exec("rm -f '%s'" % SVG_OUTPUT)
		print("Saved new file in location "+SVG_OUTPUT)

@app.route("/kindledashboard")
def sendDashboard():	
	try:
		client=request.args.get('client')
		if client is None:
			client='kt2-kitchen'
		refreshDashboard(client)
		return send_file(OUTPUT)
	except Exception as e:		
		print("".join(traceback.TracebackException.from_exception(e).format()))
		return "".join(traceback.TracebackException.from_exception(e).format()),500

@app.route("/kindledashboard/logs",methods=["GET","POST"])
def handleDashboardlogs():
	if request.method == 'POST':
		if os.path.exists(LOGFILE):
			if os.stat(LOGFILE).st_size>10000000:
				os.remove(LOGFILE)		
		with open(LOGFILE, "ab+") as logs:
			logs.write(request.data)
			return "",201
	else:
		action=request.args.get('action')
		try:			
			if os.path.exists(LOGFILE):
				if action=='download':
					return send_file(LOGFILE)
				else:
					return Response(open(LOGFILE, 'r').readlines(), mimetype='text/plain',status=200)	
			return "<h1>No logs created yet.</h1>",204
		except Exception as e:
			print("".join(traceback.TracebackException.from_exception(e).format()))
			return "".join(traceback.TracebackException.from_exception(e).format()),500

@app.route("/kindledashboard/"+SCRIPTFILE)
def sendDashboardscript():
	try:
		if os.path.exists(SCRIPTFILE):
			return send_file(SCRIPTFILE)
		else:
			return "",204
	except Exception as e:		
		print("".join(traceback.TracebackException.from_exception(e).format()))
		return "".join(traceback.TracebackException.from_exception(e).format()),500

if __name__ == '__main__':
    app.run(debug=True, port=5000)