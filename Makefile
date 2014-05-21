ifeq ("$(wildcard ./config/live.cfg)", "")
	SETTINGS=./config/development.cfg
else
	SETTINGS=./config/live.cfg
endif

run:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./main.py

init:
	virtualenv ./env

update:
	./env/bin/python ./env/bin/pip install -r ./requirements.txt

clean:
	rm -rf .env


db:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py createdb

data: tickets tokens shifts

tickets:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py createtickets

tokens:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py addtokens

shifts:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py createroles
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py createshifts


checkreconcile:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py reconcile

reallyreconcile:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py reconcile -d


warnexpire:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py warnexpire

expire:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py expire


shell:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py shell

testemails:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py testemails

admin:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./utils.py makeadmin

test:
	SETTINGS_FILE=./config/test.cfg ./env/bin/python ./env/bin/flake8 ./models ./views --ignore=E501,F403,E302
	SETTINGS_FILE=./config/test.cfg ./env/bin/python ./env/bin/nosetests ./models ./views
