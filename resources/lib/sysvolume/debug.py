# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Arne Svenson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function, unicode_literals

import sys, os, logging
from kodi_six import xbmc

#------------------------------------------------------------------------------
# Global Definitions
#------------------------------------------------------------------------------

DEBUG_ENABLED = True
DEBUG_SERVER = 'localhost'
ADDON_NAME = 'DEBUG'

try:
    from .config import settings
    DEBUG_ENABLED = settings.debug
    ADDON_NAME = settings.addon_name
except:
    pass

try:
    # LOGNOTICE not available in Kodi 19
    LOGNOTICE = xbmc.LOGNOTICE
except:
    LOGNOTICE = xbmc.LOGINFO

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def logInfo(txt=''):
    if DEBUG_ENABLED:
        xbmcLog(txt, level=LOGNOTICE)

def logDebug(txt=''):
    if DEBUG_ENABLED:
        xbmcLog(txt, level=xbmc.LOGDEBUG)

def logWarning(txt=''):
    xbmcLog(txt, level=xbmc.LOGWARNING)

def logError(txt=''):
    xbmcLog(txt, level=xbmc.LOGERROR)

def xbmcLog(txt = '', level=xbmc.LOGINFO):
    ''' Log a text into the Kodi-Logfile '''
    try:
        xbmc.log("[%s] %s" % (ADDON_NAME, txt), level)
    except:
        xbmc.log("[%s] Logging Error" % ADDON_NAME, xbmc.LOGERROR)

def logException(e, txt='', level=xbmc.LOGERROR):
    if txt:
        xbmcLog(txt + '\n' + str(e), level)
    logging.exception(str(e))

def updatePath():
    ''' Update the path to find pydevd Package '''
    if DEBUG_ENABLED:
        # For PyCharm:
        # sys.path.append("/Applications/PyCharm.app/Contents/helpers/pydev")
        # For LiClipse:
        # sys.path.append("/Applications/LiClipse.app/Contents/liclipse/plugins/org.python.pydev_4.4.0.201510052047/pysrc")
        for comp in sys.path:
            if comp.find('addons') != -1:
                pydevd_path = os.path.normpath(os.path.join(comp, os.pardir, 'script.module.pydevd', 'lib'))
                sys.path.append(pydevd_path)
                break
            pass

def halt(host=None):
    ''' This is the Break-Point-Function '''
    if DEBUG_ENABLED:
        if not host:
            if DEBUG_SERVER:
                host = DEBUG_SERVER
            else:
                host = 'localhost'
        updatePath()
        import pydevd
        pydevd.settrace(host, stdoutToServer=True, stderrToServer=True)
        pass


def killDebugThreads():
    ''' This kills all PyDevd Remote Debugger Threads '''
    if DEBUG_ENABLED:
        try:
            updatePath()
            import pydevd
            pydevd.stoptrace()
        except:
            pass
        pass
