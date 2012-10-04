# - test, real-mode
# - prepare-git, end-git

# Test with "make test" and restore config.py and index.json with "make
# real-mode".

# For other people
IS_EXITS_PWD=$(wildcard passwd)
ifeq ($(strip $(IS_EXITS_PWD)),)
	PASS="USER_ID"
else
	PASS=`cat private/passwd`
	PASS_SERVER=`cat private/passwd_server`
endif



test: doctest unittest
	@echo "Notice: You need \"make real-mode\" to restore files."

doctest: test-mode
	nosetests --with-doc *.py

unittest: test-mode
	nosetests
zip:
	tar cf ppf.tar -l `cat tools/zip_file_list`

prepare-upload:
	sed -i "s/$(PASS)/USER_PASSWORD/g" config.py
	chmod 777 dbs
	chmod 777 files
	chmod 666 dbs/index.json

upload: prepare-upload
	python tools/uploader.py --with-config
	sed -i "s/USER_PASSWORD/$(PASS)/g" config.py

unload:
	python -c 'from tests.common import destroy; destroy()'

prepare-git:
	@if [ -f config.py.bak ]; then \
		echo "config.py.bak is exists"; \
		echo "Do \"make end-git\""; \
		false; \
	fi
	mv config.py config.py.bak
	sed "s/$(PASS)/USER_PASSWORD/g" config.py.bak >> config.py
	sed -i "s/$(PASS_SERVER)/USER_PASSWORD/g" config.py
	sed -i 's/ptmono/USER_ID/g' config.py

	mv dbs/index.json dbs/index.json.bak
	# double back up. Because it is not version controled.
	cp -f dbs/index.json.bak dbs/index.json.bak2
	@echo '{"0000000001" : {"category": "a", "title":"Welcome"}}' >> dbs/index.json
	chmod 666 dbs/index.json
	@echo "Notice: You need \"make end-git\" to restore files."

end-git:
	@if [ ! -f config.py.bak ]; then \
		echo "Why end? You need prepare-git befor that."; \
		false; \
	fi
	rm config.py
	mv config.py.bak config.py
	@if [ ! -f dbs/index.json.bak ]; then \
		echo "There is no dbs/index.json.bak"; \
		echo "It seem an error during prepare-git." \
		echo "We restore the file." \
		cp dbs/index.json.bak2 dbs/index.json.bak; \
	fi
	@if [ ! -f dbs/index.json ]; then \
		mv dbs/index.json.bak dbs/index.json; \
	else \
		rm dbs/index.json; \
		mv dbs/index.json.bak dbs/index.json; \
	fi


test-mode:
	# LOCAL_TEST=False --> LOCAL_TEST=True
	sed -i "s/LOCAL_TEST=False/LOCAL_TEST=True/g" config.py
	@if [ ! -f dbs/index.json.bak ]; then \
		cp dbs/index.json dbs/index.json.bak; \
	fi

real-mode:
	sed -i "s/LOCAL_TEST=True/LOCAL_TEST=False/g" config.py
	mv dbs/index.json.bak dbs/index.json

init-index:
	echo '{"0000000001" : {"category": "a", "title":"Welcome"}}' > dbs/index.json
	chmod 666 dbs/index.json
