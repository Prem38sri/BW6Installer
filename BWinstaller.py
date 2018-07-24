# This Python file uses the following encoding: utf-8

import sys
import os
import json
import re

try:
	with open("config.json") as configfile:
    		configdata = json.load(configfile)
except ValueError as e:
	print "Something wrong with config.json, please fix it."	
	sys.exit()
except IOError as e:
	print "Wrong"
	sys.exit()

DOMAIN = configdata['DOMAIN']['property']['env']
tibcouser = configdata['DOMAIN']['property']['tibcouser']
tibcouser_home = configdata['DOMAIN']['property']['tibcouser_home']
install_home = configdata['DOMAIN']['property']['install_home']
products_to_install = configdata['DOMAIN']['property']['product_to_install']
bin_source = configdata['DOMAIN']['property']['bin_source']
#install_home_empty_check = configdata['DOMAIN']['property']['install_home_empty_check']

global product_to_install
global source
global tmp
global installlog
global lib
global fs_lower_threshold
global install_home_empty_check

install_home_empty_check = "NO"
source = tibcouser_home+"/source"
tmp = tibcouser_home+"/tmp"
installlog = tibcouser_home+"/installlog"
lib = source+"/lib"
fs_lower_threshold =4

def installer_validation():
        disk = os.statvfs(tibcouser_home)
        totalAvailSpaceNonRoot = int(disk.f_bsize*disk.f_bavail)
	totalAvailSpaceNonRoot_GB = totalAvailSpaceNonRoot/1024/1024/1024
	if os.access(install_home,os.W_OK):
                print "permission is ok"
        else:
                print "No write permission to folder  "+install_home+" for user "+os.environ['LOGNAME']
		print "Please run - chmod 755 "+install_home+" with root, programe will exit now"
                sys.exit()
	if os.access(tibcouser_home,os.W_OK):
                print "permission is ok"
        else:
                print "No write permission to folder  "+tibcouser_home+" for user "+os.environ['LOGNAME']
                print "Please run - chmod 755 "+tibcouser_home+" with root, programe will exit now"
                sys.exit()
	if not os.listdir(install_home):
		print "its empty"
		disk = os.statvfs(tibcouser_home)
		totalAvailSpaceNonRoot = float(disk.f_bsize*disk.f_bavail)
		print "available space: %d GBytes" % (totalAvailSpaceNonRoot/1024/1024/1024)
	else:
		print "Install home is not empty"
		try:
			install_home_empty_check = configdata['DOMAIN']['property']['install_home_empty_check']
			if (install_home_empty_check.upper() == "YES" or install_home_empty_check.upper() == "Y"):
                	        print "exiting"
                        	sys.exit()
			else:
				print "install home is not empty but check not set, hence proceeding"
		
		except KeyError:
			print "check not set"
			#if install_home_empty_check == Yes or install_home_empty_check == 
	if (totalAvailSpaceNonRoot_GB < fs_lower_threshold):
		print "Disk space is very less for tibcohome "+str(totalAvailSpaceNonRoot_GB)
	else:
		print "Available disk space is "+str(totalAvailSpaceNonRoot_GB)

def installer_setup():
	if not os.path.exists(source):
    		os.makedirs(source)

	if not os.path.exists(tmp):
    		os.makedirs(tmp)

	if not os.path.exists(installlog):
    		os.makedirs(installlog)

	if not os.path.exists(lib):
    		os.makedirs(lib)

def install_product():
	for product_to_install in products_to_install:
        	if (product_to_install == "BW640"):
                	if os.path.isfile(install_home+"/_installInfo/BW_6.4.0_prodInfo.xml"):
                        	print (product_to_install+" is already installed")
                	else:
                        	BW640_install(product_to_install)
        	elif (product_to_install == "BW640_HF2"):
                	if os.path.isfile(install_home+"/_installInfo/BW_6.4.0.002_prodInfo.xml"):
                        	print (product_to_install+" is already installed")
	                else:
        	                BW640_HF2_install(product_to_install)
	        elif (product_to_install == "EMS820"):
        	        if os.path.isfile(install_home+"/_installInfo/ems_8.2.0.000_prodInfo.xml"):
                	        print (product_to_install+" is already installed")
	                else:
        	                EMS820_install(product_to_install)
	        elif (product_to_install == "SAP_PLUGIN_811"):
        	        if os.path.isfile(install_home+"/_installInfo/bwpluginsap_8.1.1_prodInfo.xml"):
                	        print (product_to_install+" is already installed")
	                else:
        	                SAP_PLUGIN_811_install(product_to_install)
	        elif (product_to_install == "LargeXML_PLUGIN_610"):
        	        if os.path.isfile(install_home+"/_installInfo/bwlx_6.1.0_prodInfo.xml"):
                	        print (product_to_install+" is already installed")
	                else:
        	                LargeXML_PLUGIN_610_install(product_to_install)
	        elif (product_to_install == "SFTP_PLUGIN_611"):
        	        if os.path.isfile(install_home+"/_installInfo/bwsp_6.1.1_prodInfo.xml"):
                	        print (product_to_install+" is already installed")
	                else:
        	                SFTP_PLUGIN_611_install(product_to_install)
	        else:
        	        print ("ALL is well")


def BW640_install(product_to_install):
	###Copy binary begin here###
	print product_to_install
	product_copy(product_to_install)
	###Create silent file

	with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller_BW_6.4.0.silent",'r') as def_rf:
		def_rf_data = def_rf.read()

	def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco/bw</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
	def_rf_data = def_rf_data.replace("<!--entry key=\"environmentName\">bw6</entry-->","<entry key=\"environmentName\">"+DOMAIN+"</entry>")
	def_rf_data = def_rf_data.replace("<entry key=\"LGPLAssemblyDownload\">true</entry>","<entry key=\"LGPLAssemblyDownload\">false</entry>")
	def_rf_data = def_rf_data.replace("<entry key=\"LGPLAssemblyPath\">/opt/tibco/thirdpartyDownload</entry>","<entry key=\"LGPLAssemblyPath\">"+source+"/lib"+"</entry>")
	def_rf_data = def_rf_data.replace("<entry key=\"selectedProfiles\">Typical,Runtime</entry>","<entry key=\"selectedProfiles\">Typical</entry>")

	with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
		real_rf.write(def_rf_data)


	####Run installer

	command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86-64.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
	os.system(command_install)

	###cleanup
	product_clean(product_to_install)


def BW640_HF2_install(product_to_install):
        ###Copy binary begin here###
        print product_to_install
        product_copy(product_to_install)
        ###Create silent file

        with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller.silent",'r') as def_rf:
                def_rf_data = def_rf.read()

        def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"environmentName\">TIBCO-HOME</entry>","<entry key=\"environmentName\">"+DOMAIN+"</entry>")

        with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
                real_rf.write(def_rf_data)


        ####Run installer

        command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86-64.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
        os.system(command_install)

        ###cleanup
        product_clean(product_to_install)

def EMS820_install(product_to_install):
        ###Copy binary begin here###
        print product_to_install
        product_copy(product_to_install)
        ###Create silent file

        with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller-ems.silent",'r') as def_rf:
                def_rf_data = def_rf.read()

	def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
	def_rf_data = def_rf_data.replace("<entry key=\"environmentName\">TIBCO-HOME</entry>","<entry key=\"environmentName\">"+DOMAIN+"</entry>")
	def_rf_data = def_rf_data.replace("<entry key=\"configDirectoryRoot\">/home/user/tibco</entry>","<entry key=\"configDirectoryRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace('<entry key="feature_EMS Server Baseline_ems">true</entry>','<entry key="feature_EMS Server Baseline_ems">false</entry>')
        def_rf_data = def_rf_data.replace('<entry key="feature_Development Kit_ems">true</entry>','<entry key="feature_Development Kit_ems">false</entry>')
        def_rf_data = def_rf_data.replace('<entry key="feature_EMS Source_ems">true</entry>','<entry key="feature_EMS Source_ems">false</entry>')
        def_rf_data = def_rf_data.replace('<entry key="manualRB">true</entry>','<entry key="manualRB">false</entry>')
        def_rf_data = def_rf_data.replace("<entry key=\"configFile\">/home/user/tibco/cfgmgmt/ems/data/tibemsd.conf</entry>","<entry key=\"configFile\">"+install_home+"/tibco/cfgmgmt/ems/data/tibemsd.conf</entry>")

	with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
                real_rf.write(def_rf_data)


        ####Run installer

        command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
        os.system(command_install)

        ###cleanup
        product_clean(product_to_install)


def SAP_PLUGIN_811_install(product_to_install):
        ###Copy binary begin here###
        print product_to_install
        product_copy(product_to_install)
        ###Create silent file

        with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller_bwpluginsap_8.1.1.silent",'r') as def_rf:
                def_rf_data = def_rf.read()

        def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco/bw</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"environmentName\">bw6</entry>","<entry key=\"environmentName\">"+DOMAIN+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"configDirectoryRoot\">/opt/tibco/bw</entry>","<entry key=\"configDirectoryRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"sap.jco.dir\">/tmp</entry>","<entry key=\"sap.jco.dir\">"+lib+"/saplib</entry>")

        with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
                real_rf.write(def_rf_data)


        ####Run installer

        command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86-64.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
        os.system(command_install)
        ###cleanup
        product_clean(product_to_install)


def LargeXML_PLUGIN_610_install(product_to_install):
        ###Copy binary begin here###
        print product_to_install
        product_copy(product_to_install)
        ###Create silent file

        with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller_bwlx_6.1.0.silent",'r') as def_rf:
                def_rf_data = def_rf.read()

        def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco/bw</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"environmentName\">bw6</entry>","<entry key=\"environmentName\">"+DOMAIN+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"configDirectoryRoot\">/opt/tibco/bw</entry>","<entry key=\"configDirectoryRoot\">"+install_home+"</entry>")

        with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
                real_rf.write(def_rf_data)


        ####Run installer

        command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86-64.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
        os.system(command_install)
        ###cleanup
        product_clean(product_to_install)



def SFTP_PLUGIN_611_install(product_to_install):
        ###Copy binary begin here###
        print product_to_install
        product_copy(product_to_install)
        ###Create silent file

        with open(source+"/"+product_to_install+"/TIBCOUniversalInstaller_bwsp_6.1.1.silent",'r') as def_rf:
                def_rf_data = def_rf.read()

        def_rf_data = def_rf_data.replace("<entry key=\"installationRoot\">/opt/tibco/bw</entry>","<entry key=\"installationRoot\">"+install_home+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"environmentName\">bw6</entry>","<entry key=\"environmentName\">"+DOMAIN+"</entry>")
        def_rf_data = def_rf_data.replace("<entry key=\"configDirectoryRoot\">/opt/tibco/bw</entry>","<entry key=\"configDirectoryRoot\">"+install_home+"</entry>")

        with open(source+"/"+product_to_install+"/"+product_to_install+".silent",'w') as real_rf:
                real_rf.write(def_rf_data)


        ####Run installer

        command_install = source+"/"+product_to_install+"/TIBCOUniversalInstaller-lnx-x86-64.bin -silent -V responseFile="+source+"/"+product_to_install+"/"+product_to_install+".silent -is:tempdir "+tmp
        os.system(command_install)
        ###cleanup
        product_clean(product_to_install)


def bw_configure():

	#install maven plugin
	command_maven_install = install_home+"/tibcojre64/1.8.0/bin/java -jar "+bin_source+"/ESBAuditPlugin_6.4_installer/ESBAudit-RuntimeInstaller/devkitpackager.jar -ri install -th "+install_home+" -i "+bin_source+"/ESBAuditPlugin_6.4_installer/ESBAudit-P2Installer"
	os.system(command_maven_install)

	#install ems-driver
	if not os.path.isfile(install_home+"/_installInfo/ems_8.2.0.000_prodInfo.xml"):
		print "EMS Client is not installed, hence skipping the ems-driver installation"
	else:
		command_ems_driver_install = install_home+"/bw/6.4/bin/bwinstall --propFile "+install_home+"/bw/6.4/bin/bwinstall.tra ems-driver -Dzip.location.esc="+install_home+"/components/shared/1.0.0/plugins"
		os.system(command_ems_driver_install)

	#install oracle-driver
	command_db_driver_copy = "cp "+bin_source+"/lib/jdbc/ojdbc6.jar "+install_home+"/bw/6.4/config/drivers/shells/jdbc.oracle.runtime/runtime/plugins/com.tibco.bw.jdbc.datasourcefactory.oracle/lib"
	print command_db_driver_copy
	os.system(command_db_driver_copy)
	command_db_driver_install = install_home+"/bw/6.4/bin/bwinstall --propFile "+install_home+"/bw/6.4/bin/bwinstall.tra oracle-driver"
	os.system(command_db_driver_install)

	#update heap in bwagent.tra
	with open(install_home+"/bw/6.4/bin/bwagent.tra",'r') as ref_bwagent:
		ref_bwagent_data = ref_bwagent.read()
		ref_bwagent_data = ref_bwagent_data.replace("java.extended.properties=-Xmx1024m -Xms256m -XX:+HeapDumpOnOutOfMemoryError -XX:SurvivorRatio=128 -XX:MaxTenuringThreshold=0  -XX:+UseTLAB -XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled","java.extended.properties=-Xmx4096m -Xms1024m -XX:+CrashOnOutOfMemoryError -Djava.security.egd=file:///dev/urandom")
	with open(install_home+"/bw/6.4/bin/bwagent.tra",'w') as ref_bwagent:
		ref_bwagent.write(ref_bwagent_data)

	#update heap in bwappnode.tra
	with open(install_home+"/bw/6.4/bin/bwappnode.tra",'r') as ref_bwappnode:
                ref_bwappnode_data = ref_bwappnode.read()
                ref_bwappnode_data = ref_bwappnode_data.replace("java.extended.properties=-Xmx1024m -Xms128m -XX:+HeapDumpOnOutOfMemoryError","java.extended.properties=-Xmx2048m -Xms256m -XX:+UseG1GC -XX:+CrashOnOutOfMemoryError")
        with open(install_home+"/bw/6.4/bin/bwappnode.tra",'w') as ref_bwappnode:
                ref_bwappnode.write(ref_bwappnode_data)
	
	#update bwagent-logback.xml
	with open(install_home+"/bw/6.4/bin/bwagent-logback.xml",'r') as logback:
		logback_data = logback.read()
		logback_data = logback_data.replace("""<pattern>%d{HH:mm:ss.SSS} %-5level [%thread] %logger{36} - %msg%n</pattern>""","""<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] %logger{36} - %msg%n</pattern>""")

	with open(install_home+"/bw/6.4/bin/bwagent-logback.xml",'w') as logback:
		logback.write(logback_data)

	#update bwagent_db.json file
 	
	try:
		bwagentnetworkname_new  = configdata['DOMAIN']['property']['bwagentnetworkname']
		membername_new  = configdata['DOMAIN']['property']['membername']
		httpport_new  = configdata['DOMAIN']['property']['httpport']
		dbconnectionurl_new = configdata['DOMAIN']['property']['dbconnectionurl']
		dbuser_new = configdata['DOMAIN']['property']['dbuser']
		dbpassword_new = configdata['DOMAIN']['property']['dbpassword']
		emsserverurl_new = configdata['DOMAIN']['property']['emsserverurl']
		emsusername_new = configdata['DOMAIN']['property']['emsusername']
		emsuserpassword_new = configdata['DOMAIN']['property']['emsuserpassword']
	except KeyError:
       		print "check not set"

		
	with open(install_home+"/bw/6.4/config/bwagent_db.json",'r') as bw_db_json:
		bw_db_json_data = bw_db_json.read()
		#Obfuscate DB Password
		dbpasswd_obfuscate = install_home+"/bw/6.4/bin/bwadmin --propFile "+install_home+"/bw/6.4/bin/bwadmin.tra obfuscate \""+dbpassword_new+"\"|tail -1"
		dbpassword_new_encrypt = os.popen(dbpasswd_obfuscate).read()
		dbpassword_new_encrypt = re.sub(r'Obfuscated password: ','',dbpassword_new_encrypt)
		dbpassword_new_encrypt = dbpassword_new_encrypt.rstrip()
		
		#Obfuscate DB Password
		emsuserpasswd_obfuscate = install_home+"/bw/6.4/bin/bwadmin --propFile "+install_home+"/bw/6.4/bin/bwadmin.tra obfuscate \""+emsuserpassword_new+"\"|tail -1"
		emsuserpassword_new_encrypt = os.popen(emsuserpasswd_obfuscate).read()
		emsuserpassword_new_encrypt = re.sub(r'Obfuscated password: ','',emsuserpassword_new_encrypt)
		emsuserpassword_new_encrypt = emsuserpassword_new_encrypt.rstrip()
		abc = "abc"

		bw_db_json_data = re.sub(r'bwagentnetworkname: (.+),',"bwagentnetworkname: "+bwagentnetworkname_new+",",bw_db_json_data)
		bw_db_json_data = re.sub(r'membername: "(.+)",',"membername: \""+membername_new+"\",",bw_db_json_data)
		bw_db_json_data = re.sub(r'httpport: (.+),',"httpport: "+httpport_new+",",bw_db_json_data)
		bw_db_json_data = re.sub(r'dbtype: postgresql,','dbtype: oracle,',bw_db_json_data)
		bw_db_json_data = re.sub(r'dbdriver: "org.postgresql.Driver",','dbdriver: "oracle.jdbc.driver.OracleDriver",',bw_db_json_data)
		bw_db_json_data = re.sub(r'dbconnectionurl: "(.+)",',"dbconnectionurl: \""+dbconnectionurl_new+"\",",bw_db_json_data)
		bw_db_json_data = re.sub(r'dbuser: (.+),',"dbuser: "+dbuser_new+",",bw_db_json_data)
		bw_db_json_data = re.sub(r'dbpassword: (.+),',"dbpassword: \""+dbpassword_new_encrypt+"\",",bw_db_json_data)
		bw_db_json_data = re.sub(r'emsserverurl: "(.+)",',"emsserverurl: \""+emsserverurl_new+"\",",bw_db_json_data)
		bw_db_json_data = re.sub(r'emsusername: (.+),',"emsusername: "+emsusername_new+",",bw_db_json_data)
		bw_db_json_data = re.sub(r'emsuserpassword: "",',"emsuserpassword: \""+emsuserpassword_new_encrypt+"\",",bw_db_json_data)
	with open(install_home+"/bw/6.4/config/bwagent_db.json",'w') as bw_db_json:
		bw_db_json.write(bw_db_json_data)	

	#confgire bwagent.ini for agent
	command_config_bwagent_ini = install_home+"/bw/6.4/bin/bwadmin --propFile "+install_home+"/bw/6.4/bin/bwadmin.tra config -cf "+install_home+"/bw/6.4/config/bwagent_db.json agent"
	os.system(command_config_bwagent_ini)






### common functions
def product_copy(product_to_install):
        command_copy_lib = "cp -R "+bin_source+"/lib "+source
        os.system(command_copy_lib)
        #commented lines will copy zip locally and extract, which require mode disk space. Use either this 4 line or last 2 uncommented,which will use zip from NAS and extract in local folder
        #command_copy_product = "cp "+bin_source+"/"+product_to_install+".zip "+source
        #os.system(command_copy_product)
        #command_extract_zip = "unzip -d "+source+"/"+product_to_install+" "+source+"/"+product_to_install+".zip"
        #os.system(command_extract_zip)

        command_extract_zip = "unzip -d "+source+"/"+product_to_install+" "+bin_source+"/"+product_to_install+".zip"
        os.system(command_extract_zip)

def product_clean(product_to_install):
        command_cleanup_product_folder = "rm -rf "+source+"/"+product_to_install
        os.system(command_cleanup_product_folder)
        #Uncommnet only if zip is copied locally and not user from NAS
        #command_cleanup_product_zip = "rm -rf "+source+"/"+product_to_install+".zip"
        #os.system(command_cleanup_product_zip)


##main functtion

try:
        config_bwagent = configdata['DOMAIN']['action']['install']
        if (config_bwagent.upper() == "YES" or config_bwagent.upper() == "Y"):
                print "starting installation"
		installer_validation()
		installer_setup()
		install_product()
        else:
                print "install not set"
except KeyError:
        print "insall property not setcorrectly" 

try:
	config_bwagent = configdata['DOMAIN']['action']['config_bwagent']
	if (config_bwagent.upper() == "YES" or config_bwagent.upper() == "Y"):
        	print "starting config"
		bw_configure()
        else:
                print "config not set"
except KeyError:
	print "config property not set"

