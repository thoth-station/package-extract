TEMPFILE := $(shell mktemp -u)
GOAPTH ?= go env GOPATH
MERCATOR_GO_PATH = $(GOPATH)/src/github.com/fabric8-analytics/mercator-go

all: install


$(GOPATH):
	mkdir -p $(GOPATH)/src

.PHONY: install
install: mercator
	pip3 install -r requirements.txt
	python3 setup.py install

.PHONY: mercator
mercator: $(BINPATH)
	[ -d $(MERCATOR_GO_PATH) ] || \
          git clone https://github.com/fabric8-analytics/mercator-go $(MERCATOR_GO_PATH)
	cd $(MERCATOR_GO_PATH) &&\
	  go get &&\
	  make RUBY=NO NPM=NO PYTHON=YES JAVA=NO GRADLE=NO DOTNET=NO RUST=NO HASKELL=NO GOLANG=NO build &&\
	  make install &&\
	  cd $(PWD)

.PHONY: uninstall
uninstall:
	python3 setup.py install --record ${TEMPFILE} && \
		cat ${TEMPFILE} | xargs rm -rf && \
		rm -f ${TEMPFILE}

coala-venv:
	@echo ">>> Preparing virtual environment for coala"
	@# We need to run coala in a virtual env due to dependency issues
	virtualenv -p python3 venv-coala
	. venv-coala/bin/activate && pip3 install -r coala_requirements.txt

.PHONY: clean
clean:
	find . -name '*.pyc' -or -name '__pycache__' -or -name '*.py.orig' | xargs rm -rf
	rm -rf venv venv-coala coverage.xml
	rm -rf dist thoth_pkgdeps.egg-info build docs/

.PHONY: devenv
devenv:
	pipenv install --dev

.PHONY: pytest
pytest:
	@echo ">>> Executing testsuite"
	python3 -m pytest -s --cov=./thoth_pkgdeps -vvl --timeout=2 test/

.PHONY: pylint
pylint:
	@echo ">>> Running pylint"
	pylint thoth_pkgdeps

.PHONY: coala
coala: coala-venv
	@echo ">>> Running coala"
	. venv-coala/bin/activate && coala --non-interactive

.PHONY: pydocstyle
pydocstyle:
	@echo ">>> Running pydocstyle"
	pydocstyle thoth_pkgdeps

.PHONY: check
check: pytest pylint pydocstyle coala


# Friendly aliases.
.PHONY: test
test: check
