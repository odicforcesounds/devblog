#!/bin/ksh
# IF you are using another domain to push your code... 
git diff
pkill -x ssh-agent 
sleep 1
echo "ssh-agents killed"
eval $(ssh-agent)
sleep 1 
echo "ssh-agent inicialized"
ssh-add ~/.ssh/github
sleep 1
echo "ssh-key-id added"
git pull git@github.com:odicforcesounds/devblog
