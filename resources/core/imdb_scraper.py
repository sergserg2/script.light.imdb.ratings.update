# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################
# changes by dziobak        #
#############################

import re, urllib2, socket
import xbmc
from common import *
from StringIO import StringIO
import gzip

user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36"
base_url = "http://akas.imdb.com/title/"

def get_IMDb_page(imdb_id):
	url = base_url + imdb_id + "/"
	req = urllib2.Request(url)
	req.add_header('User-Agent', user_agent)
	req.add_header('Accept-encoding', 'gzip')
	socket.setdefaulttimeout(30)
	html = ""
	try:
		response = urllib2.urlopen(req)
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO(response.read())
			f = gzip.GzipFile(fileobj=buf)
			html = f.read()
		else:
			html=response.read()
		response.close()
		return (html, "OK", None)
	except urllib2.HTTPError as err:
                error = str( err.code ) + " " + err.reason
		defaultLog( addonLanguage(32505) % error )
                statusInfo = "get_IMDb_page: " + url + " -> " + addonLanguage(32505) % error
		return (html, "HTTP", statusInfo)
	except socket.error as err:
		defaultLog( addonLanguage(32505) % ( err ) )
                statusInfo = "get_IMDb_page: " + url + " -> " + addonLanguage(32505) % (err)
		return (html, "socket", statusInfo)

def parse_IMDb_page(imdb_id):
	do_loop = 1
	while do_loop > 0 :
		(html, status, statusInfo) = get_IMDb_page(imdb_id)
		if status == "socket":
			xbmc.sleep(1000 * do_loop)
			do_loop += 1
			if do_loop == 4: return (None,None,None,statusInfo)
		elif status == "HTTP": return (None,None,None,statusInfo)
		else: do_loop = 0
	htmlline = html.replace('\n', ' ').replace('\r', '')
	matchVotes = re.findall(r'title=\"(\d\.\d) based on (\d*,?\d*,?\d+) user ratings\"', htmlline)
	if matchVotes:
		rating = matchVotes[0][0]
		votes = matchVotes[0][1]
	else:
		rating = None
		votes = None
                statusInfo = "parse_IMDb_page: " + imdb_id + " -> no ratings"
	matchTop250 = re.findall(r'href="/chart/top\?ref_=tt_awd" > Top Rated Movies #(\d+) </a>', htmlline)
	if matchTop250:
		top250 = matchTop250[0]
	else:
		top250 = 0
	defaultLog( addonLanguage(32506) % ( rating, votes, top250 ) )
	return (rating, votes, top250, statusInfo)
