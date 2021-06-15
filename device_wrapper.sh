#!/bin/bash
 
# 5.12.2018
# Wrapper zum Starten von AgilisAGP.py 


# Exportieren der Variable TANGO_HOST fuer die Bash-Shell
 
export TANGO_HOST=angstrom.hhg.lab:10000

 
TANGOHOST=angstrom.hhg.lab
 
#Umleiten der Ausgabe in eine Log-Datei
exec &>> /home/pi/Tango_Devices/Hall_Probe/device.log
 
echo "---------------------------"
echo $(date)
echo "Tangohost: " $TANGOHOST
 
# Warten bis der Tangohost sich meldet
while ! timeout 0.2 ping -c 1 -n $TANGOHOST &> /dev/null
do
  :
# mache nix  
done
 
echo "ping Tangohost successful!"
echo "starting Hall_Probe device"
 
# Fork/exec
(
  exec /usr/bin/python3 /home/pi/Tango_Devices/Hall_Probe/hallProbe.py MOKE &
) 
&>> /home/pi/Tango_Devices/Hall_Probe/device.log