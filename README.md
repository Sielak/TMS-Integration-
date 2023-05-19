- [Overview](#overview)
    - [Description](#description)
    - [Process description](#process-description)
- [Deployment](#deployment)
  - [Already configured machine](#already-configured-machine)
  - [New machine](#new-machine)
- [Contributing](#contributing)
    - [Configure project](#configure-project)
    - [Testing](#testing)
    - [Code coverage](#code-coverage)
# Overview
## Description
This integration is used to connect Jeeves with carriers.
It use [FastAPI](https://fastapi.tiangolo.com/) to create endpoints.  
From Jeeves DB it uses `q_hl_TmsIntegration` table to store order data.  
## Process description
1. During shipment process in Jeeves new rows will be generated in `q_hl_TmsIntegration` table
2. After creation Jeeves will send row ID to integration endpoint `/addShipment`
3. Integration will fetch data from Jeeves compose proper object and send it to proper Carrier
4. In response will be information about TnT number and status of request.
# Deployment
## Already configured machine
Full CI/CD in place. 
Simply create MR to test branch to automatically build, test and deploy code to test environment.
Do this same to main branch if you want to install on production.
## New machine
1. Add new service to systemd
```bash
sudo nano /etc/systemd/system/tms.service
```
```bash
# tms.service
# For running Gunicorn based application with a config file - TutLinks.com
#
# This file is referenced from official repo of TutLinks.com
# https://github.com/windson/fastapi/blob/fastapi-postgresql-caddy-ubuntu-deploy/gunicorn.service
#

[Unit]
Description=TMS on Gunicorn Web Server as Unit Service Systemd
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/tms
Environment="PATH=/home/ubuntu/virtual_environments/venv_tms/bin"
ExecStart=/home/ubuntu/virtual_environments/venv_tms/bin/gunicorn --config /opt/tms/gunicorn.py main:app

[Install]
WantedBy=multi-user.target


```
```bash
sudo systemctl daemon-reload
```
2. Configure logrotate (for daily log rotation)
```bash
sudo nano /etc/logrotate.d/tms
```
```bash
/home/ubuntu/logs/tms/access.log /home/ubuntu/logs/tms/error.log {
    su ubuntu ubuntu
    daily
    rotate 30
    compress
    delaycompress
    postrotate
        kill -USR1 `ps -C gunicorn -f | grep tms | head -n 1 | awk {'print $2'}`
    endscript
}
```

# Contributing
### Configure project
```bash
git clone git@gitlab.hl-display.com:root/tms.git
python -m venv venv_tms
source /venv_tms/bin/activate
pip install -r requirements.txt
fill this file with proper values -> lib/config.json
python main.py
```
### Testing
All test should be created in `./test` folder  .  
To run all test you need to activate virtual env and go to `root` directory and run  
```bash
coverage run --source=. -m pytest
coverage report
# detailed view
coverage html 
# to see result in browser
cd htmlcov/
sudo python -m http.server 8302 
```
### Code coverage
Code coverage always needs to be 100%
```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
gunicorn.py                                 19      0   100%
lib/__init__.py                              0      0   100%
lib/carriers/__init__.py                     3      0   100%
lib/carriers/abstract_carrier.py             7      0   100%
lib/carriers/gls.py                        102      0   100%
lib/carriers/transmission.py               124      0   100%
lib/exporter.py                             33      0   100%
lib/jeeves.py                              120      0   100%
main.py                                     17      0   100%
models/Transmission.py                      77      0   100%
models/Transmission_jeeves.py               30      0   100%
models/__init__.py                           6      0   100%
models/exporter.py                           5      0   100%
models/gls.py                               48      0   100%
models/jeeves.py                            28      0   100%
models/shipment.py                          12      0   100%
test/__init__.py                             0      0   100%
test/test_gunicorn.py                        8      0   100%
test/test_lib_carriers_gls.py              200      0   100%
test/test_lib_carriers_transmission.py     282      0   100%
test/test_lib_exporter.py                  103      0   100%
test/test_lib_jeeves.py                    216      0   100%
test/test_main.py                           24      0   100%
------------------------------------------------------------
TOTAL                                     1464      0   100%
```
