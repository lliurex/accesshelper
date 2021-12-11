 #!/bin/bash
 #Copyright 2021 Team LliureX
 #Simple script to copy profiles to app dir
 WRKDIR="/usr/share/acceshelper/profiles"
 DESTPATH=${WRKDIR}/$(basename $2)
 
 mkdir $DESTPATH 2>/dev/null
 cp -r $1 $DESTPATH

 #And that's all
