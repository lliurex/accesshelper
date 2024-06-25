#!/bin/bash
DBG=0
LOG=/tmp/pulsesddm-$(date +%Y%m%d_%H%M).log
function debug()
{
	[ $DBG -eq 1 ] && echo "$1" >> $LOG
}
debug "-----" 
debug "$(date)"
debug "$(whoami)"
if [ -z "$(ps  -ef | grep $USER | grep a11y1)" ] 
then
	/usr/bin/dbus-launch /usr/libexec/at-spi2-registryd & >> $LOG 
	/usr/bin/dbus-launch /usr/libexec/at-spi-bus-launcher --a11y=1 --screen-reader=1 & >> $LOG
fi
pulseaudio -k || true
dbus-launch pulseaudio --daemonize=no
exit 0
