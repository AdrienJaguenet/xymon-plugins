#!/bin/bash                                                                                                                                                                      
#Verifying if the backup plan is working or not                                                                                                                                  
#Heavily inspired by https://camille.wordpress.com/2017/09/20/incremental-backups-with-duplicity-plus-nagios-monitoring/
Test=duplicity
Tmp_xymon_file=/tmp/xymon-duplicity.tmp

if [ "$1" == "debug" ] ; then
	echo "Debug mode"
	XYMON=echo
	XYMONDISP=your_xymon_server
	MACHINE=your_host
fi

grep -q "&red" $Tmp_xymon_file
if [ $? -eq 0 ] ; then
	red=1
else
	grep -q "&yellow" $Tmp_xymon_file
	if [ $? -eq 0 ] ; then
		yellow=1
	fi
fi

#Define global status
if [ "$red" == 1 ] ; then
	global_color=red
elif [ "$yellow" == 1 ] ; then
	global_color=yellow
else
	global_color=green
fi

#Send Xymon the results
"$XYMON" "$XYMSRV" "status+"$INTERVAL" "$MACHINE"."$Test" "$global_color" $(date)

$(cat $Tmp_xymon_file)
"
