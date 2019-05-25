#!/usr/bin/bash
host=nuke@jarvis
timestamp=`date +%Y-%m-%d_%H-%m`
dest="backup/pollbot/pollbot_${timestamp}.dump"

ssh $host "mkdir -p ~/backup/pollbot"
ssh $host "pg_dump -F c pollbot> ~/$dest"
