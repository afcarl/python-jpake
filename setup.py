#!/usr/bin/env python

import os, sys, subprocess, re
from distutils.core import setup, Command
from distutils.command.sdist import sdist as _sdist

class Test(Command):
    description = "run unit tests"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        for t in ["jpake/test_jpake.py",
                  ]:
            rc = self.do_test(t)
            if rc != 0:
                sys.exit(rc)

    def do_test(self, which):
        print "======= running %s" % which
        p = subprocess.Popen([sys.executable, which])
        rc = p.wait()
        if rc != 0:
            print >>sys.stderr, "Test (%s) FAILED" % which
        print "== finished %s" % which
        return rc

VERSION_PY = """
# This file is originally generated from Git information by running 'setup.py
# version'. Distribution tarballs contain a pre-generated copy of this file.

__version__ = '%s'
"""

def update_version_py():
    if not os.path.isdir(".git"):
        print "This does not appear to be a Git repository."
        return
    try:
        p = subprocess.Popen(["git", "describe", "--dirty", "--always"],
                             stdout=subprocess.PIPE)
    except EnvironmentError:
        print "unable to run git, leaving jpake/_version.py alone"
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print "unable to run git, leaving jpake/_version.py alone"
        return
    # we use tags like "python-jpake-0.5", so strip the prefix
    assert stdout.startswith("python-jpake-")
    ver = stdout[len("python-jpake-"):].strip()
    f = open("jpake/_version.py", "w")
    f.write(VERSION_PY % ver)
    f.close()
    print "set jpake/_version.py to '%s'" % ver

def get_version():
    try:
        f = open("jpake/_version.py")
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None

class Version(Command):
    description = "update _version.py from Git repo"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        update_version_py()
        print "Version is now", get_version()

class sdist(_sdist):
    def run(self):
        update_version_py()
        # unless we update this, the sdist command will keep using the old
        # version
        self.distribution.metadata.version = get_version()
        return _sdist.run(self)

setup(name="jpake",
      version=get_version(),
      description="J-PAKE password-authenticated key exchange (pure python)",
      author="Brian Warner",
      author_email="warner-pyjpake@lothar.com",
      url="http://github.com/warner/python-jpake",
      packages=["jpake"],
      license="MIT",
      cmdclass={ "test": Test, "version": Version, "sdist": sdist },
      )
