#!/usr/bin/env zsh

/sites/virtualenvs/plcb/bin/python /sites/projects/plcb/manage.py cron_job >> /sites/projects/plcb/cronlog.txt

printf "restarting apache and varnish ....\n" >> /sites/projects/plcb/cronlog.txt
service apache2 restart
service varnish restart
printf "done.\n" >> /sites/projects/plcb/cronlog.txt
printf "\n" >> /sites/projects/plcb/cronlog.txt
printf "_%.0s" {1..30} >> /sites/projects/plcb/cronlog.txt
