#!/usr/bin/zsh

workon plcb

/sites/projects/plcb/manage.py cron_job >> /sites/projects/plcb/cronlog.txt

service apache2 restart
service varnish restart

deactivate
