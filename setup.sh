python3 -m venv venv
. ./venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd startweet
python manage.py runserver
