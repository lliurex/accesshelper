#!/bin/bash
LOG=/tmp/pulsesddm-$(date +%Y%m%d_%H%M).log
echo "-----" > $LOG
date >> $LOG
whoami >> $LOG
#chmod 777 $LOG
#echo "TIME" >> $LOG
#sleep 5
#echo "TIME OK" >> $LOG
[ -z "$(ps  -ef | grep $USER | grep a11y1)" ] && /usr/bin/dbus-launch /usr/libexec/at-spi2-registryd & >> $LOG && /usr/bin/dbus-launch /usr/libexec/at-spi-bus-launcher --a11y=1 --screen-reader=1 & >> $LOG
pulseaudio -k || true
dbus-launch pulseaudio --daemonize=no
#echo "Dbus-launch: $?" >> $LOG
#export DISPLAY=:0
#export XAUTHORITY=$(sudo -u sddm ls -1 /var/run/sddm/ | head -n1)
#echo "XAUTH: $XAUTHORITY" >> $LOG
#env>/tmp/env
#export XAUTHORITY=$(ls -1 /var/run/sddm/ | head -n1)
#su -c "/usr/bin/orca --replace" sddm >> $LOG
#sudo -p -u sddm /usr/bin/orca --replace --debug-file /tmp/b & #2>> $LOG
#/usr/bin/orca --replace
#echo "----" >> $LOG
##sudo -u sddm /usr/bin/spd-say "hola" 1>>/tmp/atlaunch2 2&>1
##/usr/bin/espeak "LliureX" 1>/tmp/c 2>&1
##/usr/bin/spd-say "LliureX" 1>/tmp/c 2>&1
#sudo -u sddm mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg 
#echo "Orca: $?" >> $LOG
#echo "----" >> $LOG
exit 0
