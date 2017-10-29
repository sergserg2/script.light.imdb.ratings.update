# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################
# changes by dziobak        #
#############################

from common import *
import resources.support.tvdbsimple as tvdb
tvdb.KEYS.API_KEY = "53F49B260156B636"

def get_IMDb_ID(updateitem, tvdb_id):
	imdb_id = None
	statusInfo = None
	defaultLog( addonLanguage(32509) )
	if tvdb_id == "" or tvdb_id == None:
		return (imdb_id, "missing TVDB ID");
	if updateitem == "tvshow":
		show = tvdb.Series(tvdb_id)
		response = show.info()
		try:
			imdb_id = show.imdbId
		except:
			defaultLog( addonLanguage(32511) )
			pass
	elif updateitem == "episode":
		episode = tvdb.Episode(tvdb_id)
		response = episode.info()
		try:
			imdb_id = episode.imdbId
		except:
			defaultLog( addonLanguage(32511) )
			pass
		#if empty, return None
		if imdb_id == "" or imdb_id == None:
			imdb_id = None
			statusInfo = "get_IMDb_ID: TVDB " + str( tvdb_id ) + " (" + updateitem + ") -> missing IMDb ID"
		#special cases
		if imdb_id != None:
			if "tt" not in imdb_id: imdb_id = "tt" + str(imdb_id)
			imdb_id = imdb_id.rstrip('/')
	defaultLog( addonLanguage(32512) % ( imdb_id ) )
	return (imdb_id, statusInfo)
