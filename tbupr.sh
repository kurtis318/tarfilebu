#!/bin/bash

## Need to make the next 2 as parameters and check if directories exist.

FROMDIR="/mnt/usb/kwrp50-009"
TODIR="/home/kurtis"
IMGDIR="${FROMDIR}/__KVM_IMAGES__"

function timer()
{
    #   local START_T=$( timer );local ETIME=0;
    #   START_T=$( timer );ETIME=0;
    #   <code to instrument goes here>
    #   ETIME=$(timer "${START_T}" )
    if [[ $# -eq 0 ]]; then
        echo $(($(date +%s%N)/1000000))
    else
        local  START_T=$1
        local END_T=$(($(date +%s%N)/1000000))
        if [[ -z $START_T ]]; then
            START_T=$END_T=$;
        else
            local ELAPSED_TIME=$(($END_T - $START_T))
            local T=$(bc<<<"scale=2; ${ELAPSED_TIME}/1000")
            local SECS=$( printf '%3.2f\n' $T)
            local T=$(bc<<<"scale=2; ${ELAPSED_TIME}/60000")
            local MINS=$( printf '%3.2f\n' $T)
            echo "${ELAPSED_TIME} ms/${SECS} sec/${MINS} min"
        fi

    fi
}
## Here is the main tar file extraction loop.
## tbup.sh will create a non-compressed tar file in the backup directory.
## Process every tar file.  There could be . direcotries and files which will 
## constitute a complete file backup.

echo
TSTART=$( date +%s%N )
ls $FROMDIR/*.tar|while read TF; do 
  echo "#########################################################################" 
  DSIZE=$(tar tvf $TF | sed 's/ \+/ /g' | cut -f3 -d' ' | sed '2,$s/^/+ /' | paste -sd' ' | bc)
  TFNUMF=$( tar -tf $TF |grep -v "/$"|wc -l)
  TFNUMD=$( tar -tf $TF |grep "/$"|wc -l )
  echo "  <TF=${TF}> <DSIZE=${DSIZE}> <TFNUMF=${TFNUMF}> <TFNUMD=${TFNUMD}>"

  START_T=$( timer );ETIME=0
  tar -C $TODIR -pxf $TF
  ETIME=$( timer "${START_T}" )

  TSIZE=$( du -sh ${TODIR}${DIR} 2>&1 | awk '{print $1;}' )
  TNUMF=$( find ${TODIR}${DIR} -type f 2>&1 | wc -l )
  TNUMD=$( find ${TODIR}${DIR} -type d 2>&1 | wc -l )
  DIR="${TF##*/}"; DIR="${TODIR}/${DIR%.*}"
  echo "  <DIR=${DIR}> <DSIZE=${DSIZE}> <TFNUMF=${TFNUMF}> <TFNUMD=${TFNUMD}>"
  echo "  <ETIME=${ETIME}>"

done

## Check for images subdirectory in the tar file directory.
## tbup.sh will create this from /var/lib/libvirt/images which are the 
## KVM image files.  This can be a read big directory.

echo "#########################################################################" 
if [[ -d $IMGDIR ]]; then

  echo "  Found images directory <IMGDIR=${IMGDIR}>.  Restoring directory. This could take a while."

  DSIZE=$( du -sh ${IMGDIR} 2>&1 | awk '{print $1;}' )
  DNUMF=$( find ${IMGDIR} -type f 2>&1 | wc -l )
  DNUMD=$( find ${IMGDIR} -type d 2>&1 | wc -l )
  echo "  <DIR=${IMGDIR}> <DSIZE=${DSIZE}> <DNUMF=${DNUMF}> <TFNUMD=${DNUMD}>"

  START_T=$( timer );ETIME=0
  rsync -avhW --no-compress --progress $IMGDIR $TODIR
  ETIME=$( timer "${START_T}" )
  echo "  <ETIME=${ETIME}>"

else

  echo "  No images director found <IMGDIR=${IMGDIR}>."

fi
  
## All done.  Display total elapsed time this script ran.

echo
ETIME=$( echo "scale=4; ($TEND - $TSTART) / 1000000000" | bc  -l | awk '{printf "%.2f", $1}' )
echo "<ETIME=${ETIME}>"
echo

exit 0
