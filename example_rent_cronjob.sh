#!/bin/bash

# use "$crontab -e " to add the following line:
# 0 10,21 * * * <path-to-project>/example_rent_cronjob.sh
# do nt forget to chmox +x this file
# for me this is
# 0 10,21 * * * /home/marcel/Projects/realestatescrapper/example_rent_cronjob.sh
cd /home/marcel/Projects/realestatescrapper # set to your path
source venv/bin/activate
python example_rent.py &>> log
