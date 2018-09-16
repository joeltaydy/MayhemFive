#!/bin/bash
clear
cd CLE
celery -A CLE worker --pool=eventlet
