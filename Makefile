
SRCDIR=taskcarrier
DOCDIR=doc

all: clean in test

clean:
	python setup.py clean
	find . -name .DS_Store -delete
	find . -name *.pyc -delete
	rm -rf build

in: inplace

inplace:
	python setup.py build_ext --inplace

doc: inplace
	$(MAKE) -C "$(DOCDIR)" html

clean-doc:
	rm -rf doc/_*

test:
	nosetests "$(SRCDIR)" -sv --with-coverage

install:inplace
	python setup.py install
