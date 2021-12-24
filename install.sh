#!/bin/bash
pip3 install virtualenv==20.0.23
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 installation_prerequisite.py
deactivate
