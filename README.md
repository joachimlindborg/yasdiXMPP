yasdiXMPP
=========

  This is an XMPP-IoT python implementation with the yasdi driver to reach an SMA inverter over serial RS485 line

  sourcecode for the yasdi driver can be fetched from http://www.sma-uk.com/en_UK/products/software/yasdi.html and     building instructions can be found https://github.com/Donderda/SMysqLogger/tree/master/yasdi.

  I have built the driver on Raspberry with Wheezy and then incorporate the pyYasdi.py and yasdiwrapper.py for python

  The code is then connected to the XMPP-IoT implementation from SleekXMPP available at https://github.com/joachimlindborg/SleekXMPP/tree/xep_0323_325

  Building the yasdi sourcecode

    get the yasdisourcecode onto the raspberry
    scp -r yasdi-1.8.1build9-src pi@192.168.0.52:/home/pi/

    cd ../yasdi-1.8.1build9-src/projects
    mkdir build-gcc
    cd build-gcc/
    cmake ../generic-cmake/
    make
    make install
  
  pi@raspberrypi ~/yasdi-1.8.1build9-src/projects/build-gcc $ sudo make install
[ 55%] Built target yasdi
[ 57%] Built target yasdi_drv_ip
[ 60%] Built target yasdi_drv_serial
[ 97%] Built target yasdimaster
[100%] Built target yasdishell
Install the project...
-- Install configuration: ""
-- Installing: /usr/local/bin/yasdishell
-- Removed runtime path from "/usr/local/bin/yasdishell"
-- Installing: /usr/local/lib/libyasdi.so.1.8.1
-- Installing: /usr/local/lib/libyasdi.so.1
-- Installing: /usr/local/lib/libyasdi.so
-- Installing: /usr/local/lib/libyasdimaster.so.1.8.1
-- Installing: /usr/local/lib/libyasdimaster.so.1
-- Installing: /usr/local/lib/libyasdimaster.so
-- Removed runtime path from "/usr/local/lib/libyasdimaster.so.1.8.1"
-- Installing: /usr/local/lib/libyasdi_drv_ip.so.1.8.1
-- Installing: /usr/local/lib/libyasdi_drv_ip.so.1
-- Installing: /usr/local/lib/libyasdi_drv_ip.so
-- Removed runtime path from "/usr/local/lib/libyasdi_drv_ip.so.1.8.1"
-- Installing: /usr/local/lib/libyasdi_drv_serial.so.1.8.1
-- Installing: /usr/local/lib/libyasdi_drv_serial.so.1
-- Installing: /usr/local/lib/libyasdi_drv_serial.so
-- Removed runtime path from "/usr/local/lib/libyasdi_drv_serial.so.1.8.1"


running the pyYASDI.py application to test the drivers

  cd yasdi
  python pyYASDI.py
  
