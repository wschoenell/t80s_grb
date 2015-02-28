

Add telegram to the /etc/rc.local startup scripts 
=================================================

    su -c "telegram-cli -d -P 9999" chimera &
    sleep 5
    echo "dialog_list" | nc localhost 9999 
