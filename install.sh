#!/usr/bin/bash

systemctl stop HinetTGBot.service
echo  "" > Hinet-TW.log

cp  HinetTGBot.service  /lib/systemd/system/
chmod 644 /lib/systemd/system/HinetTGBot.service
systemctl daemon-reload
systemctl start HinetTGBot.service
systemctl enable HinetTGBot.service
systemctl status HinetTGBot.service
tail -f Hinet-TW.log