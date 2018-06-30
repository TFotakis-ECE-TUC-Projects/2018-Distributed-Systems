#!/bin/bash
source venv/bin/activate
python WebService/manage.py runserver 127.0.0.1:8000 &
python ApplicationService/manage.py runserver 127.0.0.1:8001 &
python AuthService/manage.py runserver 127.0.0.1:8002 &
python StorageService/manage.py runserver 127.0.0.1:8003 &
echo "Visit: http://127:0.0.1:8000"