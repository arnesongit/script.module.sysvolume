# script.module.sysvolume

This Kodi module contains callable scripts to change the system volume on Linux/ALSA and on macOS 

See [changelog.txt](https://github.com/arnesongit/script.change.sysvolume/blob/master/changelog.txt) for informations.

## Installation

1. Download the zip file [from this folder](https://github.com/arnesongit/repo/tree/master/script.change.sysvolume) from github
2. Use "Install from Zip" Method to install the addon.
   Or you install the Addon from my (Repository)[https://github.com/arnesongit/repository.arneson/raw/master/repository.arneson/repository.arneson-0.1.1.zip].
3. The Addon appears in Programs,

## Using the Addon functions

To select the System Audio Device, call "System Volume Changer" from the Programs Menu.

In the Addon Settings you can
- Set the Device Name and Mixer Name manually
- Modify the Volume step
- Set a Volume Limit
- Endble/Disable the Progress Dialog which shows the Volume Level after changing it

The volume can be changed with following script functions:
```
RunScript(script.change.sysvolume,up)
RunScript(script.change.sysvolume,down)
RunScript(script.change.sysvolume,muteToggle)
```
You you can also use the folowing funtions to change the volume or the mute status:
```
RunScript(script.change.sysvolume,change,10)        to increase the volume by 10%
RunScript(script.change.sysvolume,change,-10)       to decrease the volume by 10%
RunScript(script.change.sysvolume,set,45)           to set the volume to 45%
RunScript(script.change.sysvolume,mute,true)        to mute the volume
RunScript(script.change.sysvolume,mute,false)       to unmute the volume
```
Modify the keyboard.xml to change the volume with keyboard shortcuts.

Example:
```
<keymap>
  <global>
    <keyboard>
      <f8>RunScript(script.change.sysvolume,muteToggle)</f8>
      <f9>RunScript(script.change.sysvolume,down)</f9>
      <f10>RunScript(script.change.sysvolume,up)</f10>
      <f9 mod="ctrl">RunScript(script.change.sysvolume,change,-10)</f9>
      <f10 mod="ctrl">RunScript(script.change.sysvolume,change,10)</f10>
    </keyboard>
  </global>
</keymap>
```