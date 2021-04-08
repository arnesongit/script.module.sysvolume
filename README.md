# script.module.sysvolume

This Kodi module contains callable scripts to change the system volume on Linux/ALSA and on macOS 

See [changelog.txt](https://github.com/arnesongit/script.module.sysvolume/blob/master/changelog.txt) for informations.

## Manual Installation

1. Download the zip file from the repository folder [for Kodi 19](https://github.com/arnesongit/repository.tidal2/tree/main/script.module.sysvolume)
   or [for Kodi 17 and 18](https://github.com/arnesongit/repository.tidal2/tree/until-leia/script.module.sysvolume).
2. Use "Install from Zip" Method to install the addon. You have to allow third party addon installation in the Kodi settings !
3. The addon appears as a "Program Addon".

## Installation with TIDAL2 Repository

With this method you will get updates automatically.

1. Download the Repository zip file [for Kodi 19](https://github.com/arnesongit/repository.tidal2/blob/main/repository.tidal2/repository.tidal2-0.2.0.zip?raw=true)
   or [for Kodi 17 and 18](https://github.com/arnesongit/repository.tidal2/blob/until-leia/repository.tidal2/repository.tidal2-0.1.0.zip?raw=true).
2. Use "Install from Zip" Method to install the repository. You have to allow third party addon installation in the Kodi settings !
3. Install the sysvolume addon from this repository.
4. The addon appears as a "Program Addon".

## Using the Addon functions

To select the System Audio Device, call "System Volume Changer" from the Programs Menu.

In the Addon Settings you can
- Set the Device Name and Mixer Name manually
- Modify the Volume step
- Set a Volume Limit
- Endble/Disable the Progress Dialog which shows the Volume Level after changing it

The volume can be changed with following script functions:
```
RunScript(script.module.sysvolume,up)
RunScript(script.module.sysvolume,down)
RunScript(script.module.sysvolume,muteToggle)
```
You you can also use the folowing funtions to change the volume or the mute status:
```
RunScript(script.module.sysvolume,change,10)        to increase the volume by 10%
RunScript(script.module.sysvolume,change,-10)       to decrease the volume by 10%
RunScript(script.module.sysvolume,set,45)           to set the volume to 45%
RunScript(script.module.sysvolume,mute,true)        to mute the volume
RunScript(script.module.sysvolume,mute,false)       to unmute the volume
```
Modify the keyboard.xml to change the volume with keyboard shortcuts.

Example:
```
<keymap>
  <global>
    <keyboard>
      <f8>RunScript(script.module.sysvolume,muteToggle)</f8>
      <f9>RunScript(script.module.sysvolume,down)</f9>
      <f10>RunScript(script.module.sysvolume,up)</f10>
      <f9 mod="ctrl">RunScript(script.module.sysvolume,change,-10)</f9>
      <f10 mod="ctrl">RunScript(script.module.sysvolume,change,10)</f10>
    </keyboard>
  </global>
</keymap>
```