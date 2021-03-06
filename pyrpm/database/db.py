#
# Copyright (C) 2004, 2005 Red Hat, Inc.
# Authors: Phil Knirsch <pknirsch@redhat.com>
#          Thomas Woerner <twoerner@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

import pyrpm.openpgp as openpgp

#
# Database base class only __init__ and clear are implemented
# Merge of old database class and parts of the resolver
#

class RpmDatabase:
    OK = 1
    ALREADY_INSTALLED = -1
    NOT_INSTALLED = -3

    def __init__(self, config, source, buildroot=''):
        if self.__class__ is RpmDatabase:
            raise NotImplementedError, "Abstract class"
        self.config = config
        self.source = source
        self.buildroot = buildroot or ''
        if self.buildroot and self.buildroot[-1] != '/':
            self.buildroot += '/'
        RpmDatabase.clear(self)
        self.keyring = openpgp.PGPKeyRing()
        self.is_read = 0                # 1 if the database was already read

    def __contains__(self, pkg):
        raise NotImplementedError

    # clear all structures
    def clear(self):
        pass

    # Clears the specified tags resp. keeps the ntags in all packages in repo.
    # Make sure that this only gets implemented properly in databases where
    # packages can dynamically reload single tags if necessary!
    def clearPkgs(self, tags=None, ntags=None):
        pass

    def setBuildroot(self, buildroot):
        """Set database chroot to buildroot."""
        self.buildroot = buildroot or ''
        if self.buildroot and self.buildroot[-1] != '/':
            self.buildroot += '/'

    def importFilelist(self):
        return 1

    def isFilelistImported(self):
        return 1

    ### not implemented functions ###

    def open(self):
        """If the database keeps a connection, prepare it."""
        raise NotImplementedError

    def close(self):
        """If the database keeps a connection, close it."""
        raise NotImplementedError

    def read(self):
        """Read the database in memory."""
        raise NotImplementedError

    def getMemoryCopy(self, reposdb=None):
        from pyrpm.database.memorydb import RpmMemoryDB
        db = RpmMemoryDB(self.config, self.source, self.buildroot)
        db.addPkgs(self.getPkgs())
        return db

    def isIdentitySave(self):
        """return if package objects that are added are in the db afterwards
        (.__contains__() returns True and the object are return from searches)
        """
        raise NotImplementedError

    # add package
    def addPkg(self, pkg):
        raise NotImplementedError

    # add package list
    def addPkgs(self, pkgs):
        for pkg in pkgs:
            self.addPkg(pkg)

    # remove package
    def removePkg(self, pkg):
        raise NotImplementedError

    def getPkgs(self):
        raise NotImplementedError

    def getNames(self):
        raise NotImplementedError

    def hasName(self, name):
        raise NotImplementedError

    def getPkgsByName(self, name):
        raise NotImplementedError

    def getFilenames(self):
        raise NotImplementedError

    def numFileDuplicates(self, filename):
        raise NotImplementedError

    def getFileDuplicates(self):
        raise NotImplementedError

    def iterProvides(self):
        raise NotImplementedError

    def iterRequires(self):
        raise NotImplementedError

    def getFileRequires(self):
        return [filename for filename, f, ver, pkg in self.iterRequires()
                if filename[0]=="/"]

    def getPkgsFileRequires(self):
        result = {}
        for filename, flag, ver, pkg in self.iterRequires():
            if filename[0] == "/":
                result.setdefault(pkg, []).append(filename)
        return result
    
    def iterConflicts(self):
        raise NotImplementedError

    def iterObsoletes(self):
        raise NotImplementedError

    def iterTriggers(self):
        raise NotImplementedError

    def reloadDependencies(self):
        raise NotImplementedError

    def searchPkgs(self, names):
        raise NotImplementedError

    def search(self, words):
        if not words:
            return []
        result = []
        for pkg in self.getPkgs():
            for word in words:
                if (word in pkg.get('name', '') or
                    word in (pkg['summary'] and pkg['summary'][0] or '') or
                    word in (pkg['description'] and
                             pkg['description'][0] or '') or
                    word in (pkg['rpm_packager'] or '') or 
                    word in (pkg['group'] and pkg['group'][0] or '') or
                    word in (pkg['url'] and pkg['url'][0] or '')
                    ):
                    result.append(pkg)
                    break
        return result
                

    def searchProvides(self, name, flag, version):
        raise NotImplementedError

    def searchFilenames(self, filename):
        raise NotImplementedError

    def searchRequires(self, name, flag, version):
        raise NotImplementedError

    def searchConflicts(self, name, flag, version):
        raise NotImplementedError

    def searchObsoletes(self, name, flag, version):
        raise NotImplementedError

    def searchTriggers(self, name, flag, version):
        raise NotImplementedError

    def searchDependency(self, name, flag, version):
        """Return list of RpmPackages from self.names providing
        (name, RPMSENSE_* flag, EVR string) dep."""
        s = self.searchProvides(name, flag, version).keys()
        if name[0] == '/': # all filenames are beginning with a '/'
            s += self.searchFilenames(name)
        return s

    def _getDBPath(self):
        raise NotImplementedError

# vim:ts=4:sw=4:showmatch:expandtab
