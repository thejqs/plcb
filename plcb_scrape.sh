#!/bin/bash

workon plcb

./manage.py cron_job >> /sites/projects/plcb/cronlog.txt

service apache restart
service varnish restart

deactivate
