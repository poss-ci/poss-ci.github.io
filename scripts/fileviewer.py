from __future__ import division
import requests, json
from shutil import copyfile
from yattag import Doc, indent
from os import listdir
from os.path import isfile, join

doc, tag, text = Doc().tagtext()
with tag('html'):
    with tag('body'):
        files = [f for f in listdir("/root/poss-ci.github.io/archives") if isfile(join("/root/poss-ci.github.io/archives", f)) and f != 'helper.js']
        revfiles = files[::-1] 
        for f in revfiles:
            with tag('p'):
                text()
                with tag('a',href="https://poss-ci.github.io/archives/"+f):
                    text(f)
result = doc.getvalue()
print "Writing result to a file at /root/poss-ci.github.io/archives.html"
with open('/root/poss-ci.github.io/archives.html','w') as afile :
    afile.write(result.encode('utf-8'))