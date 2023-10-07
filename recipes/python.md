============================================================================
pip-compile --output-file requirements.txt requirements.in
============================================================================
python -V
python3 -V

============================================================================
Method 1:from source
apt-get install zlib1g-dev
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz
tar -xvf Python-3.6.3.tgz
cd Python-3.6.3
./configure
make 
make install
python3.6 -V

============================================================================
Method 2: Install Python 3.6 from PPA
apt-get install software-properties-common python-software-properties
add-apt-repository ppa:jonathonf/python-3.6
apt-get update
apt-get install python3.6
python3.6 -V


$ python3 -V
Python 3.6.5
$ python -V
Python 2.7.15rc1

#change version
$ which python3
/usr/bin/python3
vi .bashrc
alias python='/usr/bin/python3'
$ python --version
Python 3.6.5
============================================================================
# install pip and Python 2.7
sudo apt-get install -y python-pip
pip --version

# install pip and Python 3
sudo apt install python3-venv python3-pip
pip3 --version

# install “SomePackage” into an environment with site.USER_BASE customized to ‘/myappenv’, do the following:
# pip will not perform a --user install in a --no-site-packages virtualenv (i.e. the default kind of virtualenv), 
# due to the user site not being on the python path. The installation would be pointless
export PYTHONUSERBASE=/myappenv
pip install --user SomePackage

# From within a --no-site-packages virtualenv (i.e. the default kind):
pip install --user requests
Can not perform a '--user' install. User site-packages are not visible in this virtualenv.
# From within a --system-site-packages virtualenv where SomePackage==0.3 is already installed in the virtualenv:
pip install --user SomePackage==0.4
Will not install to the user site because it will lack sys.path precedence
# From within a real python, where SomePackage is not installed globally:
pip install --user SomePackage
# From within a real python, where SomePackage is installed globally, but is not the latest version
pip install --user SomePackage
pip install --user --upgrade SomePackage

# From within a real python, where SomePackage is installed globally, and is the latest version
pip install --user SomePackage
pip install --user --upgrade SomePackage
pip install --user --ignore-installed SomePackage
============================================================================
Prerequisites
python -V
python3 -V

# Install Virtualenv
sudo apt-get install python-virtualenv # method1
sudo easy_install virtualenv # method2
sudo pip install virtualenv # method3
conda install virtualenv # method4
virtualenv --version

# create and activate the virtual environment
mkdir ~/virtualenvironment
# create a folder for your new app
virtualenv ~/virtualenvironment/my_new_app
# add --no-site-packages if you want to isolate your environment from the main site packages directory
virtualenv --no-site-packages ~/virtualenvironment/my_new_app
cd ~/virtualenvironment/my_new_app/bin
# activate your environment
source activate
# exit your virtualenv
deactivate
# install an app in your Virtualenv
pip install flask

# Deleting your virtual environment
rm -rf ~/virtualenvironment
============================================================================
# installing Django globally on the system.NOT DESIGNED FOR
sudo pip install django
# installing Django locally
pip install django
============================================================================
# Install Virtualenv
sudo apt-get install python-virtualenv # method1
sudo pip install virtualenv # method3
conda install virtualenv # method4
============================================================================
# activate your environment
source activate
# In the /bin directory there is an activate BASH script. 
./activate

# activate the environment
env/bin/pip
env/bin/python
source env/bin/activate

$ which python # globally 
/usr/bin/python
$ source env1/bin/activate
$ which python # locally on env1 virtual environment
/home/vagrant/myproject/env1/bin/python

 # use the versions of python and pip inside the environment
 env/bin/python
 env/bin/pip 
============================================================================

============================================================================
# Build wheels for a requirement (and all its dependencies), and then install
$ pip wheel --wheel-dir=/tmp/wheelhouse SomePackage
$ pip install --no-index --find-links=/tmp/wheelhouse SomePackage
============================================================================
# Compute the hash of a downloaded archive
pip download SomePackage
pip hash ./pip_downloads/SomePackage-2.2.tar.gz
============================================================================
# Each project you work on has its own requirements.txt file
# you can use this to install the dependencies for that project into its virtual environment
env/bin/pip install -r requirements.txt


pip freeze > requirements.txt
pip install -r requirements.txt
pip install -r example-requirements.txt

# Generate a requirements file and then install from it in another environment.
$ env1/bin/pip freeze > requirements.txt
$ env2/bin/pip install -r requirements.txt

# if pkg1 requires pkg3>=1.0 and pkg2 requires pkg3>=1.0,<=2.0, and if pkg1 is resolved first, pip will only use pkg3>=1.0, 
# and could easily end up installing a version of pkg3 that conflicts with the needs of pkg2
requirements.txt
pkg1
pkg2
pkg3>=1.0,<=2.0

# ProjectA in your requirements file requires ProjectB but the latest version (v1.3) has a bug
# you can force pip to accept earlier versions
requirements.txt
ProjectA
ProjectB<1.3
# suppose a dependency, SomeDependency from PyPI has a bug, and you can’t wait for an upstream fix.
# You could clone/copy the src, make the fix, and place it in VCS with the tag sometag
requirements.txt
git+https://myvcs.com/some_dependency@sometag#egg=SomeDependency

pip install -c constraints.txt

$ pip install SomePackage            # latest version
$ pip install SomePackage==1.0.4     # specific version
$ pip install 'SomePackage>=1.0.4'     # minimum version
docopt == 0.6.1             # Version Matching. Must be version 0.6.1
keyring >= 4.1.1            # Minimum version 4.1.1
coverage != 3.5             # Version Exclusion. Anything except version 3.5
Mopidy-Dirble ~= 1.1        # Compatible release. Same as >= 1.1, == 1.*

# Upgrade an already installed SomePackage to the latest from PyPI.
pip install --upgrade SomePackage
# Install a particular source archive file.
$ pip install ./downloads/SomePackage-1.0.4.tar.gz
$ pip install http://my.package.repo/SomePackage-1.0.4.zip
# Install from a different index, and not PyPI
pip install --index-url http://my.package.repo/simple/ SomePackage
# Install from a local flat directory containing archives (and don’t scan indexes)
$ pip install --no-index --find-links=file:///local/dir/ SomePackage
$ pip install --no-index --find-links=/local/dir/ SomePackage
$ pip install --no-index --find-links=relative/dir/ SomePackage
============================================================================
# install from local packages only, with no traffic to PyPI.
# download the archives that fulfill your requirements:
pip download --destination-directory DIR -r requirements.txt
# pip download --destination-directory DIR -r requirements.txt
# if some of your requirements don’t come as wheels from PyPI, and you want wheels
pip wheel --wheel-dir DIR -r requirements.txt
# to install from local only
pip install --no-index --find-links=DIR -r requirements.txt
============================================================================
virtualenv env
env/bin/pip install requests
env/bin/pip install flask
env/bin/pip freeze> requirements.txt
virtualenv env1
env1/bin/pip install -r requirements.txt
============================================================================
virtualenv --python=/usr/bin/python3.2 name_of_your_virtualenv
source activate name_of_your_virtualenv
python --version

virtualenv venv3 --python=`which python3`
virtualenv venv2 --python=`which python2`
venv3/bin/python --version
venv2/bin/python --version

virtualenv venv2 -p `which python2`
venv2/bin/python --version
Python 2.7.12
virtualenv venv3 -p `which python3`
venv3/bin/python --version
Python 3.5.2

virtualenv -p $(which python2) venvp2
venv2/bin/python --version
Python 2.7.12
virtualenv -p $(which python3) venvp3
venvp3/bin/python --version
Python 3.5.2

# call virtualenv with python version
python3 -m virtualenv -p $(which python3) venv3
venv3/bin/python --version
Python 3.5.2
python -m virtualenv -p $(which python2) venv2
venv2/bin/python --version
Python 2.7.12
python3 -m virtualenv -p $(which python2) venv1
venv1/bin/python --version
Python 2.7.12
python -m virtualenv -p $(which python3) venv5
venv5/bin/python --version
Python 3.5.2

# The venv module provides support for creating lightweight “virtual environments” with their own site directories
python3 -m venv virtualenv1
virtualenv1/bin/python --version
Python 3.5.2
============================================================================
virtualenvwrapper
# make sure virtualenv is already installed
# the virtualenvwrapper tool is just some wrapper scripts around the main virtualenv tool.

# Install pip
sudo apt install python-pip

# Install Virtualenv
sudo pip install virtualenv # method3
virtualenv --version

# Install virtualenvwrapper
pip install virtualenvwrapper

which virtualenvwrapper.sh
/home/vagrant/.local/bin/virtualenvwrapper.sh

# Bash shell, either the ~/.bashrc file or the ~/.profile
cat >> ~/.bashrc << EOF
> export WORKON_HOME=$HOME/.virtualenvs   # Optional
> export PROJECT_HOME=$HOME/projects      # Optional
> source /home/vagrant/.local/bin/virtualenvwrapper.sh
> EOF

source ~/.bashrc

# Create a virtual environment
mkvirtualenv my_project
# Work on a virtual environment
workon my_project
# deactivate
deactivate
# delete
rmvirtualenv venv
# List all of the environments
lsvirtualenv
# Navigate into the directory of the currently activated virtual environment, so you can browse its site-packages
cdvirtualenv
# Shows contents of site-packages directory
lssitepackages
============================================================================
multiple ansible environments

sudo pip install virtualenv
sudo pip install virtualenvwrapper

cat >> ~/.profile << EOF
export WORKON_HOME=$HOME/.virtualenvs   # Optional
source /usr/local/bin/virtualenvwrapper.sh
EOF

mkvirtualenv ansible-latest
pip install ansible

mkvirtualenv ansible-2.7
pip install ansible==2.7

============================================================================
vagrant@remotecontrol01:~$ hostnamectl
   Static hostname: remotecontrol01
         Icon name: computer-vm
           Chassis: vm
        Machine ID: 596011e352744fafa2713e957add0deb
           Boot ID: 8c8d71d061ad4eb2b55b2c85881e030f
    Virtualization: oracle
  Operating System: Ubuntu 19.04
            Kernel: Linux 5.0.0-17-generic
      Architecture: x86-64

vagrant@remotecontrol01:~$ sudo apt install python-pip -y
vagrant@remotecontrol01:~$ sudo pip install virtualenv
vagrant@remotecontrol01:~$ sudo pip install virtualenvwrapper
vagrant@remotecontrol01:~$ python2 --version
Python 2.7.16
vagrant@remotecontrol01:~$ python3 --version
Python 3.7.3

vagrant@remotecontrol01:~$ virtualenv -p /usr/bin/python2.7 ~venv27
Running virtualenv with interpreter /usr/bin/python2.7
Already using interpreter /usr/bin/python2.7
New python executable in /home/vagrant/~venv27/bin/python2.7
Also creating executable in /home/vagrant/~venv27/bin/python
Installing setuptools, pip, wheel...
done.

vagrant@remotecontrol01:~$ virtualenv -p /usr/bin/python3.7 ~venv37
Running virtualenv with interpreter /usr/bin/python3.7
Already using interpreter /usr/bin/python3.7
Using base prefix '/usr'
New python executable in /home/vagrant/~venv37/bin/python3.7
Also creating executable in /home/vagrant/~venv37/bin/python
Installing setuptools, pip, wheel...
done.
vagrant@remotecontrol01:~$ sudo apt-get install python3-distutils -y

cat >> ~/.profile << EOF
export WORKON_HOME=$HOME/.virtualenvs   # Optional
source /usr/local/bin/virtualenvwrapper.sh
EOF
vagrant@remotecontrol01:~$ source .profile
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/premkproject
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/postmkproject
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/initialize
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/premkvirtualenv
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/postmkvirtualenv
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/prermvirtualenv
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/postrmvirtualenv
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/predeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/postdeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/preactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/postactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/get_env_details

vagrant@remotecontrol01:~$ python3 --version
Python 3.7.3
vagrant@remotecontrol01:~$ which python3
/usr/bin/python3

vagrant@remotecontrol01:~$ mkvirtualenv -p /usr/bin/python3 venv373
Running virtualenv with interpreter /usr/bin/python3
Already using interpreter /usr/bin/python3
Using base prefix '/usr'
New python executable in /home/vagrant/.virtualenvs/venv373/bin/python3
Also creating executable in /home/vagrant/.virtualenvs/venv373/bin/python
Installing setuptools, pip, wheel...
done.
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv373/bin/predeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv373/bin/postdeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv373/bin/preactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv373/bin/postactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv373/bin/get_env_details
(venv373) vagrant@remotecontrol01:~$ ls -lai .virtualenvs/venv373/
total 16
3677748 drwxrwxr-x 4 vagrant vagrant 4096 Aug 29 13:58 .
3674757 drwxrwxr-x 5 vagrant vagrant 4096 Aug 29 13:58 ..
3677805 drwxrwxr-x 2 vagrant vagrant 4096 Aug 29 13:58 bin
3677749 drwxrwxr-x 3 vagrant vagrant 4096 Aug 29 13:58 lib
(venv373) vagrant@remotecontrol01:~$ ls -lai .virtualenvs/
total 68
3674757 drwxrwxr-x  5 vagrant vagrant 4096 Aug 29 13:58 .
3670052 drwxr-xr-x 10 vagrant vagrant 4096 Aug 29 13:43 ..
3674926 -rwxr-xr-x  1 vagrant vagrant  135 Aug 29 13:43 get_env_details
3674886 -rw-r--r--  1 vagrant vagrant   96 Aug 29 13:43 initialize
3674924 -rw-r--r--  1 vagrant vagrant   73 Aug 29 13:43 postactivate
3674903 -rw-r--r--  1 vagrant vagrant   75 Aug 29 13:43 postdeactivate
3674885 -rwxr-xr-x  1 vagrant vagrant   66 Aug 29 13:43 postmkproject
3674888 -rw-r--r--  1 vagrant vagrant   73 Aug 29 13:43 postmkvirtualenv
3674898 -rwxr-xr-x  1 vagrant vagrant  110 Aug 29 13:43 postrmvirtualenv
3674908 -rwxr-xr-x  1 vagrant vagrant   99 Aug 29 13:43 preactivate
3674902 -rw-r--r--  1 vagrant vagrant   76 Aug 29 13:43 predeactivate
3674877 -rwxr-xr-x  1 vagrant vagrant   91 Aug 29 13:43 premkproject
3674887 -rwxr-xr-x  1 vagrant vagrant  130 Aug 29 13:43 premkvirtualenv
3674895 -rwxr-xr-x  1 vagrant vagrant  111 Aug 29 13:43 prermvirtualenv
3674927 drwxrwxr-x  6 vagrant vagrant 4096 Aug 29 13:57 test1
3676723 drwxrwxr-x  6 vagrant vagrant 4096 Aug 29 13:57 test2
3677748 drwxrwxr-x  4 vagrant vagrant 4096 Aug 29 13:58 venv373
(venv373) vagrant@remotecontrol01:~$ deactivate
vagrant@remotecontrol01:~$ cd ~

vagrant@remotecontrol01:~$ which python2
/usr/bin/python2
vagrant@remotecontrol01:~$ python2 --version
Python 2.7.16

vagrant@remotecontrol01:~$ mkvirtualenv -p /usr/bin/python2 venv2716
Running virtualenv with interpreter /usr/bin/python2
Already using interpreter /usr/bin/python2
New python executable in /home/vagrant/.virtualenvs/venv2716/bin/python2
Also creating executable in /home/vagrant/.virtualenvs/venv2716/bin/python
Installing setuptools, pip, wheel...
done.
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv2716/bin/predeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv2716/bin/postdeactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv2716/bin/preactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv2716/bin/postactivate
virtualenvwrapper.user_scripts creating /home/vagrant/.virtualenvs/venv2716/bin/get_env_details
(venv2716) vagrant@remotecontrol01:~$ deactivate
vagrant@remotecontrol01:~$



============================================================================

pip uninstall SomePackage
pip show sphinx
# list installed packages
pip list
# list outdated packages
pip list --outdated
# pip can search PyPI for packages
pip search "query"
# pip comes with support for command line completion in bash, zsh and fish.
pip completion --bash >> ~/.profile
pip completion --zsh >> ~/.zprofile
pip completion --fish > ~/.config/fish/completions/pip.fish

# you can use the result of the completion command directly with the eval function of your shel l
# e.g. by adding the following to your startup file
eval "`pip completion --bash`"

============================================================================
vagrant@vgclient01:~/.virtualenvs/k8sbox1$ sudo docker -v
sudo: docker: command not found

vagrant@vgclient01:~/.virtualenvs/k8sbox1$ workon k8sbox1
(k8sbox1) vagrant@vgclient01:~/.virtualenvs/k8sbox1$ pwd
/home/vagrant/.virtualenvs/k8sbox1
(k8sbox1) vagrant@vgclient01:~/.virtualenvs/k8sbox1$
(k8sbox1) vagrant@vgclient01:~/.virtualenvs/k8sbox1$ sudo bash /vagrant/k8snodes.sh
(k8sbox1) vagrant@vgclient01:~/.virtualenvs/k8sbox1$ docker -v
Docker version 18.06.2-ce, build 6d37f41
============================================================================
"pip install -e ."
installs site-packages/PackageName.egg-link file
adds path to site-packages/easy-install.pth
optionally installs CLI targets in <venv>/bin
how setuptools dependencies are handled via pip

install the dependencies
*[dev] is the name of the requirements group from setup.py
git clone URL
cd project
"pip install -e ." OR "pip install -e .[dev]*"

============================================================================
#pycharm scrapy install
File - Setting - Project: your_project_name -  Project Interpreter -  “+” - Type there scrapy - Install Package

Pycharm Terminal - pip3 install Scrapy (For python 3.xx)
Pycharm Terminal - pip install Scrapy (For python 3.xx)
scrapy --version
============================================================================
$ hostnamectl
  Operating System: CentOS Linux 8
       CPE OS Name: cpe:/o:centos:centos:8
            Kernel: Linux 4.18.0-240.1.1.el8_3.x86_64
      Architecture: x86-64

#install python 3x
yum install python3
python3 -V
pip3 --version

pip3 install --user virtualenv
virtualenv --version

#create python3 virtual environment
virtualenv venv3 --python=`which python3`
cd venv3/bin/
$ source activate
$ python -V
Python 3.6.8
$ python3 -V
Python 3.6.8
$ python2 -V
Python 2.7.18
$ pip --version
pip 21.3.1 from /home/vagrant/venv3/lib/python3.6/site-packages/pip (python 3.6)
$ pip3 --version
pip 21.3.1 from /home/vagrant/venv3/lib/python3.6/site-packages/pip (python 3.6)
$ pip2 --version
pip 9.0.3 from /usr/lib/python2.7/site-packages (python 2.7)
$ deactivate

#install python 2x
yum install python2
python2 -V

#create python2 virtual environment
cd venv2/bin
source activate
$ python -V
Python 2.7.18
$ python3 -V
Python 3.6.8
$ python2 -V
Python 2.7.18
$ pip --version
pip 20.3.4 from /home/vagrant/venv2/lib/python2.7/site-packages/pip (python 2.7)
$ pip3 --version
pip 21.3.1 from /home/vagrant/venv3/lib/python3.6/site-packages/pip (python 3.6)
$ pip2 --version
pip 9.0.3 from /usr/lib/python2.7/site-packages (python 2.7)
$ deactivate

============================================================================
$ hostnamectl
  Operating System: CentOS Linux 8
       CPE OS Name: cpe:/o:centos:centos:8
            Kernel: Linux 4.18.0-240.1.1.el8_3.x86_64
      Architecture: x86-64
      
yum install python2
pip2 --version

pip install virtualenv
============================================================================
