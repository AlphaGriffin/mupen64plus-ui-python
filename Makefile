# Copyright (C) 2017 Alpha Griffin
# @%@~LICENSE~@%@
#
# A simple make file to automate some of the build steps for Mupen64Plus.

# Adapted from the file auto-generated by sphinx-quickstart.

# You can set these variables from the command line.
SPHINXOPTS    = -c etc/sphinx
SPHINXBUILD   = sphinx-build
PAPER         =
DOCDIR        = doc

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(DOCDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .


.PHONY: default

default: help
	@echo
	@echo "Please choose a make target and try again."

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  help           display this help screen"
	@echo ""
	@echo "  all            to make all common tasks: python, docs"
	@echo "  clean          to clean all common tasks: python_clean, docs_clean"
	@echo ""
	@echo "  install        to install what has been built to the system (first try make all)"
	@echo ""
	@echo "  python         to build Python code"
	@echo "  python_clean   to clean up after Python build"
	@echo ""
	@echo "  apidoc         to generate new API template files for Sphinx"
	@echo "  apidoc_clean   to remove the API template files for Sphinx (USE CAUTION: these may have been manually edited)"
	@echo ""
	@echo "  docs           to make all documentation: html, text, man, coverage"
	@echo "  docs_clean     to clean up all generated documentation"
	@echo "  html           to make standalone HTML files"
	@echo "  text           to make text files"
	@echo "  man            to make manual pages"


all:	qtpy python #docs

clean:	docs_clean python_clean



python:
	./setup.py build_py

python_clean:
	./setup.py clean
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ | xargs -r rm -r


qtpy:
	./setup.py build_qt

qtpy_clean:
	find src -type f -name "*_ui.py" | xargs -r rm


install:
	./setup.py install
	if [ -d "doc/man" ]; then \
		install -d /usr/local/share/man/man1; \
		cp -r doc/man/* /usr/local/share/man/man1; \
	fi



apidoc:
	sphinx-apidoc src -o api

apidoc_clean:
	rm -rf api


docs:	html text man coverage
	@echo "Documentation finished."

docs_clean:
	rm -rf $(DOCDIR)/doctrees
	rm -rf $(DOCDIR)/html
	rm -rf $(DOCDIR)/text
	rm -rf $(DOCDIR)/man
	rm -rf $(DOCDIR)/coverage

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(DOCDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(DOCDIR)/html."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(DOCDIR)/text
	@echo
	@echo "Build finished. The text files are in $(DOCDIR)/text."

man:
	$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(DOCDIR)/man
	@echo
	@echo "Build finished. The manual pages are in $(DOCDIR)/man."

coverage:
	$(SPHINXBUILD) -b coverage $(ALLSPHINXOPTS) $(DOCDIR)/coverage
	@echo "Testing of coverage in the sources finished, look at the " \
	      "results in $(DOCDIR)/coverage/python.txt."


