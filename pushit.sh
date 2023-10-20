#!/bin/bash
# IF you are using another domain to push your code... 

pkill -x ssh-agent 
sleep 1
echo "ssh-agents killed"
eval $(ssh-agent)
sleep 1 
echo "ssh-agent inicialized"
ssh-add ~/.ssh/github_odrsa
sleep 1
echo "ssh-key-id added"
git add . 
git commit -m "Make it Right for a better Ride"
git push --set-upstream git@github.com:daoexpression/devblog main
echo "Push completed"
sleep 3
