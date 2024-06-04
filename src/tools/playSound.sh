#!/bin/bash
LOG=/tmp/playSound-$(date +%Y%m%d_%H%M).log
echo "-----" > $LOG
echo "DSP: $0 $@">$LOG
export DISPLAY=$1
export XAUTHORITY=$2
date >> $LOG
whoami >> $LOG
echo "Sleeping 2"
sleep 2
#chmod 777 $LOG
echo "XAUTH: $XAUTHORITY" >> $LOG
#/usr/bin/orca --replace  >> $LOG &
#su -m -c "/usr/bin/orca --replace" sddm >> $LOG
#sudo -n -E -b -u sddm /usr/bin/orca --replace >> $LOG
pkexec --user sddm /usr/bin/mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg >>$LOG 2>>$LOG
#/usr/bin/mplayer /usr/share/sounds/Oxygen-Im-Phone-Ring.ogg >>$LOG 2>>$LOG
sudo -n -u sddm /usr/bin/orca --replace >> $LOG
echo "Orca: $?" >> $LOG
echo "----" >> $LOG
touch /tmp/.orca
exit 0
