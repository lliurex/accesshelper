#!/bin/bash
DBG=0
LOG=/tmp/playSound-$(date +%Y%m%d_%H%M).log
function debug()
{
	[ $DBG -eq 1 ] && echo "$1" >> $LOG
}
debug "-----"
#debug"DSP: $0 $@">$LOG
export DISPLAY=$1
export XAUTHORITY=$2
debug "$(date)"
debug "$(whoami)"
#debug"Sleeping 2"
#Sleep for avoiding race conditions with pulse 
sleep 2
debug "XAUTH: $XAUTHORITY"
pkexec --user sddm /usr/bin/mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg >>$LOG 2>>$LOG
sudo -n -u sddm /usr/bin/orca --replace >> $LOG
debug "Orca: $?"
debug "----"
exit 0
