------------------------------------------------------------------------------------------
python3 -V
python2 -V
------------------------------------------------------------------------------------------
#Command-line one-liners
# -c run Python script sent in as cmd string

python -c "print(3.0/2)" 
python -c "import math;print(math.sin(1))" 
python -c "for i in range(1,5):print(i)"
python -c "for r in range(3): print 'test' "

python -c "x =1 ; y =4 ; print(x,y) ; x,y = y,x ; print(x,y)" #Swap Variables
python -c "x,y,z =1,4,7;  print(x,y,z) ; x,y,z = z,y,x ; print(x,y,z)" #Swap Variables

python -c "txt='She said \"Never let go\"' ; print(txt) " #Backslashes (\) are used to escape characters in a Python string.

python -c "game='Popular Nintendo Game Mario Kart'; print('l' in game)" #determine if a letter or a substring exists in a string
True
python -c "game='Popular Nintendo Game Mario Kart'; print(game[0]);print(game[1]);print(game[2])"

python -c "for i in range(1,11):for j in range(1,11): print(i,j)"  #Does not work; two loops in a line are an invalid syntax.
python -c "for i, j in ((i,j) for i in range (1,11) for j in range(1,11)): print(i, j)"

#Convert a CSV to JSON
python3 -c \
"import csv,json,sys;print(json.dumps(list(csv.reader(open(sys.argv[1])))))" \
covid19-vaccinations-town-age-grp.csv
------------------------------------------------------------------------------------------
#Setting path at Unix/Linux

$ ls -l /usr/bin/python3
lrwxrwxrwx 1 root root 10 Mar 25 12:41 /usr/bin/python3 -> python3.10

export PATH="$PATH:/usr/local/bin/python"

PYTHONPATH
tells the Python interpreter where to locate the module files imported into a program
PYTHONSTARTUP
named as .pythonrc.py 
contains commands that load utilities or modify PYTHONPATH.
PYTHONCASEOK
used in Windows to instruct Python to find the first case-insensitive match in an import statement.
PYTHONHOME
alternative module search path
------------------------------------------------------------------------------------------
#Setting path at Windows

#C:\Python is the path of the Python directory
path %path%;C:\Python
------------------------------------------------------------------------------------------
#Interactive Mode Programming

$ python3
Python 3.10.4 (main, Jun 29 2022, 12:14:53) [GCC 11.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>

------------------------------------------------------------------------------------------
#Script Mode Programming

$ cat scripty.py
#!/usr/bin/python

print ("Hello, Python!")
$ python3 scripty.py
Hello, Python!
------------------------------------------------------------------------------------------
#Multi-Line Statements

total = item_one + \
        item_two + \
        item_three

days = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday']
------------------------------------------------------------------------------------------       
$ echo "22.67892" | python3 -c "print(f'{round(float(input()))}')" #Round floats in Bash with Python's help
------------------------------------------------------------------------------------------       
#single ('), double (") and triple (''' or """) quotes to denote string literals

word = 'word'
sentence = "This is a sentence."
paragraph = """This is a paragraph. It is
made up of multiple lines and sentences.""" 
------------------------------------------------------------------------------------------
#Multiple Statements on a Single Line

import sys; x = 'foo'; sys.stdout.write(x + '\n')
------------------------------------------------------------------------------------------
#Assigning Values to Variables
counter = 100          # An integer assignment
miles   = 1000.0       # A floating point
name    = "John"       # A string
------------------------------------------------------------------------------------------
#Multiple Assignment
a = b = c = 1
------------------------------------------------------------------------------------------
#comments

# First comment
print "Hello, Python!" # second comment


------------------------------------------------------------------------------------------
#Strings
str = 'Hello World!'

print(str)          # Prints complete string
print(str[0])       # Prints first character of the string
print(str[2:5])     # Prints characters starting from 3rd to 5th
print(str[2:])      # Prints string starting from 3rd character
print(str * 2)      # Prints string two times
print (str + "TEST") # Prints concatenated string

#TypeError: 'str' object does not support item assignment
str[2]="a" #update string
print(str)

------------------------------------------------------------------------------------------
#Lists,elements and size can be changed

list = [ 'abcd', 786 , 2.23, 'john', 70.2 ]
tinylist = [123, 'john']

print (list)          # Prints complete list
print (list[0])       # Prints first element of the list
print (list[1:3])     # Prints elements starting from 2nd till 3rd
print (list[2:])      # Prints elements starting from 3rd element
print (tinylist * 2)  # Prints list two times
print (list + tinylist) # Prints concatenated lists

print(list)
list[2] = "3" #update the list
print(list)

------------------------------------------------------------------------------------------
# Tuples, read-only lists,cannot be updated

tuple = ( 'abcd', 786 , 2.23, 'john', 70.2  )
tinytuple = (123, 'john')

print tuple               # Prints the complete tuple
print tuple[0]            # Prints first element of the tuple
print tuple[1:3]          # Prints elements of the tuple starting from 2nd till 3rd 
print tuple[2:]           # Prints elements of the tuple starting from 3rd element
print tinytuple * 2       # Prints the contents of the tuple twice
print tuple + tinytuple   # Prints concatenated tuples
------------------------------------------------------------------------------------------
#Dictionary,key-value pairs.
 
 dict = {}
dict['one'] = "This is one"
dict[2]     = "This is two"
dict[3]     = 3

tinydict = {'name': 'john','code':6734, 'dept': 'sales'}

print(dict['one'])
print(dict[3])

print(dict.keys())
print(dict.values())
print(dict)
------------------------------------------------------------------------------------------
#type conversion

int("0x12F", base=16) #passing a hexadecimal string and expecting a decimal integer.

str(5) # convert a Python int to a string using str()
type(str(6))
------------------------------------------------------------------------------------------
#concatenate string and integer

s = 'Year is '
y = 2018;

print("%s%s" % (s, y)) 
print("{}{}".format(s, y))
print(f'{s}{y}')

#join a and b using a null string separator (sep), since the default separator for print() is a space (” “).
a = "Hello, I am in grade "
b = 12
print(a, b, sep="")

#String containing arithmetic expression
>>> x=eval('3+4')
>>> type(x)
<class 'int'>
>>> x
7

>>> x = eval('list((a*2 for a in range(5)))')
>>> x
[0, 2, 4, 6, 8]
>>> type(x)
<class 'list'>
------------------------------------------------------------------------------------------
# input by the user, nested if
answer = input("What is your age? ")

if int(answer) >= 18:
    answer = input("What country do you live in? ")
    if answer == "canada":
        print("Me as well!")
    else:
        print("Oh, I do not live there.")

food = input("What is your favorite food? ")
drink = input("What is your favorite drink? ")

if food == "pizza" and drink == "juice":
    print("Those are my favorite as well!")
else:
    print("One of those is not my favorite")
------------------------------------------------------------------------------------------    
#List comprehensions

lst1 = [1, 2, 3]
lst2 = [3, 4, 5]
print([x * y for x in lst1 for y in lst2]) #[3, 4, 5, 6, 8, 10, 9, 12, 15]

any([i % 3 for i in [3, 3, 4, 4, 3]]) #4 % 3 = 1, and 1 is true, so any()  returns True.

sum(1 for i in [3, 3, 4, 4, 3] if i == 4) #how many items a condition is true
------------------------------------------------------------------------------------------
mytuple = (0, 1, False) # Returns True because the second item is True
x = any(mytuple)
print(x)

myset = {0, 1, 0} ## Returns True because the second item is True
x = any(myset)
print(x)

mydict = {0 : "Apple", 1 : "Orange"} # For dictionaries the any() function checks the keys, not the values.
x = any(mydict) # Returns True because the second key is True.
print(x)
-----------------------------------------------------------------------------------------
#multi-line statements in the one-line command-line

echo -e "import sys\nfor r in range(10): print 'rob'" | python

python -c "exec(\"import sys\nfor r in range(10): print 'rob'\")"

(echo "import sys" ; echo "for r in range(10): print 'rob'") | python

python - <<EOF
import random
for r in range(3): print(random.randint(1, 42))
EOF

python -c "import sys; map(lambda x: sys.stdout.write('rob%d\n' % x), range(10))"
------------------------------------------------------------------------------------------
#Python wrapper for ls command, run shell command in Python
#!/usr/bin/env python
#A System Information Gathering Script
import subprocess
        
#Command 1
uname = “uname”
uname_arg = “-a”
print "Gathering system information with %s command:\n" % uname
subprocess.call([uname, uname_arg])
        
#Command 2
diskspace = "df"
diskspace_arg = "-h"
print "Gathering diskspace information %s command:\n" % diskspace
subprocess.call([diskspace, diskspace_arg])
------------------------------------------------------------------------------------------
#Python wrapper for ls command, run shell command in Python
$ cat ls.py
#!/usr/bin/env python
#Python wrapper for the ls command

import subprocess

subprocess.call(["ls","-l"])
------------------------------------------------------------------------------------------
# list locked users
$ cat locked_user.py
#! /usr/bin/python3

import os
import stat
import sys

def get_homes_and_uids_for_users_with_shells():
    users = {}
    with open("/etc/passwd", "rt") as pf:
        for line in pf:
            login, x, uid, gid, gecos, home, shell = line.split(':')
            if x != 'x':
                sys.stderr.write("*** Account '{!r}' not properly shadowed\n"
                                 .format(login))
            if shell not in ('/bin/false', '/usr/bin/false',
                             '/sbin/nologin', '/usr/sbin/nologin'):
                users[login] = (int(uid), home)
    return users

def check_ssh_auth_perms(path, owner):
    owners = (0, owner)
    badwritebits = stat.S_IWGRP | stat.S_IWOTH # 0022
    # FIXME: I'm not sure whether sshd allows symlinks at any point in this
    # path.  Conservatively assume it does.
    # FIXME: Doesn't check for ACLs.
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return False
    if (st.st_size == 0 or st.st_uid not in owners
        or not stat.S_ISREG(st.st_mode)
        or stat.S_IMODE(st.st_mode) & badwritebits):
        return False
    while True:
        path = os.path.dirname(path)
        # Not necessary to check for ENOENT; if we got here at all,
        # the entire chain of parent dirs must exist
        st = os.stat(path)
        if (st.st_uid not in owners
            or not stat.S_ISDIR(st.st_mode)
            or stat.S_IMODE(st.st_mode) & badwritebits):
            return False
        if path == '/': break
    return True

def get_users_with_ssh_keys(all_users):
    ssh_users = set()
    already_processed_homes = {}
    for login, (uid, home) in all_users.items():
        if home in already_processed_homes:
            if already_processed_homes[home]:
                ssh_users.add(login)
            continue
        if (check_ssh_auth_perms(home + "/.ssh/authorized_keys", uid)
            or check_ssh_auth_perms(home + "/.ssh/authorized_keys2", uid)):
            already_processed_homes[home] = True
            ssh_users.add(login)
        else:
            already_processed_homes[home] = False
    return ssh_users

def get_users_with_possible_passwords():
    pw_users = set()
    with open("/etc/shadow", "rt") as sf:
        for line in sf:
            login, phash, chg, mina, maxa, warn, inact, expir, res \
                = line.split(':')
            if not phash:
                sys.stderr.write("*** Account '{!r}' has blank password\n"
                                 .format(login))
            if phash[0] != '*' and phash[0] != '!':
                pw_users.add(login)
    return pw_users

def main():
    users = get_homes_and_uids_for_users_with_shells()
    ssh_users = get_users_with_ssh_keys(users)
    pw_users = get_users_with_possible_passwords()

    active_users = set(users.keys()) & (ssh_users | pw_users)
    for u in sorted(active_users):
        sys.stdout.write(u + "\n")

main()
vagrant@vg-ubuntu-01:~$
------------------------------------------------------------------------------------------
$ cat a.py
#!/usr/bin/env python

for a in [1, 2]:
    for b in ['a', 'b']:
        print (a, b)
$ python3 a.py
------------------------------------------------------------------------------------------
#check whether a certain file path is a directory
#!/usr/bin/env python

import os

if os.path.isdir("/tmp"):
    print "/tmp is a directory"
else:
    print "/tmp is not a directory"
------------------------------------------------------------------------------------------
#calculate_size.py
#python3 /path/to/calculate_size.py </path/to/your/textfile/with/a/filelist>
#sudo python3 /path/to/calculate_size.py </path/to/your/textfile/with/a/filelist>

#!/usr/bin/env python3
import os
import subprocess
import sys

f_list = sys.argv[1]
get = lambda x: subprocess.check_output(["/bin/bash", "-c", x]).decode("utf-8")

with open(f_list) as src:
    files = [f.strip() for f in src.readlines()]

total_size = []
for f in files:
    size = get('du -hk "'+f+'"').split()[0]; total_size.append(int(size))
    print(f.strip('"')+"\t", size+" k")
print("-"*30, "\nnumber of files: "+str(len(total_size)), "\ntotal size: "+str(sum(total_size))+" k")
try:
    print("average size: "+str(int(sum(total_size)/len(total_size)))+" k\n\n")
except ZeroDivisionError:
    pass

proceed = input("Should I delete the listed files? \n(press return to proceed, x + return to cancel): ")
if proceed == "":
    for file in files:
        os.remove(file)
------------------------------------------------------------------------------------------
#Extract IP address from file; reoccuring, common, repeating IP address

#log
Feb  3 13:34:05 j4-be02 sshd[676]: Failed password for root from 85.17.188.70 port 48495 ssh2
Feb  3 21:45:18 j4-be02 sshd[746]: Failed password for invalid user test from 62.45.87.113 port 50636 ssh2
Feb  4 08:39:46 j4-be02 sshd[1078]: Failed password for root from 1.234.51.243 port 60740 ssh2
Feb  5 08:39:46 j4-be02 sshd[1078]: Failed password for root from 1.234.51.243 port 60740 ssh2
Feb  5 08:45:46 j4-be02 sshd[1078]: Failed password for root from 1.234.51.243 port 60740 ssh2

def attackers_count(): #how many attacks occur per hour per day
   from itertools import groupby
    #open the auth.log for reading
   myAuthlog=open('logs/ip.log5', 'r')

   # looks for 'Failed password for'
   myAuthlog = (line for line in myAuthlog if "Failed password for" in line)
   # Groups all the times and dates together
   for key, group in groupby(myAuthlog, key = lambda x: x[:9]):
       month, day, hour = key[0:3], key[4:6], key[7:9]
       # prints the results out in a format to understand e.g date, time then amount of attacks
       print( "On%s-%s at %s:00 There was %d attacks"%(day, month, hour, len(list(group))) )
       
def attackers_count_by_IP(): #how many attacks occur per hour per day per IP
   from itertools import groupby
   import re
   myAuthlog = open('logs/ip.log5', 'r')
   myAuthlog = (line for line in myAuthlog if "Failed password for" in line)
   for key, group in groupby(myAuthlog, key=lambda x: x[:9] + re.search('from(.+?) port', x).group(1)):
      month, day, hour, ip = key[0:3], key[4:6], key[7:9], key[10:]
      print( "On%s-%s at %s:00 There was %d attacks FROM IP %s" % (day, month, hour, len(list(group)), ip) )
------------------------------------------------------------------------------------------
#Extract IP address from file; reoccuring, common, repeating IP address

#log
USER_ID,IP_ADDRESS
XXXXXX24,10.12.6.54
XXXXXX24,10.12.6.54
XXXXXX24,10.12.6.54
XXXXXX24,10.12.6.54
XXXXXX24,10.12.6.54
XXXXXX25,10.12.6.55
XXXXXX25,10.12.6.55
XXXXXX25,10.12.6.55
XXXXXX25,10.12.6.55
XXXXXX25,10.12.6.55
XXXXXX21,10.12.6.51
XXXXXX21,10.12.6.51
XXXXXX21,10.12.6.51
XXXXXX21,10.12.6.51

import collections

import pandas as pd
from tabulate import tabulate

with open("data_file.csv") as file:
    next(file, None)  # skip the header
    counter = collections.Counter([line.strip() for line in file])

output = collections.defaultdict(dict)
for user_and_ip, ip_to_user_count in counter.items():
    user, ip = user_and_ip.split(",")
    output[ip].update({user: ip_to_user_count})

df = pd.DataFrame(output).fillna("")
print(tabulate(df, headers="keys"))
df.to_csv("user_to_ip.csv")

# or

import csv
import collections
from collections import Counter

datafile=open('conn.csv','r')
usefuldata=[]
for line in datafile:
   usefuldata.append(line)
outfile1=Counter(usefuldata)
for value,count in outfile1.most_common():
  print(value,count)
------------------------------------------------------------------------------------------
#Extract IP address from file; reoccuring, common, repeating IP address

#log
1;Jan 10, 2003 04:34:12.870401000 EST;65.240.185.205;2335;131.243.2.12;21;6;48;TCP;2335

2;Jan 10, 2003 04:34:12.870741000 EST;131.243.2.12;21;65.240.185.205;2335;6;48;TCP;21

3;Jan 10, 2003 04:34:13.050626000 EST;65.240.185.205;2335;131.243.2.12;21;6;40;TCP;2335

4;Jan 10, 2003 04:34:13.274193000 EST;131.243.2.12;21;65.240.185.205;2335;6;123;FTP;Response

5;Jan 10, 2003 04:34:13.455582000 EST;65.240.185.205;2335;131.243.2.12;21;6;56;FTP;Request

from collections import Counter

def getIP(line):
  parts = line.split(";")
  if len(parts) == 10:
    return parts[2]

with open("/path/to/log", "r") as f:
  ips = Counter(getIP(line) for line in f)

------------------------------------------------------------------------------------------
#Extract IP address from file

#log
"No.","Time","Source","Destination","Protocol","Info"
"1","0.000000","120.107.103.180","172.16.112.50","TELNET","Telnet Data ..." 
"2","0.000426","172.16.112.50","172.16.113.168","TELNET","Telnet Data ..." 
"3","0.019849","172.16.113.168","172.16.112.50","TCP","21582 > telnet [ACK]" 
"4","0.530125","172.16.113.168","172.16.112.50","TELNET","Telnet Data ..." 
"5","0.530634","172.16.112.50","172.16.113.168","TELNET","Telnet Data ..."


import csv
from collections import defaultdict

# A dictionary whose values are by default (a
# dictionary whose values are by default 0)
bySource = defaultdict(lambda: defaultdict(lambda: 0))

with open('logfile.txt') as logfile:
     for row in csv.DictReader(logfile):
         bySource[row["Source"]][row["Protocol"]] += 1

for source, protocols in bySource.iteritems():
    protocols['Total'] = sum(protocols.values())

    print "From IP %s Protocol Count: %s" % (
        source,
        ' '.join("(%s: %d)" % item for item in protocols.iteritems())
    )
------------------------------------------------------------------------------------------
#Extract IP address from file

import re
  
# opening and reading the file
with open('test2.txt') as fh:
  string = fh.readlines()
    
# declaring the regex pattern for IP addresses 
pattern =re.compile('''((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)
{3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)''')
  
# initializing the list objects
valid =[]
invalid=[]
  
# extracting the IP addresses
for line in string:
    line = line.rstrip()
    result = pattern.search(line)
  
    # valid IP addresses
    if result:
      valid.append(line)
  
    # invalid IP addresses  
    else:
      invalid.append(line)
  
# displaying the IP addresses
print("Valid IPs")
print(valid)
print("Invalid IPs")
print(invalid)
------------------------------------------------------------------------------------------
#Extract IP address from file

# importing the module
import re
  
# opening and reading the file 
with open('a.txt') as fh:
   fstring = fh.readlines()
  
# declaring the regex pattern for IP addresses
pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
  
# initializing the list object
lst=[]
  
# extracting the IP addresses
for line in fstring:
   lst.append(pattern.search(line)[0])
  
# displaying the extracted IP addresses
print(lst)

------------------------------------------------------------------------------------------
#check IP address

#!/usr/bin/env python
import ipaddress


def validIP(IP_ADDRESS):
    try:
        ipadr = ipaddress.ip_address(IP_ADDRESS)
        print(IP_ADDRESS + ' valid IP address')
    except ValueError:
        # print(ipadr + ' invalid ip address')
        print(IP_ADDRESS + ' invalid ip address')
------------------------------------------------------------------------------------------
#check IP address

def validIP_parse(IP_ADDRESS):
        octets = IP_ADDRESS.split(".")
        if len(octets) != 4:
            msg = IP_ADDRESS + " does not have 4 octets"
            print(msg)
            return

        for i in octets:
            try:
                if not isinstance(int(i), int):
                    print(" IP_ADDRESS + ' invalid ip address' ")
            except ValueError:
                    print(IP_ADDRESS + ' has non integer value ')
                    return

        for i in octets:
            if not ( 0<= int(i) <=255 ):
                 print(IP_ADDRESS + ' octet has value out of range')
                 return

        print(IP_ADDRESS + ' valid ip address')
        return
------------------------------------------------------------------------------------------
$cat file1.txt
qwer hy
asdf uj
zxcv ui
1234 op
aa bb
$cat file2.txt
0987 aa
5678 bb
uiop cc
qwer tt
zxcv vv
aa bb
$ cat common_linux_files.py
#!/usr/bin/env python

file1 = set( line.strip() for line in open("file1.txt") )
file2 = set( line.strip() for line in open("file2.txt") )

for line in file1 & file2:
    if line:
        print(line)
------------------------------------------------------------------------------------------
# words of a file

l = []
f = open("filename.txt", "rU")
for line in f:
    for word in line.split()
        l.append(word)
        
------------------------------------------------------------------------------------------
# words of a file
def word_gen(file):
    for line in file:
        for word in line.split():
            yield word

with open('somefile') as f:
    word_gen(f)
------------------------------------------------------------------------------------------
# words of a file

words = open('myfile').read().split()
------------------------------------------------------------------------------------------
# words of a file

f = file("your-filename-here").read()
for word in f.split():
    # do something with word
    print(word)
------------------------------------------------------------------------------------------
# words of a file

line = ''
while True:
    word, space, line = line.partition(' ')
    if space:
        # A word was found
        yield word
    else:
        # A word was not found; read a chunk of data from file
        next_chunk = input_file.read(1000)
        if next_chunk:
            # Add the chunk to our line
            line = word + next_chunk
        else:
            # No more data; yield the last word and return
            yield word.rstrip('\n')
            return
------------------------------------------------------------------------------------------
#compare files

# Open File in Read Mode
file_1 = open('file1.txt', 'r')
file_2 = open('file2.txt', 'r')

print("Comparing files ", " @ " + 'file1.txt', " # " + 'file2.txt', sep='\n')

file_1_line = file_1.readline()
file_2_line = file_2.readline()

# Use as a COunter
line_no = 1

print()

with open('file1.txt') as file1:
	with open('file2.txt') as file2:
		same = set(file1).intersection(file2)

print("Common Lines in Both Files")

for line in same:
	print(line, end='')

print('\n')
print("Difference Lines in Both Files")
while file_1_line != '' or file_2_line != '':

	# Removing whitespaces
	file_1_line = file_1_line.rstrip()
	file_2_line = file_2_line.rstrip()

	# Compare the lines from both file
	if file_1_line != file_2_line:
	
		# otherwise output the line on file1 and use @ sign
		if file_1_line == '':
			print("@", "Line-%d" % line_no, file_1_line)
		else:
			print("@-", "Line-%d" % line_no, file_1_line)
			
		# otherwise output the line on file2 and use # sign
		if file_2_line == '':
			print("#", "Line-%d" % line_no, file_2_line)
		else:
			print("#+", "Line-%d" % line_no, file_2_line)

		# Print a empty line
		print()

	# Read the next line from the file
	file_1_line = file_1.readline()
	file_2_line = file_2.readline()

	line_no += 1

file_1.close()
file_2.close()

------------------------------------------------------------------------------------------
#compare files

from difflib import Differ
 
with open('file1.txt') as file_1, open('file2.txt') as file_2:
    differ = Differ()
 
    for line in differ.compare(file_1.readlines(), file_2.readlines()):
        print(line)
        
        
------------------------------------------------------------------------------------------
#compare files

import difflib
 
with open('file1.txt') as file_1:
    file_1_text = file_1.readlines()
 
with open('file2.txt') as file_2:
    file_2_text = file_2.readlines()
 
# Find and print the diff:
for line in difflib.unified_diff(
        file_1_text, file_2_text, fromfile='file1.txt',
        tofile='file2.txt', lineterm=''):
    print(line)
    

------------------------------------------------------------------------------------------
$ cat compare_files.py
#!/usr/bin/env python

import filecmp

file1 = "file1.txt"
file2 = "file2.txt"

result = filecmp.cmp(file1,file2)
print(result)

deep_result = filecmp.cmp(file1,file2,shallow=False)
print(deep_result)

if result == False:
    print(file1, " is different from ", file2)
else:
    print(file1, " and ", file2, " are same")
------------------------------------------------------------------------------------------
#Compare Two Dictionaries

def compare_dicts(dictionary1,dictionary2):
        common_pairs = dict()
        for key in dictionary1:
            if (key in dictionary2 and dictionary1[key] == dictionary2[key]):
                common_pairs[key] = dictionary1[key]
        print(common_pairs)
------------------------------------------------------------------------------------------
#Compare Two Dictionaries

def Dicts_Not_Equal(first,second):
    """ return True if both do not have same length or if any keys and values are not the same """
    if len(first) == len(second): 
        for k in first:
            if first.get(k) != second.get(k,k) or k not in second: return (True)
        for k in second:         
            if first.get(k,k) != second.get(k) or k not in first: return (True)
        return (False)   
    return (True)
------------------------------------------------------------------------------------------
#Compare Two Dictionaries

def compare_dicts(x,y):
    if json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True):
        print(' both equal')
    else:
        print (' not equal')
------------------------------------------------------------------------------------------
#Compare Two Dictionaries

def equal(a, b):
    type_a = type(a)
    type_b = type(b)
    
    if type_a != type_b:
        return False
    
    if isinstance(a, dict):
        if len(a) != len(b):
            return False
        for key in a:
            if key not in b:
                return False
            if not equal(a[key], b[key]):
                return False
        return True

    elif isinstance(a, list):
        if len(a) != len(b):
            return False
        while len(a):
            x = a.pop()
            index = indexof(x, b)
            if index == -1:
                return False
            del b[index]
        return True
        
    else:
        return a == b

def indexof(x, a):
    for i in range(len(a)):
        if equal(x, a[i]):
            return i
    return -1

------------------------------------------------------------------------------------------
#Compare Two Dictionaries

def dicts_equal(d1,d2):
    """ return True if all keys and values are the same """
    return all(k in d2 and d1[k] == d2[k]
               for k in d1) \
        and all(k in d1 and d1[k] == d2[k]
               for k in d2)
               
------------------------------------------------------------------------------------------
#Compare Two Dictionaries

shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
print(len(shared_items))

------------------------------------------------------------------------------------------
#Compare Two Dictionaries
dict1 = {'Name': 'asif', 'Age': 5}
dict2 = {'Name': 'lalita', 'Age': 78}
  
if dict1 == dict2:
    print "dict1 is equal to dict2"
else:
    print "dict1 is not equal to dict2"
------------------------------------------------------------------------------------------
#difference between two time stamps in minutes
from datetime import datetime

fmt = '%Y-%m-%d %H:%M:%S'
tstamp1 = datetime.strptime('2016-04-06 21:26:27', fmt)
tstamp2 = datetime.strptime('2016-04-07 09:06:02', fmt)

if tstamp1 > tstamp2:
    td = tstamp1 - tstamp2
else:
    td = tstamp2 - tstamp1
td_mins = int(round(td.total_seconds() / 60))

print('The difference is approx. %s minutes' % td_mins)   
------------------------------------------------------------------------------------------
#convert a file into a dictionary

#read this log file and store the information inside a dictionary
#variable order stores all the dictionary keys in the same order as that of a single log
2021-10-26 10:26:44 | https://website.com/home | SUCCESS | Message
2021-10-26 10:26:54 | https://website.com/about | SUCCESS | Message
2021-10-26 10:27:01 | https://website.com/page | ERROR | Message
2021-10-26 10:27:03 | https://website.com/user/me | SUCCESS | Message
2021-10-26 10:27:04 | https://website.com/settings/ | ERROR | Message

import json

file_name = "log.txt"
file = open(file_name, "r")
data = []
order = ["date", "url", "type", "message"]

for line in file.readlines():
    details = line.split("|")
    details = [x.strip() for x in details]
    structure = {key:value for key, value in zip(order, details)}
    data.append(structure)
    
for entry in data:
    print(json.dumps(entry, indent = 4))





------------------------------------------------------------------------------------------
#convert a file into a dictionary

cat data.txt
a 1
b 2
c 3

with open('infile.txt') as f:
  d = dict(x.rstrip().split(None, 1) for x in f)

# or dict comprehension
with open("infile.txt") as f:
    d = {int(k): v for line in f for (k, v) in [line.strip().split(None, 1)]}

# or dict comprehension
d = { line.split()[0] : line.split()[1] for line in open("infile.txt") } 

# or by pandas
import pandas as pd 
d = pd.read_csv("file.txt", delimiter=" ", header = None).to_dict()[0]
------------------------------------------------------------------------------------------
#convert a file into a dictionary

cat data.txt
a 1
b 2
c 3

def file_read(logFile):
    f = open(logFile)
    dict = {}
    for line in f:
        key,value = line.split()
        dict[key] = value
    print(dict)

file_read('data.txt')
------------------------------------------------------------------------------------------
#convert a file into a dictionary

cat data.txt
a 1
b 2
c 3

dictionary = {}
f = open("data.txt")
for line in file:
 
    (key, value) = line.split()
    dict[key] = int(value)  # value is numeric
 
print ('\ntext file to dictionary=\n',dictionary)
------------------------------------------------------------------------------------------
#convert a file into a dictionary

cat data.txt
myline = data
myline2 = This is data
myline3 = Dict_Keydata
myline4 = Dict_datavalue

myfile = open("data.txt", 'r')
data_dict = {}
for line in myfile:
    k, v = line.strip().split('=')
    data_dict[k.strip()] = v.strip()
 
myfile.close()
 
print(' text file to dictionary =\n ',data_dict
------------------------------------------------------------------------------------------
#JSON Module to Convert text file to dictionary

import json #Import the JSON Module
dict_students = {'Name' : 'Jack', 'Sub' : 'Math', 'marks' : 100,'Grade':'A'}#open the file in write mode using with statement
with open("DictFile.txt","w") as file:
  file.write(json.dumps(dict_students)) #Write the dictionary to file
   
#reading the json file
with open("DictFile.txt", "r") as file: #open the file in read mode using with statement
 file_content = file.read() #Convert text file to Dictionary 
 print('file contents:',file_content)
------------------------------------------------------------------------------------------
#Pickle.dump() to Convert dictionary to a text file

import pickle
dict_students = {'Name' : 'Jack', 'Sub' : 'Math', 'marks' : 100,'Grade':'A'}
file = open("DictFile.pkl","wb") #open the file in write mode by using “wb”, this mode is used to open files for writing in binary format.
pickle.dump(dict_students, file) #pickle.dump() to serialize dictionary data and then write to file.
file.close()
 
#reading the DictFile.pkl" contents
file = open("DictFile.pkl", "rb") #open the binary file in reading mode(“rb”)
file_contents = pickle.load(file) #pickle.load() method to deserialize the file contents
print(file_contents)

------------------------------------------------------------------------------------------
#store a list as a dictionary

items = {}
for a in range(10):
    items[a] = []    # items[a] creates a key 'a' and stores an empty list there
    for b in range(10):
        if function() == condition:
            items[a].append(WRONG)
for a, b in oldItems:
    items[a][b] = RIGHT
------------------------------------------------------------------------------------------
#(AM/PM) using strftime

>>> from datetime import datetime
>>> print(datetime.today().strftime("%H:%M %p"))
15:31 AM

------------------------------------------------------------------------------------------
#(AM/PM) using strftime, %H (24 hour format)  %I (12 hour format)

from datetime import datetime
date_string = '2009-11-29 03:17 PM'
format = '%Y-%m-%d %I:%M %p'
my_date = datetime.strptime(date_string, format)

# This prints '2009-11-29 03:17 AM'
print my_date.strftime(format)

------------------------------------------------------------------------------------------
#Calculate Time Difference
from datetime import datetime

# start time
start_time = "2:13:57"
end_time = "11:46:38"

# convert time string to datetime
t1 = datetime.strptime(start_time, "%H:%M:%S")
print('Start time:', t1.time())

t2 = datetime.strptime(end_time, "%H:%M:%S")
print('End time:', t2.time())

# get difference
delta = t2 - t1

# time difference in seconds
print(f"Time difference is {delta.total_seconds()} seconds")

# time difference in milliseconds
ms = delta.total_seconds() * 1000
print(f"Time difference is {ms} milliseconds")

sec = delta.total_seconds()
print('difference in seconds:', sec)

min = sec / 60
print('difference in minutes:', min)

# get difference in hours
hours = sec / (60 * 60)
print('difference in hours:', hours)
------------------------------------------------------------------------------------------
#log

Jul 11 16:11:58:710 [139681125603136] dut: Device State: ON
Jul 11 16:11:58:710 [139681125603136] dut: Subscribe request received from 172.17.60.11/49248
Jul 11 16:11:58:962 [139681125603136] dut: sockAccept: new socket fd=31
Jul 11 16:11:58:962 [139681125603136] dut: sockAccept: new session nims=0x17279e0 new=0x1759750 fd=31 10.238.40.228/48002<-10.238.40.228/37400
Jul 11 16:11:58:962 [139681125603136] dut: RREQUEST: verify_login <-10.238.40.228/37400  h=367 d=147
Jul 11 16:11:58:962 [139681125603136] dut:  head  mtype=100 cmd=verify_login seq=0 ts=1499811118 frm=10.238.40.228/37400 tout=180 addr= sid=zYyeCp56Cg4og2P41oP7yQADMTQ5OTgzMjcxMwFheGEtdWltc2VydmVyMS1kZXZf
Jul 11 16:11:58:962 [139681125603136] dut:  data  time=1499811118 cmd=probe_list

import re
from datetime import datetime

pattern=re.compile(r"(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d) (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d),(?P<microsecond>\d\d\d)")
logline="2021-10-20 13:12:21,697 - root - DEBUG - begin:test(4), pattern:%d%d(4), next:(0)"

m=re.search(pattern,logline)
if m:
    print(f"Dict with string valiue : {m.groupdict()}")

    extracted_date=dict([(k,int(v)) for k,v in m.groupdict().items()])
    ### ATTENTION ###
    ### extracted_date["microsecond"] are in fact milisecond in the pattern
    extracted_date["microsecond"]*=1000

    print(f"Dict with integer value : {extracted_date}")

    begin_date=datetime(**extracted_date)
    print(str(begin_date))

else:
    print("notfound")

end_date=datetime.strptime("2021-10-20 13:38:12,456000", "%Y-%m-%d %H:%M:%S,%f")
print(end_date)

delta=end_date-begin_date

print(f"Delta in seconds   : {delta.seconds}")
print(f"Delta microseconds : {delta.microseconds}")
print(f"Delta days         : {delta.days}")
------------------------------------------------------------------------------------------
#Difference between two timestamps 

from datetime import datetime

# start and end timestamps
start_ts = 1652426243.907874
end_ts = 1652436243.907874

# convert timestamps to datetime object
dt1 = datetime.fromtimestamp(start_ts)
print('Datetime Start:', dt1)
dt2 = datetime.fromtimestamp(end_ts)
print('Datetime End:', dt2)

# Difference between two timestamps
# in hours:minutes:seconds format
delta = dt2 - dt1
print('Difference is:', delta)
------------------------------------------------------------------------------------------
#execute_external_commands

import subprocess

subprocess.call(["touch", "sample.txt"])
subprocess.call(["ls"])
print("Sample file created")
subprocess.call(["rm", "sample.txt"])
subprocess.call(["ls"])
print("Sample file deleted")
------------------------------------------------------------------------------------------

