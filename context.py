# -*- coding: utf-8 -*-

#############################
# Light IMDb Ratings Update #
# by axlt2002               #
#############################

import xbmc
import sys, re
from resources.core import update_context

def UpdateContext():
	update_context.update( sys.listitem.getfilename(), sys.listitem.getLabel() )

if (__name__ == "__main__"):
     UpdateContext()