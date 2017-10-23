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
	
max_threads = 3	#0 - 1 thread, 1 - 2 threads ...
num_threads = 0
lock = allocate_lock()

def thread_parse_IMDb_page(dType, tParam0, tParam1, tParam2, tParam3, tParam4, tParam5):
	#movie:   MovieID,   IMDb,    Title, Rating, Votes, Top250
	#tvshow:  TVShowID,  imdb_id, Title, Rating, Votes, tvdb_id
	#episode: EpisodeID, IMDb,    Title, Rating, Votes, TVDB
	global num_threads
	parsed_data = parse_IMDb_page(tParam1)
	if parsed_data == None:
		defaultLog( addonLanguage(32503) % ( tParam2 ) )
	else:
		Rating = float( ( "%.1f" % tParam3 ) )
		Votes = '{:,}'.format( int ( tParam4 ) )
		if (dType == "movie"):
			Top250 = tParam5
		else:
			Top250 = None
		defaultLog( addonLanguage(32499) % ( Rating, Votes, Top250 ) )
		updatedRating = parsed_data[0]
		updatedVotes = parsed_data[1]
		if (dType == "movie"):
			updatedTop250 = parsed_data[2]
		else:
			updatedTop250 = None
		if Rating != updatedRating or ( Votes != updatedVotes and \
				((dType == "movie" and IncludeMoviesVotes == "true" ) or ((dType == "tvshow" or dType == "episode") and IncludeTVShowsVotes == "true")) or \
				( dType == "movie" and (Top250 != updatedTop250) and IncludeMoviesTop250 == "true" )):
			if (dType == "movie"):
				jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":' + str( tParam0 ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","top250":' + str( updatedTop250 ) + '},"id":1}'
			elif (dType == "tvshow"):
				jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetTVShowDetails","params":{"tvshowid":' + str( tParam0 ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + tParam1 + '","tvdb": "' + tParam5 + '"}},"id":1}'
			elif (dType == "episode"):
				jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":' + str( tParam0 ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + tParam1 + '","tvdb": "' + tParam5 + '"}},"id":1}'
			debugLog( "JSON Query: " + jSonQuery )
			jSonResponse = xbmc.executeJSONRPC( jSonQuery )
			jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
			debugLog( "JSON Response: " + jSonResponse )
			defaultLog( addonLanguage(32500) % ( tParam2, str( updatedRating ), str( updatedVotes ), str( updatedTop250 ) ) )
		else:
			defaultLog( addonLanguage(32502) % ( tParam2 ) )
	lock.acquire()
	num_threads -= 1
	lock.release()

class Movies:
	def __init__( self ):
		defaultLog( addonLanguage(32255) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32255), 5000 )
			xbmc.sleep(5000)
		self.AllMovies = []
		self.getDBMovies()
		self.doUpdate()
		defaultLog( addonLanguage(32258) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32258), 5000 )
			xbmc.sleep(5000)

	def getDBMovies( self ):
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetMovies","params":{"properties":["imdbnumber","rating","votes","top250"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'movies' ):
				for item in jSonResponse['result']['movies']:
					MovieID = item.get('movieid'); IMDb = item.get('imdbnumber'); Title  = item.get('label'); 
					Rating = item.get('rating'); Votes = item.get('votes'); Top250 = item.get('top250');
					self.AllMovies.append( ( MovieID, IMDb, Title, Rating, Votes, Top250 ) )
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
			IMDb = Movie[1]
			TVDB = None
			defaultLog( addonLanguage(32507) % ( Movie[2], IMDb, TVDB ) )
			if IMDb == "" or IMDb == None or "tt" not in IMDb:
				defaultLog( addonLanguage(32503) % ( Movie[2] ) )
				continue
			start_new_thread(thread_parse_IMDb_page,("movie",Movie[0],Movie[1],Movie[2],Movie[3],Movie[4],Movie[5]))
			lock.acquire()
			num_threads += 1
			lock.release()
		if ShowProgress == "true":
			Progress.close()

class TVShows:
	def __init__( self ):
		defaultLog( addonLanguage(32256) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32256), 5000 )
			xbmc.sleep(5000)
		self.AllTVShows = []
		self.getDBTVShows()
		self.doUpdateTVShows()
		defaultLog( addonLanguage(32259) )
		if ShowNotifications == "true":
			doNotify( addonLanguage(32259), 5000 )
			xbmc.sleep(5000)

	def getDBTVShows( self ):
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetTVShows","params":{"properties":["imdbnumber","uniqueid","rating","votes"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'tvshows' ):
				for item in jSonResponse['result']['tvshows']:
					TVShowID = item.get('tvshowid'); unique_id = item.get('uniqueid'); imdb_id = unique_id.get('imdb'); Title  = item.get('label');
					Rating = item.get('rating'); Votes = item.get('votes'); tvdb_id = item.get('imdbnumber')
					self.AllTVShows.append( ( TVShowID, imdb_id, Title, Rating, Votes, tvdb_id ) )
		except: pass
	  
	def doUpdateEpisodes( self, tvshowid, tvshowtitle ):
		global num_threads
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"tvshowid":' + str( tvshowid ) + ', "properties":["uniqueid","rating","votes"]},"id":1}'
		debugLog( "JSON Query: " + jSonQuery )
		jSonResponse = xbmc.executeJSONRPC( jSonQuery )
		jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
		debugLog( "JSON Response: " + jSonResponse )
		jSonResponse = jSon.loads( jSonResponse )
		try:
			if jSonResponse['result'].has_key( 'episodes' ):
				Counter = 0
				AllEpisodes = jSonResponse['result']['limits']['total']
				for item in jSonResponse['result']['episodes']:
					while num_threads > max_threads:
						xbmc.sleep(500)
					if ShowProgress == "true":
						Counter = Counter + 1
						self.Progress.update( (Counter*100)/AllEpisodes, addonLanguage(32262), tvshowtitle )
					EpisodeID = item.get('episodeid'); unique_id = item.get('uniqueid'); IMDb = unique_id.get('imdb'); Title  = item.get('label');
					Rating = item.get('rating'); Votes = item.get('votes');
					TVDB = unique_id.get('tvdb')
					if TVDB == "" or TVDB == None:
						TVDB = unique_id.get('unknown')
					defaultLog( addonLanguage(32507) % ( Title, IMDb, TVDB ) )
					if IMDb == "" or IMDb == None or "tt" not in IMDb:
						IMDb = get_IMDb_ID("episode", TVDB)
					if IMDb == "" or IMDb == None:
						defaultLog( addonLanguage(32503) % ( Title ) )
						continue
					start_new_thread(thread_parse_IMDb_page,("episode",EpisodeID,IMDb,Title,Rating,Votes,TVDB))
					lock.acquire()
					num_threads += 1
					lock.release()
		except: pass

	def doUpdateTVShows( self ):
		global num_threads
		if ShowProgress == "true":
			self.Progress = xbmcgui.DialogProgressBG()
			self.Progress.create( addonLanguage(32262) )
		for TVShow in self.AllTVShows:
			while num_threads > max_threads:
				xbmc.sleep(500)
			if ShowProgress == "true":
				self.Progress.update( 0, addonLanguage(32262), TVShow[2] )
			IMDb = TVShow[1]
			TVDB = TVShow[5]
			defaultLog( addonLanguage(32507) % ( TVShow[2], IMDb, TVDB ) )
			if IMDb == "" or IMDb == None or "tt" not in IMDb:
				IMDb = get_IMDb_ID("tvshow", TVDB)
			if IMDb == "" or IMDb == None:
				defaultLog( addonLanguage(32503) % ( TVShow[2] ) )
				continue		   
			start_new_thread(thread_parse_IMDb_page,("tvshow",TVShow[0],IMDb,TVShow[2],TVShow[3],TVShow[4],TVShow[5]))
			lock.acquire()
			num_threads += 1
			lock.release()
			if IncludeEpisodes == "true":
				self.doUpdateEpisodes( TVShow[0], TVShow[2] )
			else:
				self.Progress.update( 100, addonLanguage(32262), TVShow[2] )
				xbmc.sleep(1000)
		if ShowProgress == "true":
			self.Progress.close()

def perform_update():
	if addonSettings.getSetting( "PerformingUpdate" ) == "true":
		xbmcgui.Dialog().ok( "%s" % ( addonName ), addonLanguage(32251) )
		return
	addonSettings.setSetting( "PerformingUpdate", "true" )
	if onMovies == "true": Movies()
	if ShowNotifications == "true":
		xbmc.sleep(5000)
	if onTVShows == "true": TVShows()
	addonSettings.setSetting( "PerformingUpdate", "false" )
