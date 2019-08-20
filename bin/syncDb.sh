#!/usr/bin/bash

host=nuke@jarvis

echo 'Dumping DB on remote'
ssh $host 'pg_dump -O -F c pollbot > pollbot.dump'
echo 'Sync DB'
scp $host:pollbot.dump /tmp/

echo 'Drop and recreate DB'
dropdb pollbot || true
createdb pollbot

echo 'Restoring DB'
pg_restore -O -j 4 -F c -d pollbot /tmp/pollbot.dump

echo 'Deleting dumps'
rm /tmp/pollbot.dump
ssh $host 'rm pollbot.dump'
echo 'Done'
