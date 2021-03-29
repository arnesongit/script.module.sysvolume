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

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import re
import traceback
import subprocess
from kodi_six import py2_encode
from . import debug
from . import config


class Mixer(object):

    @staticmethod
    def create(device_name, mixer_name, step_up, step_down, max_volume):
        if sys.platform.lower().startswith('darwin'):
            return MacOsMixer(device_name, mixer_name, step_up, step_down, max_volume)
        elif sys.platform.lower().startswith('linux'):
            return LinuxAlsaMixer(device_name, mixer_name, step_up, step_down, max_volume)
        else:
            return Mixer(device_name, mixer_name, step_up, step_down, max_volume)

    @staticmethod
    def _execute(execPath):
        process = subprocess.Popen(py2_encode(execPath), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout_value, stderr_value = process.communicate()
        stdout_value = stdout_value.decode()
        stderr_value = stderr_value.decode()
        retCode = process.returncode
        if len(stderr_value) > 2:
            debug.logError(stderr_value)
        return stdout_value

    @staticmethod
    def getDevices():
        if sys.platform.lower().startswith('darwin'):
            return MacOsMixer.getDevices()
        elif sys.platform.lower().startswith('linux'):
            return LinuxAlsaMixer.getDevices()
        else:
            return {}

    def __init__(self, device_name, mixer_name, step_up, step_down, max_volume):
        self.device_name = device_name
        self.mixer_name = mixer_name
        self.step_up = step_up
        self.step_down = step_down
        self.max_volume = max_volume
        self.volume = int(max_volume / 2)
        self.muted = False

    def _save_state(self):
        config.setSetting('last_volume', '%s' % self.volume)
        config.setSetting('last_muted', 'true' if self.muted else 'false')

    def _restore_state(self):
        self.volume = int('0%s' % config.getSetting('last_volume'))
        self.muted = True if config.getSetting('last_muted') == 'true' else False

    def getVolume(self):
        debug.logInfo('getVolume: %s' % self.volume)
        return self.volume

    def setVolume(self, volume, ignoreLimits=False):
        self.volume = volume if ignoreLimits else min(self.max_volume, volume)
        debug.logInfo('setVolume: %s' % self.volume)
        return self.volume

    def changeVolume(self, step, ignoreLimits=False):
        debug.logInfo('changeVolume: %s' % step)
        return self.setVolume(self.getVolume() + step, ignoreLimits)

    def volumeUp(self, step=0):
        stepVal = abs(step if step != 0 else self.step_up)
        debug.logInfo('volumeUp: %s' % stepVal)
        return self.changeVolume(stepVal)

    def volumeDown(self, step=0):
        stepVal = 0 - abs(step if step != 0 else self.step_down)
        debug.logInfo('volumeDown: %s' % stepVal)
        return self.changeVolume(stepVal)

    def isMuted(self):
        debug.logInfo('isMuted: %s' % self.muted)
        return self.muted

    def setMute(self, mute):
        debug.logInfo('setMute: %s' % mute)
        self.muted = mute
        return self.muted

    def muteToggle(self):
        return self.setMute(mute=not self.isMuted())


class MacOsMixer(Mixer):

    OSASCRIPT = "osascript -e '%s'"
    MIN_FUNCTION = 'on min(x,y)\n if x <= y\n return x\n else\n return y\n end if\n end min'
    VOLUME_GET = '{device} volume of (get volume settings)'
    VOLUME_SET = 'set volume {device} volume {volume}'
    VOLUME_CHANGE = 'set volume {device} volume (my min({max_volume}, ({device} volume of (get volume settings)){sign}{step}))'
    VOLUME_UP = 'set volume {device} volume (my min({max_volume}, ({device} volume of (get volume settings))+{step}))'
    VOLUME_DOWN = 'set volume {device} volume ({device} volume of (get volume settings))-{step}'
    MUTE_GET = '{device} muted of (get volume settings)'
    MUTE_SET = 'set volume {device} muted {mute}'
    MUTE_TOGGLE = 'set volume {device} muted not ({device} muted of (get volume settings))'

    @staticmethod
    def getDevices():
        return {'output': {'name': 'System Volume', 'mixer': []} }

    def __init__(self, device_name, mixer_name, step_up, step_down, max_volume):
        Mixer.__init__(self, device_name, mixer_name, step_up, step_down, max_volume)
        self._restore_state()

    def getVolume(self):
        try:
            retval = self._execute(self.OSASCRIPT % self.VOLUME_GET.format(device=self.device_name))
            self.volume = int('0%s' % retval)
            self._save_state()
        except Exception as e:
            debug.logError(str(e))
            traceback.print_exc()
        return Mixer.getVolume(self)

    def setVolume(self, volume, ignoreLimits=False):
        try:
            newVolume = Mixer.setVolume(self, volume, ignoreLimits)
            cmds = [self.VOLUME_SET.format(device=self.device_name, volume=newVolume),
                    self.VOLUME_GET.format(device=self.device_name)
                    ]
            retval = self._execute(self.OSASCRIPT % '\n'.join(cmds))
            self.volume = int('0%s' % retval)
            debug.logInfo('setVolume: %s' % self.volume)
            self._save_state()
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        return Mixer.getVolume(self)

    def changeVolume(self, step, ignoreLimits=False):
        try:
            sign = '+' if step >= 0 else '-'
            uStep = abs(int(step))
            cmds = [self.MIN_FUNCTION,
                    self.VOLUME_CHANGE.format(device=self.device_name, max_volume=self.max_volume, sign=sign, step=uStep),
                    self.VOLUME_GET.format(device=self.device_name)
                    ]
            retval = self._execute(self.OSASCRIPT % '\n'.join(cmds))
            self.volume = int('0%s' % retval)
            debug.logInfo('changeVolume: %s (%s)' % (self.volume, step))
            self.muted = False
            self._save_state()
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        return Mixer.getVolume(self)

    def isMuted(self):
        try:
            retval = self._execute(self.OSASCRIPT % self.MUTE_GET.format(device=self.device_name))
            self.muted = retval.lower().find('true') >= 0
            self._save_state()
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('isMuted: %s' % self.muted)
        return self.muted

    def setMute(self, mute):
        try:
            cmds = [self.MUTE_SET.format(device=self.device_name, mute='True' if mute else 'False'),
                    self.MUTE_GET.format(device=self.device_name)
                    ]
            retval = self._execute(self.OSASCRIPT % '\n'.join(cmds))
            self.muted = True if retval.lower().find('true') >= 0 else False
            self._save_state()
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('setMute: %s' % self.muted)
        return self.muted

    def muteToggle(self):
        try:
            cmds = [self.MUTE_TOGGLE.format(device=self.device_name),
                    self.MUTE_GET.format(device=self.device_name)
                    ]
            retval = self._execute(self.OSASCRIPT % '\n'.join(cmds))
            self.muted = retval.lower().find('true') >= 0
            self._save_state()
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('muteToggle: %s' % self.muted)
        return self.muted


class LinuxAlsaMixer(Mixer):

    DEVICES = "cat /proc/asound/cards"
    SIMPLE_CONTROLS = "amixer -c '{device}' scontrols"
    MIXER_GET = "amixer -c '{device}' get '{mixer}'"
    MIXER_SET = "amixer -c '{device}' set '{mixer}' {value}"

    @staticmethod
    def getDevices():
        try:
            devices = {}
            r = re.compile(r'^.+\[(?P<device>.+)\]\:\s(?P<name>.+)$')
            retval = Mixer._execute(LinuxAlsaMixer.DEVICES)
            lines = retval.split('\n')
            for line in lines:
                try:
                    g = r.match(line).groupdict()
                    devices[g['device'].strip()] = {'name': g['name'], 'mixer': []}
                except:
                    pass
            device_keys = devices.keys()
            r = re.compile(r"^.+\s'(?P<name>.+)',\d+$")
            for key in device_keys:
                retval = Mixer._execute(LinuxAlsaMixer.SIMPLE_CONTROLS.format(device=key))
                lines = retval.split('\n')
                for line in lines:
                    try:
                        g = r.match(line).groupdict()
                        devices[key]['mixer'].append(g['name'])
                    except:
                        pass
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        return devices

    def __init__(self, device_name, mixer_name, step_up, step_down, max_volume):
        Mixer.__init__(self, device_name, mixer_name, step_up, step_down, max_volume)
        self._restore_state()
        self.pattern = re.compile(r'^.+Playback\s\d+\s\[(?P<volume>[\d\.\+\-]+)%\]\s\[.+\].*$')

    def _parse_result(self, result):
        try:
            ok = False
            lines = result.split('\n')
            for line in lines:
                m = self.pattern.match(line)
                if m:
                    g = m.groupdict()
                    if g:
                        self.volume = int(g['volume'])
                        self.muted = True if '[off]' in line else False if '[on]' in line else self.muted
                        self._save_state()
                        ok = True
                        break
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        return ok

    def getVolume(self):
        try:
            retval = self._execute(self.MIXER_GET.format(device=self.device_name, mixer=self.mixer_name))
            self._parse_result(retval)
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        return Mixer.getVolume(self)

    def setVolume(self, volume, ignoreLimits=False):
        self.volume = abs(int(volume if ignoreLimits else min(self.max_volume, volume)))
        try:
            retval = self._execute(self.MIXER_SET.format(device=self.device_name, mixer=self.mixer_name, value='%s%%' % self.volume))
            self._parse_result(retval)
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('setVolume: %s' % self.volume)
        return self.volume

    def changeVolume(self, step, ignoreLimits=False):
        if not ignoreLimits and self.volume + step > self.max_volume:
            return self.setVolume(self.max_volume, ignoreLimits=ignoreLimits)
        try:
            sign = '+' if step >= 0 else '-'
            uStep = abs(int(step))
            retval = self._execute(self.MIXER_SET.format(device=self.device_name, mixer=self.mixer_name, value='%s%%%s' % (uStep, sign)))
            self._parse_result(retval)
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('changeVolume: %s (%s)' % (self.volume, step))
        return self.volume

    def isMuted(self):
        self.getVolume()
        debug.logInfo('isMuted: %s' % self.muted)
        return self.muted

    def setMute(self, mute):
        try:
            retval = self._execute(self.MIXER_SET.format(device=self.device_name, mixer=self.mixer_name, value='off' if mute else 'on'))
            self._parse_result(retval)
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('muteToggle: %s' % self.muted)
        return self.muted

    def muteToggle(self):
        try:
            retval = self._execute(self.MIXER_SET.format(device=self.device_name, mixer=self.mixer_name, value='toggle'))
            self._parse_result(retval)
        except Exception as e:
            debug.logException(e)
            traceback.print_exc()
        debug.logInfo('muteToggle: %s' % self.muted)
        return self.muted
