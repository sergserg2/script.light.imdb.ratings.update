# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################
# changes by dziobak        #
#############################

import xbmc, xbmcgui
import sys, re
if sys.version_info >= (2, 7): import json as jSon
else: import simplejson as jSon
from common import *
from imdb_scraper import parse_IMDb_page
from tvdb_scraper import get_IMDb_ID
	
def update( filename, label ):
	if addonSettings.getSetting( "PerformingUpdate" ) == "true":
		xbmcgui.Dialog().ok( "%s" % ( addonName ), addonLanguage(32251) )
		return
	addonSettings.setSetting( "PerformingUpdate", "true" )
	updateitem = ""
	allepisodes = False
	seasonpisodes = False
	id_parts = re.findall(r"[-+]?\d*\.\d+|\d+", filename)
	if "movies" in filename:
		updateitem = "movie"
		id = int(id_parts[0])
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetMovieDetails","params":{"movieid":' + str( id ) + ',"properties":["imdbnumber","rating","votes","top250"]},"id":1}'
	elif "tvshows" in filename and "season" in filename and "tvshowid" in filename:
		updateitem = "episode"
		id = int(id_parts[2])
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodeDetails","params":{"episodeid":' + str( id ) + ',"properties":["uniqueid","rating","votes"]},"id":1}'
	elif "tvshows" in filename and "tvshowid" in filename:
		updateitem = "season"
		id = int(id_parts[1])
		dialog = xbmcgui.Dialog()
		seasonpisodes = dialog.yesno( "%s" % ( addonName ), addonLanguage(32508) % label )
		if seasonpisodes == False:
			return
	elif "tvshows" in filename:
		updateitem = "tvshow"
		id = int(id_parts[0])
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetTVShowDetails","params":{"tvshowid":' + str( id ) + ',"properties":["imdbnumber","uniqueid","rating","votes"]},"id":1}'
		dialog = xbmcgui.Dialog()
		allepisodes = dialog.yesno( "%s" % ( addonName ), addonLanguage(32253) )
	Progress = xbmcgui.DialogProgressBG()
	Progress.create( addonLanguage(32260), label )
	if seasonpisodes == True:
		doUpdateEpisodes( Progress, int(id_parts[0]), int(id_parts[1]), label )
		xbmc.sleep(1000)
		Progress.close()
		addonSettings.setSetting( "PerformingUpdate", "false" )
		return
	debugLog( "JSON Query: " + jSonQuery )
	jSonResponse = xbmc.executeJSONRPC( jSonQuery )
	jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
	debugLog( "JSON Response: " + jSonResponse )
	jSonResponse = jSon.loads( jSonResponse )
	if jSonResponse['result'].has_key( 'moviedetails' ):
		item = jSonResponse['result']['moviedetails']
		ID = item.get('movieid')
		IMDb = item.get('imdbnumber')
		TVDB = None
	elif jSonResponse['result'].has_key( 'tvshowdetails' ):
		item = jSonResponse['result']['tvshowdetails']
		ID = item.get('tvshowid')
		unique_id = item.get('uniqueid')
		IMDb = unique_id.get('imdb')
		TVDB = item.get('imdbnumber')
	elif jSonResponse['result'].has_key( 'episodedetails' ):
		item = jSonResponse['result']['episodedetails']
		ID = item.get('episodeid')
		unique_id = item.get('uniqueid')
		IMDb = unique_id.get('imdb')
		TVDB = unique_id.get('tvdb')
		if TVDB == "" or TVDB == None:
			TVDB = unique_id.get('unknown')
	exit = False
	Title = item.get('label')
	defaultLog( addonLanguage(32507) % ( Title, IMDb, TVDB ) )
	if (updateitem != "movie") and (IMDb == "" or IMDb == None or "tt" not in IMDb):
		(IMDb, statusInfo) = get_IMDb_ID(updateitem, TVDB)
	if IMDb == None:
		defaultLog( addonLanguage(32503) % ( Title ) )
		exit = True
	else:	
		(updatedRating, updatedVotes, updatedTop250, statusInfo) = parse_IMDb_page(IMDb)
		if updatedRating == None:
			defaultLog( addonLanguage(32503) % ( Title ) )
			exit = True
	if exit == True:
		Progress.update( 100, addonLanguage(32260), label )
		xbmc.sleep(1000)
		Progress.close()
		addonSettings.setSetting( "PerformingUpdate", "false" )
		return
	if updateitem != "movie":
		updatedTop250 = None
	if updateitem == "movie":
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":' + str( ID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","top250":' + str( updatedTop250 ) + '},"id":1}'
	elif updateitem == "tvshow":
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetTVShowDetails","params":{"tvshowid":' + str( ID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + IMDb + '","tvdb": "' + TVDB + '"}},"id":1}'
	elif updateitem == "episode":
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":' + str( ID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + IMDb + '","tvdb": "' + TVDB + '"}},"id":1}'
	debugLog( "JSON Query: " + jSonQuery )
	jSonResponse = xbmc.executeJSONRPC( jSonQuery )
	jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
	debugLog( "JSON Response: " + jSonResponse )
	defaultLog( addonLanguage(32500) % ( Title, str( updatedRating ), str( updatedVotes ), str( updatedTop250 ) ) )
	if allepisodes == True:
		doUpdateEpisodes( Progress, ID, None, Title )
	else:
		Progress.update( 100, addonLanguage(32260), label )
	xbmc.sleep(1000)
	Progress.close()
	addonSettings.setSetting( "PerformingUpdate", "false" )
		
def doUpdateEpisodes( progress, tvshowid, season, tvshowtitle ):
	if season == None:
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"tvshowid":' + str( tvshowid ) + ', "properties":["uniqueid","rating","votes"]},"id":1}'
	else:
		jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes","params":{"tvshowid":' + str( tvshowid ) + ', "season":' + str( season ) + ', "properties":["uniqueid","rating","votes"]},"id":1}'
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
				TVDB = ""
				Counter = Counter + 1
				progress.update( (Counter*100)/AllEpisodes, addonLanguage(32260), tvshowtitle )
				EpisodeID = item.get('episodeid'); unique_id = item.get('uniqueid'); IMDb = unique_id.get('imdb'); Title = item.get('label')
				TVDB = unique_id.get('tvdb')
				if TVDB == "" or TVDB == None:
					TVDB = unique_id.get('unknown')
				defaultLog( addonLanguage(32507) % ( Title, IMDb, TVDB ) )
				if IMDb == "" or IMDb == None or "tt" not in IMDb:
					(IMDb, statusInfo) = get_IMDb_ID("episode", TVDB)
				if IMDb == None:
					defaultLog( addonLanguage(32503) % ( Title ) )
					continue
				(updatedRating, updatedVotes, updatedTop250, statusInfo) = parse_IMDb_page(IMDb)
				if updatedRating == None:
					defaultLog( addonLanguage(32503) % ( Title ) )
					continue
				updatedTop250 = None
				jSonQuery = '{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":' + str( EpisodeID ) + ',"rating":' + str( updatedRating ) + ',"votes":"' + str( updatedVotes ) + '","uniqueid": {"imdb": "' + IMDb + '","tvdb": "' + TVDB + '"}},"id":1}'
				debugLog( "JSON Query: " + jSonQuery )
				jSonResponse = xbmc.executeJSONRPC( jSonQuery )
				jSonResponse = unicode( jSonResponse, 'utf-8', errors='ignore' )
				debugLog( "JSON Response: " + jSonResponse )
				defaultLog( addonLanguage(32500) % ( Title, str( updatedRating ), str( updatedVotes ), str( updatedTop250 ) ) )
	except: pass
