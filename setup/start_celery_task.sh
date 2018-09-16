#!/bin/bash
clear
cd CLE
celery -A CLE beat -l info
