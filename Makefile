
all:
	@echo Use make install to install
	@echo You must have sudo prepared
	
install:
	sudo cp monitorcn.sh /usr/local/bin/
	sudo cp cn2zabbix.py /usr/local/bin/
	pip install -r requirements.txt
	sudo mkdir -p /etc/cn2zabbix/
	sudo cp monitorcn.service /etc/systemd/system/
	sudo systemctl daemon-reload
	
	
	
