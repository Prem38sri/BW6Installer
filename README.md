# BW6Installer
Python script to install BW6 and configure with DB and EMS for persistence

Steps to execute -

Edit config.json with properties with all details(Maintain the order of Product installation like BW, BWHF, PLugin etc
run as /bin/python ./install.py

Script will read values from the json file names config.json and perfome installation and configuration(DB Driver, EMS Driver, update jvm propeties for .tra files etc.

