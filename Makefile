rebuild:
	rm -r dist *.egg*
	python setup.py sdist
	pip uninstall django-dvbboxes
	pip install dist/django-dvbboxes-*.tar.gz
