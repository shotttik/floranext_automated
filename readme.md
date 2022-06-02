# Instructions to run the project in Linux

### Install pip3
> python3 -m pip install --user --upgrade pip

### Installing virtualenv
> python3 -m pip install --user virtualenv

### Creating a virtual environment¶
> python3 -m venv env

### Activating a virtual environment¶
> source env/bin/activate

### Installing packages
> python3 -m pip install -r requirements.txt

### Create .env file and insert inside it your credentials
```
ADMIN_EMAIL = 'automation@mail.com'
ADMIN_PASSWORD = 'automation'
SENDGRID_API_KEY = 'SENDGRID_API_KEY'
EMAIL = 'hello@automation.com'
PASSWORD = 'automation'
SMTP_SERVER = 'smtp.sendgrid.net'
PORT = '587'
TO_EMAIL = 'automation@send.com'
```

## RUN PROJECT
> python3 main.py

# ATTENTION:
### Make sure you you have `log` folder where your script `main.py` is located
### Make sure you you secret information/credentials is correct and inserted in `.env` file and this file located where your script `main.py`
### Make Sure you completed all the steps before the script was executed

#### This chromedriver is for `101.0.4951.64` chrome browser. if your chrome browser dont support, you need to install same version of Chrome
> https://chromedriver.chromium.org/downloads

## GOOD LUCK !