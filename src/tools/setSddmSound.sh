w
!/bin/bash
DBG=1
LOG=/tmp/playSound-$(date +%Y%m%d_%H%M).log
function debug()
{
	[ $DBG -eq 1 ] && echo "$1" >> $LOG
}
debug "-----"
#debug"DSP: $0 $@">$LOG
export DISPLAY=$1
export XAUTHORITY=$2
export HOME=$(mktemp -d)
chown sddm:sddm $HOME
debug "$(date)"
debug "$(whoami)"
#debug"Sleeping 2"
#Sleep for avoiding race conditions with pulse 
sleep 2
debug "XAUTH: $XAUTHORITY"
if [ -z "$(ps  -ef | grep $USER | grep spi2|grep -v grep)" ] 
then
	debug "Launching spi2"
	#pkexec --user sddm /usr/bin/dbus-launch /usr/libexec/at-spi2-registryd & >> $LOG 
	#pkexec --user sddm /usr/bin/dbus-launch /usr/libexec/at-spi-bus-launcher --a11y=1 --screen-reader=1 & >> $LOG
	sudo -n -u sddm /usr/bin/dbus-launch /usr/libexec/at-spi2-registryd & >> $LOG 
	sudo -n -u sddm /usr/bin/dbus-launch /usr/libexec/at-spi-bus-launcher --a11y=1 --screen-reader=1 & >> $LOG
fi
#pkexec --user sddm /usr/bin/mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg >>$LOG 2>>$LOG
sudo -n -u sddm /usr/bin/mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg >>$LOG 2>>$LOG
debug "Launching ORCA"
sudo -n -u sddm  /usr/bin/xbrlapi -q &
sudo -n -u sddm /usr/bin/orca --replace &
debug "Orca: $?"
debug "----"
exit 0
