# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################
# changes by dziobak        #
#############################

import xbmc, xbmcgui
import sys
if sys.version_info >= (2, 7): import json as jSon
else: import simplejson as jSon
from common import *
from imdb_scraper import parse_IMDb_page
from tvdb_scraper import get_IMDb_ID
from thread import start_new_thread, allocate_lock

max_threads = int(NumberOfThreads) - 1	#0 - 1 thread, 1 - 2 threads ...
num_threads = 0

def thread_parse_IMDb_page(dType, dbID, IMDb, Title, Rating, Votes, TVDB, lock, flock):
        #movie:   MovieID,   IMDb, Title, Rating, Votes, Top250
        #tvshow:  TVShowID,  IMDb, Title, Rating, Votes, TVDB
        #episode: EpisodeID, IMDb, Title, Rating, Votes, TVDB
	global num_threads
        if IMDb == None or IMDb == "" or "tt" not in IMDb: IMDb = None
        Top250 = None
        if dType == "movie":
                Top250 = TVDB
                if Top250 == None: Top250 = 0
                TVDB = None
        defaultLog( addonLanguage(32507) % ( Title, IMDb, TVDB ) )
        if IMDb == None:
                if dType == "tvshow" or dType == "episode":
                        (IMDb, statusInfo) = get_IMDb_ID(dType, TVDB)
                if IMDb == None:
                        defaultLog( addonLanguage(32503) % ( Title ) )
                        flock.acquire()
                        try:
                                statusLog( Title + ": " + statusInfo )
                        finally:
                                flock.release()
                        lock.acquire()
                        num_threads -= 1
                        lock.release()
                        return
        (updatedRating, updatedVotes, updatedTop250, statusInfo) = parse_IMDb_page(IMDb)
	if updatedRating == None:
		defaultLog( addonLanguage(32503) % ( Title ) )
                flock.acquire()
                try:
                        statusLog( Title + ": " + statusInfo )
                finally:
                        flock.release()
	else:
		Rating = str( float( ( "%.1f" % Rating ) ) )
		Votes = '{:,}'.format( int ( Votes ) )
		defaultLog( addonLanguage(32499) % ( Rating, Votes, Top250 ) )
		if (dType != "movie"):
			updatedTop250 = None
		if Rating != updatedRating or ( Votes != updatedVotes and \
				((dType == "movie" and IncludeMoviesVotes == "true" ) or ((dType == "tvshow" or dType == "episode") and IncludeTVShowsVotes == "true")) or \
				( dType == "movie" and (Top250 != updatedTop250) and IncludeMoviesTop250 == "true" )):
			if (dType == "movie"):
				jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":' + str( dbID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","top250":' + str( updatedTop250 ) + '},"id":1}'
			elif (dType == "tvshow"):
                                jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetTVShowDetails","params":{"tvshowid":' + str( dbID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + IMDb + '","tvdb": "' + TVDB + '"}},"id":1}'
			elif (dType == "episode"):
                                jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":' + str( dbID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + IMDb + '","tvdb": "' + TVDB + '"}},"id":1}'
			debugLog( "JSON Query: " + jSonQuery )
			jSonResponse = xbmc.executeJSONRPC( jSonQuery )
			jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
			debugLog( "JSON Response: " + jSonResponse )
			defaultLog( addonLanguage(32500) % ( Title, str( updatedRating ), str( updatedVotes ), str( updatedTop250 ) ) )
		else:
			defaultLog( addonLanguage(32502) % ( Title ) )
	lock.acquire()
	num_threads -= 1
	lock.release()
	return

class Movies:
	def __init__( self ):
		defaultLog( addonLanguage(32255) )
		statusLog( addonLanguage(32255) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32255), 5000 )
			xbmc.sleep(5000)
		self.AllMovies = []
		self.getDBMovies()
                self.lock = allocate_lock()
                self.flock = allocate_lock()
		self.doUpdate()
		defaultLog( addonLanguage(32258) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32258), 5000 )
			xbmc.sleep(5000)

	def getDBMovies( self ):
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"properties":["imdbnumber","rating","votes","top250","playcount"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'movies' ):
				for item in jSonResponse['result']['movies']:
					MovieID = item.get('movieid'); IMDb = item.get('imdbnumber'); Title  = item.get('label'); 
					Rating = item.get('rating'); Votes = item.get('votes'); Top250 = item.get('top250'); Watched = item.get('playcount');
					self.AllMovies.append( ( MovieID, IMDb, Title, Rating, Votes, Top250, Watched ) )
	  	except: pass

	def doUpdate( self ):
		global num_threads
		AllMovies = len( self.AllMovies ); Counter = 0;
		if ShowProgress == "true":
			Progress = xbmcgui.DialogProgressBG()
			Progress.create( addonLanguage(32261) )
		for Movie in self.AllMovies:
			while num_threads > max_threads:
				xbmc.sleep(500)
			if ShowProgress == "true":
				Counter = Counter + 1
				Progress.update( (Counter*100)/AllMovies, addonLanguage(32261), Movie[2] )
			if int(Movie[6]) > 0 and ExcludeWatched == "true":
				defaultLog( addonLanguage(32504) % ( Movie[2] ) )
				continue
                        start_new_thread(thread_parse_IMDb_page,("movie",Movie[0],Movie[1],Movie[2],Movie[3],Movie[4],Movie[5],self.lock,self.flock))
                        self.lock.acquire()
			num_threads += 1
                        self.lock.release()
                while num_threads > 0:
                        xbmc.sleep(500)
		if ShowProgress == "true":
			Progress.close()

class TVShows:
	def __init__( self ):
		defaultLog( addonLanguage(32256) )
                statusLog( addonLanguage(32256) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32256), 5000 )
			xbmc.sleep(5000)
		self.AllTVShows = []
		self.getDBTVShows()
                self.lock = allocate_lock()
                self.flock = allocate_lock()
		self.doUpdateTVShows()
		defaultLog( addonLanguage(32259) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32259), 5000 )
			xbmc.sleep(5000)

	def getDBTVShows( self ):
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetTVShows","params":{"properties":["imdbnumber","uniqueid","rating","votes","playcount"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'tvshows' ):
				for item in jSonResponse['result']['tvshows']:
					TVShowID = item.get('tvshowid'); unique_id = item.get('uniqueid'); imdb_id = unique_id.get('imdb'); Title  = item.get('label');
					Rating = item.get('rating'); Votes = item.get('votes'); tvdb_id = item.get('imdbnumber'); Watched = item.get('playcount');
					self.AllTVShows.append( ( TVShowID, imdb_id, Title, Rating, Votes, tvdb_id, Watched ) )
		except: pass
	  
	def doUpdateEpisodes( self, tvshowid, tvshowtitle, PCounter ):
		global num_threads
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"tvshowid":' + str( tvshowid ) + ', "properties":["uniqueid","rating","votes","playcount","episode","season"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'episodes' ):
				for item in jSonResponse['result']['episodes']:
					while num_threads > max_threads:
						xbmc.sleep(500)
					EpisodeID = item.get('episodeid'); unique_id = item.get('uniqueid'); IMDb = unique_id.get('imdb')
					Title = tvshowtitle + " " + str( item.get('season') ) + "x" + str( "%02d" % item.get('episode') );
					Rating = item.get('rating'); Votes = item.get('votes'); Watched = item.get('playcount');
					TVDB = unique_id.get('tvdb')
					if TVDB == "" or TVDB == None:
						TVDB = unique_id.get('unknown')
					if ShowProgress == "true":
						self.Progress.update( PCounter, addonLanguage(32262), Title )
					if int(Watched) > 0 and ExcludeWatched == "true":
						defaultLog( addonLanguage(32504) % ( Title ) )
						continue
                                        start_new_thread(thread_parse_IMDb_page,("episode",EpisodeID,IMDb,Title,Rating,Votes,TVDB,self.lock,self.flock))
                                        self.lock.acquire()
					num_threads += 1
					self.lock.release()
		except: pass

	def doUpdateTVShows( self ):
		global num_threads
		AllTVShows = len( self.AllTVShows ); Counter = 0;
		if ShowProgress == "true":
			self.Progress = xbmcgui.DialogProgressBG()
			self.Progress.create( addonLanguage(32262) )
		for TVShow in self.AllTVShows:
			while num_threads > max_threads:
				xbmc.sleep(500)
			if ShowProgress == "true":
                                Counter = Counter + 1
                                PCounter = (Counter*100)/AllTVShows
				self.Progress.update( PCounter, addonLanguage(32262), TVShow[2] )
			if int(TVShow[6]) > 0 and ExcludeWatched == "true":
				defaultLog( addonLanguage(32504) % ( TVShow[2] ) )
				continue
                        start_new_thread(thread_parse_IMDb_page,("tvshow",TVShow[0],TVShow[1],TVShow[2],TVShow[3],TVShow[4],TVShow[5],self.lock,self.flock))
                        self.lock.acquire()
			num_threads += 1
			self.lock.release()
			if IncludeEpisodes == "true":
				self.doUpdateEpisodes( TVShow[0], TVShow[2], PCounter )
                while num_threads > 0:
                        xbmc.sleep(500)
		if ShowProgress == "true":
			self.Progress.close()

def perform_update():
	if addonSettings.getSetting( "PerformingUpdate" ) == "true":
		xbmcgui.Dialog().ok( "%s" % ( addonName ), addonLanguage(32251) )
		return
	addonSettings.setSetting( "PerformingUpdate", "true" )
        beginStatusLog()
	if onMovies == "true":
		Movies()
		if ShowNotifications == "true":	xbmc.sleep(5000)
	if onTVShows == "true": TVShows()
	addonSettings.setSetting( "PerformingUpdate", "false" )

