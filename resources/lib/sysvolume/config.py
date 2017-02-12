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

import os
import xbmcaddon


class CONST(object):
    addon_id = 'script.change.sysvolume'


class Config(object):

    def __init__(self, addon):
        self.reload(addon)

    def reload(self, addon):
        # Addon Info
        self.addon_id = addon.getAddonInfo('id')
        self.addon_name = addon.getAddonInfo('name')
        self.addon_path = addon.getAddonInfo('path').decode('utf-8')
        self.addon_base_url = 'plugin://' + self.addon_id
        self.addon_icon = os.path.join(self.addon_path, 'icon.png').decode('utf-8')
        # Settings
        self.device_name = addon.getSetting('device_name').decode('utf-8')
        self.mixer_name = addon.getSetting('mixer_name').decode('utf-8')
        self.step_up = int('0%s' % addon.getSetting('step_up'))
        self.step_down = int('0%s' % addon.getSetting('step_down'))
        self.max_volume = int('0%s' % addon.getSetting('max_volume'))
        self.show_progress = True if addon.getSetting('show_progress') == 'true' else False
        self.progress_time = int('0%s' % addon.getSetting('progress_time'))
        self.debug = True if addon.getSetting('debug') == 'true' else False

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------

addon = xbmcaddon.Addon(CONST.addon_id)
settings = Config(addon) 

def _T(txtid):
    try:
        txt = addon.getLocalizedString(txtid)
        return txt
    except:
        return '?: %s' % txtid

def reloadConfig():
    settings.reload(addon)
    return settings

def getSetting(setting):
    return addon.getSetting(setting)

def setSetting(setting, value):
    addon.setSetting(setting, value)

