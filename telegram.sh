#!/bin/bash
export TELEGRAM_DIR="/home/pi/.telegram-cli"
echo "Sending $2 to $1"

cd $TELEGRAM_DIR
printf "mark_read $1\nmsg $1 $2\nsafe_quit" | telegram-cli2 -W
