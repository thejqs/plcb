#!/usr/bin/env zsh

'''
a helper script to make sure the server process updates to account for
new data and also that the cache refreshes at the right time --
but only after the scraper completes and exits, reliquishing memory
'''

/sites/virtualenvs/plcb/bin/python /sites/projects/plcb/manage.py cron_job >> /sites/projects/plcb/cronlog.txt

printf "restarting apache and varnish ....\n" >> /sites/projects/plcb/cronlog.txt
printf "_%.0s\n" {1..30} >> /sites/projects/plcb/cronlog.txt
service apache2 restart
service varnish restart
printf "done." >> /sites/projects/plcb/cronlog.txt
