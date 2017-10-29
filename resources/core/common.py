# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################

import xbmc, xbmcaddon
import os, unicodedata

addonSettings   = xbmcaddon.Addon( "script.light.imdb.ratings.update" )
addonName       = addonSettings.getAddonInfo( "name" )
addonIcon       = os.path.join( addonSettings.getAddonInfo( "path" ), "icon.png" )
addonProfile    = xbmc.translatePath( addonSettings.getAddonInfo( "profile" ) ).decode('utf-8')
addonLanguage   = addonSettings.getLocalizedString

onMovies             = addonSettings.getSetting( "Movies" )
onTVShows            = addonSettings.getSetting( "TVShows" )
ShowNotifications    = addonSettings.getSetting( "ShowNotifications" )
ShowProgress         = addonSettings.getSetting( "ShowProgress" )
IncludeMoviesVotes   = addonSettings.getSetting( "IncludeMoviesVotes" )
IncludeMoviesTop250  = addonSettings.getSetting( "IncludeMoviesTop250" )
IncludeTVShowsVotes  = addonSettings.getSetting( "IncludeTVShowsVotes" )
IncludeEpisodes      = addonSettings.getSetting( "IncludeEpisodes" )
ExcludeWatched       = addonSettings.getSetting( "ExcludeWatched" )
NumberOfThreads      = addonSettings.getSetting( "NumberOfThreads" )

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

def debugLog( textMessage ):
     xbmc.log( "[%s] - %s" % ( addonName, doNormalize( textMessage ) ), level = xbmc.LOGDEBUG )

def doNotify( textMessage, millSec ):
     xbmc.executebuiltin( 'Notification( "%s", "%s", %s, "%s")' % ( addonName, textMessage.encode('utf-8'), millSec, addonIcon ) )

def statusLog( textMessage ):
     f = open( addonProfile + "/update.log", 'a' )
     f.write( doNormalize( textMessage + "\n" ) )
     f.close()

def beginStatusLog():
     f = open( addonProfile + "/update.log", 'w' )
     f.close()