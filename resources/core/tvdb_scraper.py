# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################
# changes by dziobak        #
#############################

from common import *
from requests.exceptions import ConnectionError
import resources.support.tvdbsimple as tvdb
tvdb.KEYS.API_KEY = "53F49B260156B636"

def get_IMDb_ID(updateitem, tvdb_id):
	defaultLog( addonLanguage(32509) )
	if tvdb_id == "" or tvdb_id == None:
		return (None, "missing TVDB ID");
	if updateitem == "tvshow":
			show = tvdb.Series(tvdb_id)
	elif updateitem == "episode":
			show = tvdb.Episode(tvdb_id)
	else:
		defaultLog( addonLanguage(32511) )
		return (None, "bad item type :" + updateitem)
	#connection
	try:
		response = show.info()
	except ConnectionError as err:
		defaultLog( "TVDB connection error: " + err )
		return (imdb_id, "get_IMDb_ID: connection error: " + err)
	#result
	try:
		imdb_id = show.imdbId
	except:
		imdb_id = None
		pass
	#no IMDb ID
	if imdb_id == None or imdb_id == "":
		defaultLog( addonLanguage(32511) )
		return (None, "get_IMDb_ID: TVDB " + str( tvdb_id ) + " (" + updateitem + ") -> missing IMDb ID")
	#special cases
	if "tt" not in imdb_id: imdb_id = "tt" + str(imdb_id)
	imdb_id = imdb_id.rstrip('/')
	defaultLog( addonLanguage(32512) % ( imdb_id ) )
	return (imdb_id, "OK")
