#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2015-2017 Dave Parsons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function
import os
import sys
import shutil
import tarfile
import zipfile

try:
    # For Python 3.0 and later
    # noinspection PyCompatibility
    from urllib.request import urlopen
    # noinspection PyCompatibility
    from html.parser import HTMLParser
    # noinspection PyCompatibility
    from urllib.request import urlretrieve
except ImportError:
    # Fall back to Python 2
    # noinspection PyCompatibility
    from urllib2 import urlopen
    # noinspection PyCompatibility
    from HTMLParser import HTMLParser
    # noinspection PyCompatibility
    from urllib import urlretrieve


# Parse the Fusion directory page
class CDSParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.HTMLDATA = []

    def handle_data(self, data):
        # Build a list of numeric data from any element
        if data.find("\n") == -1:
            if data[0].isdigit():
                self.HTMLDATA.append(data)
                self.HTMLDATA.sort(key=lambda s: [int(u) for u in s.split('.')])

    def clean(self):
        self.HTMLDATA = []


def convert_path(path):
    # OS path separator replacement funciton
    return path.replace(os.path.sep, '/')


def main():
    # Check minimal Python version is 2.7
    if sys.version_info < (2, 7):
        sys.stderr.write('You need Python 2.7 or later\n')
        sys.exit(1)

    # Setup url and file paths
    url = 'https://softwareupdate.vmware.com/cds/vmw-desktop/fusion/'
    dest = os.path.dirname(os.path.abspath(__file__))

    # Re-create the tools folder
    shutil.rmtree(dest + '/tools', True)
    os.mkdir(dest + '/tools')

    # Get the list of Fusion releases
    # And get the last item in the ul/li tags
    response = urlopen(url)
    html = response.read()
    parser = CDSParser()
    parser.feed(str(html))
    url = url + parser.HTMLDATA[-1] + '/'
    parser.clean()

    # Open the latest release page
    # And build file URL
    response = urlopen(url)
    html = response.read()
    parser.feed(str(html))
    urlpost15 = url + parser.HTMLDATA[-1] + '/packages/com.vmware.fusion.tools.darwin.zip.tar'
    urlpre15 = url + parser.HTMLDATA[-1] + '/packages/com.vmware.fusion.tools.darwinPre15.zip.tar'
    parser.clean()

    # Download the darwin.iso tgz file
    print('Retrieving Darwin tools from: ' + urlpost15)
    urlretrieve(urlpost15, convert_path(dest + '/tools/com.vmware.fusion.tools.darwin.zip.tar'))

    # Extract the tar to zip
    tar = tarfile.open(convert_path(dest + '/tools/com.vmware.fusion.tools.darwin.zip.tar'), 'r')
    tar.extract('com.vmware.fusion.tools.darwin.zip', path=convert_path(dest + '/tools/'))
    tar.close()

    # Extract the iso and sig files from zip
    cdszip = zipfile.ZipFile(convert_path(dest + '/tools/com.vmware.fusion.tools.darwin.zip'), 'r')
    cdszip.extract('payload/darwin.iso', path=convert_path(dest + '/tools/'))
    cdszip.extract('payload/darwin.iso.sig', path=convert_path(dest + '/tools/'))
    cdszip.close()

    # Move the iso and sig files to tools folder
    shutil.move(convert_path(dest + '/tools/payload/darwin.iso'), convert_path(dest + '/tools/darwin.iso'))
    shutil.move(convert_path(dest + '/tools/payload/darwin.iso.sig'), convert_path(dest + '/tools/darwin.iso.sig'))

    # Cleanup working files and folders
    shutil.rmtree(convert_path(dest + '/tools/payload'), True)
    os.remove(convert_path(dest + '/tools/com.vmware.fusion.tools.darwin.zip.tar'))
    os.remove(convert_path(dest + '/tools/com.vmware.fusion.tools.darwin.zip'))

    # Download the darwinPre15.iso tgz file
    print('Retrieving DarwinPre15 tools from: ' + urlpre15)
    urlretrieve(urlpre15, convert_path(dest + '/tools/com.vmware.fusion.tools.darwinPre15.zip.tar'))

    # Extract the tar to zip
    tar = tarfile.open(convert_path(dest + '/tools/com.vmware.fusion.tools.darwinPre15.zip.tar'), 'r')
    tar.extract('com.vmware.fusion.tools.darwinPre15.zip', path=convert_path(dest + '/tools/'))
    tar.close()

    # Extract the iso and sig files from zip
    cdszip = zipfile.ZipFile(convert_path(dest + '/tools/com.vmware.fusion.tools.darwinPre15.zip'), 'r')
    cdszip.extract('payload/darwinPre15.iso', path=convert_path(dest + '/tools/'))
    cdszip.extract('payload/darwinPre15.iso.sig', path=convert_path(dest + '/tools/'))
    cdszip.close()

    # Move the iso and sig files to tools folder
    shutil.move(convert_path(dest + '/tools/payload/darwinPre15.iso'), convert_path(dest + '/tools/darwinPre15.iso'))
    shutil.move(convert_path(dest + '/tools/payload/darwinPre15.iso.sig'), convert_path(dest + '/tools/darwinPre15.iso.sig'))

    # Cleanup working files and folders
    shutil.rmtree(convert_path(dest + '/tools/payload'), True)
    os.remove(convert_path(dest + '/tools/com.vmware.fusion.tools.darwinPre15.zip.tar'))
    os.remove(convert_path(dest + '/tools/com.vmware.fusion.tools.darwinPre15.zip'))


if __name__ == '__main__':
    main()
