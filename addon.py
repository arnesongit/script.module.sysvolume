# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Arne Svenson
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

from __future__ import unicode_literals

import sys
import traceback
import xbmc, xbmcgui

from resources.lib.sysvolume.mixer import Mixer
from resources.lib.sysvolume import debug, config
from resources.lib.sysvolume.config import settings, _T

#------------------------------------------------------------------------------
# Public Functions
#------------------------------------------------------------------------------

def get_argv(idx, default=''):
    retval = default
    try:
        retval = sys.argv[idx]
    except:
        pass
    return retval

def get_argv_int(idx, default=0):
    retval = default
    try:
        retval = int(sys.argv[idx])
    except:
        pass
    return retval

def show_progress(mixer):
    if settings.show_progress:
        dia = xbmcgui.DialogProgressBG()
        dia.create(heading=settings.addon_name)
        dia.update(percent=mixer.volume, message='[%s] %s: %s%% %s' % (settings.device_name,
                                                                       settings.mixer_name,
                                                                       mixer.volume, _T(30104) if mixer.muted else ''))
        xbmc.sleep(settings.progress_time)
        dia.close()

def select_device():
    devices = Mixer.getDevices()
    devkeys = devices.keys()
    devlist = []
    for key in devkeys:
        devlist.append('[%s] %s' % (key, devices[key]['name']))
    if len(devlist) == 0:
        xbmcgui.Dialog().ok(_T(30101), _T(30102))
    else:
        device = xbmcgui.Dialog().select(_T(30101), devlist)
        if devices >= 0:
            mixers = devices[devkeys[device]]['mixer']
            if len(mixers) > 0:
                mixer = xbmcgui.Dialog().select(_T(30103), mixers)
                mixer_name = mixers[mixer]
            else:
                mixer_name = ''
            config.setSetting('device_name', devkeys[device].encode('utf-8'))
            config.setSetting('mixer_name', mixer_name.encode('utf-8'))

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        mixer = Mixer.create(settings.device_name, settings.mixer_name,
                             settings.step_up, settings.step_down,
                             settings.max_volume)
        cmd = get_argv(1, '').lower()
        if cmd == 'up':
            mixer.volumeUp(step=get_argv_int(2, default=settings.step_up))
            show_progress(mixer)
        elif cmd == 'down':
            mixer.volumeDown(step=get_argv_int(2, default=settings.step_down))
            show_progress(mixer)
        elif cmd == 'change':
            mixer.changeVolume(step=get_argv_int(2, default=0))
            show_progress(mixer)
        elif cmd == 'set':
            mixer.setVolume(volume=get_argv_int(2, default=mixer.volume))
            show_progress(mixer)
        elif cmd == 'mute':
            newMute = get_argv(2, default= 'true' if mixer.muted else 'false').lower()
            mixer.setMute(mute= True if newMute == 'true' else False)
            show_progress(mixer)
        elif cmd == 'mutetoggle':
            mixer.muteToggle()
            show_progress(mixer)
        else:
            select_device()
            pass
    except Exception as e:
        debug.log(str(e), level=xbmc.LOGERROR)
        traceback.print_exc()
