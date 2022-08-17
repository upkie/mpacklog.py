# Documentation Makefile
#
# Copyright 2022 Stéphane Caron

PROJECT_NAME = mpacklog

# You can also set these variables from the command line.
DOXYGEN      = doxygen
HTMLDIR      = html
REMOTEDIR    = scaron.info:public_html/doc/$(PROJECT_NAME)

.PHONY: clean html open upload

html:
	(cd .. && $(DOXYGEN) Doxyfile)

clean:
	rm -rf $(HTMLDIR)

open:
	firefox $(HTMLDIR)/index.html

upload: clean html
	rsync -auvz --delete-after $(HTMLDIR)/ $(REMOTEDIR)/
