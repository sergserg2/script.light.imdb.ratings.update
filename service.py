# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################

import xbmc, xbmcaddon, xbmcvfs
import time, _strptime
from datetime import date, datetime, timedelta

addonID       = "script.light.imdb.ratings.update"
addonSettings = xbmcaddon.Addon( addonID )
addonName     = addonSettings.getAddonInfo( "name" )
addonProfile  = xbmc.translatePath( addonSettings.getAddonInfo( "profile" ) ).decode('utf-8')
addonLanguage = addonSettings.getLocalizedString

if not xbmcvfs.exists( addonProfile ): xbmcvfs.mkdir( addonProfile )

WeekDay       = addonSettings.getSetting( "WeekDay" )
DayTime       = addonSettings.getSetting( "DayTime" )
WeekText      = [addonLanguage(32828),addonLanguage(32829),addonLanguage(32830),addonLanguage(32831),addonLanguage(32832),addonLanguage(32833),addonLanguage(32834)]

def doUnicode( textMessage ):
    try: textMessage = unicode( textMessage, 'utf-8' )
    except: pass
    return textMessage

def doNormalize( textMessage ):
     try: textMessage = unicodedata.normalize( 'NFKD', doUnicode( textMessage ) ).encode( 'utf-8' )
     except: pass
     return textMessage

def defaultLog( textMessage ):
     xbmc.log( "[%s] - %s" % ( addonName, doNormalize( textMessage ) ) )
	 
def UpdateSchedule():
     day_difference = date.weekday( date.today() ) - int( WeekDay )
     if day_difference < 0:
		day_difference = -day_difference
     elif day_difference > 0:
		day_difference = 7-day_difference
     elif day_difference == 0 and time.strftime("%H:%M:%S") >= DayTime:
		day_difference = day_difference+7	 
     nextrun = datetime.now() + timedelta( days = day_difference )
     nextruntime = DayTime
     addonSettings.setSetting( "ScheduledWeekDay", datetime.strftime(nextrun, "%Y-%m-%d") )
     defaultLog( addonLanguage(32655) % ( datetime.strftime(nextrun, "%Y-%m-%d"), str( nextruntime ) ) )

def AutoStart():
     xbmc.sleep(5000)
     defaultLog( addonLanguage(32200) )
     if addonSettings.getSetting( "ScheduleEnabled" ) == "true":
		   defaultLog( addonLanguage(32655) % ( addonSettings.getSetting( "ScheduledWeekDay" ), addonSettings.getSetting( "DayTime" ) ) )	 
     addonSettings.setSetting( "PerformingUpdate", "false" )
     while ( not xbmc.abortRequested ):
		   xbmc.sleep(5000)
		   if addonSettings.getSetting( "ScheduleEnabled" ) == "true":
		    global WeekDay
		    global DayTime
		    newWeekDay = addonSettings.getSetting( "WeekDay" )
		    newScheduledTime = addonSettings.getSetting( "DayTime" )
		    if ( WeekDay != newWeekDay ) or ( DayTime != newScheduledTime ) or ( addonSettings.getSetting( "ScheduledWeekDay" ) == "2000-01-01"):
				WeekDay = newWeekDay
				DayTime = newScheduledTime
				UpdateSchedule()
		    try:
				ScheduledDay = datetime.strptime( addonSettings.getSetting( "ScheduledWeekDay" ), "%Y-%m-%d" )
		    except TypeError:
				ScheduledDay = datetime(*(time.strptime( addonSettings.getSetting( "ScheduledWeekDay" ), "%Y-%m-%d" )[0:6]))
		    if ( datetime.now() >= ScheduledDay ):
				if ( time.strftime("%H:%M:%S") >= addonSettings.getSetting( "DayTime" ) ):
					UpdateSchedule()
					xbmc.executebuiltin( "XBMC.RunScript(special://home/addons/script.light.imdb.ratings.update/main.py)" )
					while ( not xbmc.abortRequested ):
						xbmc.sleep(5000)

if (__name__ == "__main__"):
     AutoStart()
