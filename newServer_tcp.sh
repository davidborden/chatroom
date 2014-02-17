#! /bin/sh
set -e
#Start the server with the port ($1), pipe in the welcome ($2)
#Send output to $3
python secure_tcp_chatroom.py $1 &

echo $!
#Save its PID so we can kill it after we run the server.
