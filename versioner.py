import os
import re
from errors import (NoVersionNumber, NoValidVersion, VersionZero)


class Versioner(object):
    def __init__(self, filename, pads=3, postfix='.v', ext='.*'):
        self.filename = os.path.normpath(filename).replace('\\', '/')
        self.postfix = postfix
        self.pads = pads
        extension = os.path.splitext(self.filename)[1]
        self.ext = extension[1:] if extension else ext
        self.regex_splits = re.compile('(?P<head>.*%s)(?P<version>[0-9]+)(?P<tail>[.].*)' % (self.postfix))

    def __str__(self):
        return self.filename

    def __eq__(self, version):
        if isinstance(version, str):
            version = int(version)
        return self.current == version

    @staticmethod
    def int_to_pad(pads, number):
        return ('%s%sd' % ('%0', '%d' % pads)) % number

    def _current(self, path):
        try:
            return int(self._splits['version'])
        except Exception:
            raise NoVersionNumber

    @property
    def _splits(self):
        info = [match.groupdict() for match in self.regex_splits.finditer(self.filename)]
        if info:
            return info[0]
        else:
            return {'head': self.filename[:self.filename.rindex('.')],
                    'version': None,
                    'tail': self.filename[self.filename.rindex('.'):]}

    @property
    def versionless(self):
        try:
            if not self._splits.get('tail'):
                return self._splits.get('head')
            else:
                if not self.isVersionless:
                    filename = self._splits.get('head')[:len(self.postfix) * -1]
                    return '%s%s' % (filename, self._splits.get('tail'))
                else:
                    return '%s%s' % (self._splits.get('head'), self._splits.get('tail'))
        except Exception:
            raise NoValidVersion

    @property
    def isVersionless(self):
        return not self._splits.get('version')

    def to_version(self, version):
        version = self.int_to_pad(int(self.pads), int(version))

        if self.isVersionless:
            return '%s%s%s%s' % (self._splits['head'], self.postfix, version, self._splits['tail'])
        else:
            return '%s%s%s' % (self._splits['head'], version, self._splits['tail'])

    @property
    def first(self):
        return self.to_version(1)
        
    @property
    def current(self):
        return self._current(self.filename)

    @property
    def next(self):
        if not self.current:
            return self.first

        return self.to_version(self.current + 1)

    @property
    def previous(self):
        version = self.current
        if not version:
            raise NoValidVersion

        elif version > 1:
            return self.to_version(self.current - 1)

        elif version == 1:
            raise VersionZero

    def __iter__(self):
        dirname, base = os.path.split(self._splits['head'])
        if os.path.isdir(dirname):
            for ver in sorted(os.listdir(dirname)):
                if ver.startswith(base) and ver.endswith(self._splits['tail']):
                    yield Versioner(os.path.join(dirname, ver))
    
    def __contains__(self, version):
        if isinstance(version, str):
            version = int(version)
        return any(filter(lambda x: x == version, self))
    @property
    def last(self):
        old = 0
        last = None
        for ver in self:
            try:
                new = ver.current
                if old <= new:
                    old = new
                    last = ver
            except NoVersionNumber:
                pass

        return last

    @property
    def allVersionsInt(self):
        for ver in sorted(self):
            yield ver.current

    @property
    def lastInt(self):
        return max(self.allVersionsInt)


if __name__ == '__main__':
    filename = r"examples\test_mod_v001.txt"
    ver = Versioner(filename)
    print(ver.isVersionless)
    print(ver.versionless)
    print(ver.to_version(15))
    print(ver.first)
    print(ver.current)
    print(ver.next)
    print(ver.last)
    print(7 in ver)
    print(ver.previous)
    
