----------------------------------------------------------------------------------------------------
#how to update java windows 10
java control panel-update tab

start menu-Type here to search-Environment Variables-System Variables
C:\Program Files\Java\jdk-17.0.2 #Set the JAVA_HOME System Path
%JAVA_HOME%\bin; #Confirm that the path to JAVA_HOME,Append the path to the JDK (up to the bin folder) as the PATH value
----------------------------------------------------------------------------------------------------
#Installing the JDK from the Command Line
msiexec.exe /i installer.msi  #Basic UI mode
msiexec.exe /i installer.msi /L C:\path\setup.log #Creating a Log File
msiexec.exe installer.msi /qn   #Silent mode
msiexec.exe installer.msi /qn /L C:\path\setup.log  #Creating a Log File

MsiExec.exe/X{<UninstallString>}  #Uninstalling the JDK in Silent Mode
#Finding the JDK Registry Key and UninstallString Value
HKEY_LOCAL_MACHINE/Software/Microsoft/Windows/CurrentVersion/Uninstall

#During installation, the following files are copied to the location mentioned
#Alternatively, run these executables directly from the JDK's bin directory. 
"C:\Program Files\Common Files\Oracle\Java\javapath\java.exe" 
"C:\Program Files\Common Files\Oracle\Java\javapath\javaw.exe"
"C:\Program Files\Common Files\Oracle\Java\javapath\javac.exe" 
"C:\Program Files\Common Files\Oracle\Java\javapath\jshell.exe"

#Instead of double-clicking or opening the JDK installer,Installing the JDK Silently
jdk.exe /s
----------------------------------------------------------------------------------------------------
java -version // JRE version
javac -version // Java compiler version 
java -XshowSettings:properties -version # detailed information about java version
----------------------------------------------------------------------------------------------------
# how to clone github project Eclipse IDE

Menu- - Perspective - Git Repositories and click on Add Git Repo
----------------------------------------------------------------------------------------------------
# add project in local git repository

Import - Git - Projects from Git - Existing Local Repository 
----------------------------------------------------------------------------------------------------
# add project from github url

Import - Git - Projects from Git - Existing Local Repository - Clone URI
----------------------------------------------------------------------------------------------------
# ...references non-existing project eclipse...
Project->properties -  "Project Facets" -"Convert to faceted form" - choose your server and JDK version - Apply and Close.
----------------------------------------------------------------------------------------------------
Problem:eclipse update/upgrade windows 10

Incompatible JVM. Version 1.8.0_261 of the JVM is not suitable for this product. Version: 11 or greater is required in Eclipse

Fix:
Add the -vm parameters in the eclipse configuration file

>java --version
java 17.0.2 2022-01-18 LTS
Java(TM) SE Runtime Environment (build 17.0.2+8-LTS-86)
Java HotSpot(TM) 64-Bit Server VM (build 17.0.2+8-LTS-86, mixed mode, sharing)

back up first
notepad C:\Users\username\Downloads\jee-2022-03\eclipse\eclipse.ini

#add the following two lines directly before the line -vmargs in eclipse.ini
-vm
C:\Program Files\Java\jdk-17.0.2\bin\javaw.exe
----------------------------------------------------------------------------------------------------
Problem:java control panel missing update tab windows 10

Fix:
"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\JavaSoft\Java Update\Policy".
set to 1 (hexa)
EnableJavaUpdate
