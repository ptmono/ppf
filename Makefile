

test: doctest unittest

doctest:
	nosetests --with-doc *.py

unittest:
	nosetests
zip:
	tar cf ppf.tar -l `cat tools/zip_file_list`

upload:
	python tools/uploader.py --with-config

unload:
	python -c 'from tests.common import destroy; destroy()'

# For other people
IS_EXITS_PWD=$(wildcard passwd)
ifeq ($(strip $(IS_EXITS_PWD)),)
	PASS="USER_ID"
else
	PASS=`cat passwd`
endif

prepare-git:
	@if [ -f config.py.bak ]; then \
		echo "config.py.bak is exists"; \
		echo "Do \"make end-git\""; \
		false; \
	fi
	mv config.py config.py.bak
	sed "s/$(PASS)/USER_PASSWORD/g" config.py.bak >> config.py
	sed -i 's/ptmono/USER_ID/g' config.py

	mv dbs/index.json dbs/index.json.bak
	# double back up. Because it is not version controled.
	cp -f dbs/index.json.bak dbs/index.json.bak2
	@echo '{"0000000001" : {"category": "a", "title":"Welcome"}}' >> dbs/index.json

end-git:
	@if [ ! -f config.py.bak ]; then \
		echo "Why end? You need prepare-git befor that."; \
		false; \
	fi
	rm config.py
	mv config.py.bak config.py

	rm dbs/index.json
	mv dbs/index.json.bak dbs/index.json


