# Author: Leandro Inocencio aka Cesio (cesio.arg@gmail.com)

import os
import re
import json
from collections import OrderedDict


_PLACEHOLDER_REGEX = re.compile('{(.+?)}')
_FIELDPATTERN_REGEX = re.compile('({.+?})')
_FIELDREPLACE = r'(?P<%s>[:a-zA-Z0-9_-]*)'

rules = {}
convertionTable = {}


class JSONReadError(Exception):
    pass


class InvalidFilePath(Exception):
    pass


if os.environ.get('RULESFILE'):
    try:
        print("Cargando JSON file", os.environ['RULESFILE'])

        with open(os.environ['RULESFILE'], 'r') as jsonf:
            jsonData = json.loads(jsonf.read())
            rules = jsonData['rules']

            if not convertionTable:
                convertionTable = jsonData['convertionTable']
    except IOError:
        raise JSONReadError('Error reading JSON file.')


class Freeway(object):
    def __init__(self, filepath=None, pattern='auto', rules=rules,
                 convertionTable=convertionTable, rulesfile=None, **kwargs):
        self._rules = {}

        if not rulesfile:
            rulesfile = os.environ['RULESFILE']

        if not rules and os.environ.get('RULESFILE'):
            try:
                # print "Cargando JSON file", rulesfile
                with open(rulesfile, 'r') as jsonf:
                    jsonData = json.loads(jsonf.read())
                    rules = jsonData['rules']

                    if not convertionTable:
                        convertionTable = jsonData['convertionTable']

            except IOError:
                raise JSONReadError('Error reading JSON file.')

        if isinstance(pattern, basestring):
            pattern = [pattern]
        self.pattern = pattern

        self._rules = OrderedDict(Freeway.get_rules(rules))
        self._convertionTable = convertionTable

        if filepath:
            self.parseFilepath(filepath, self.pattern)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self)

    def parseFilepath(self, filepath, patterns=['auto']):
        if filepath:
            self.filepath = filepath.replace('\\', '/')

            for key, value in Freeway.info_from_path(self.filepath,
                                                     self._rules,
                                                     self.pattern).items():
                setattr(self, key, value)

    @staticmethod
    def info_from_path(path, rules, patterns=['auto']):
        for pattern in patterns:
            if pattern == 'auto':
                for key, rule in rules.items():
                    for item in Freeway.expandRules(key, Freeway(rules=rules)):
                        match = re.match(item.regex, path, re.IGNORECASE)
                        if not match:
                            continue
                        info = {key:value for key, value in match.groupdict().items() if not key.endswith('_')}
                        info['pattern'] = pattern
                        return info

            else:
                for item in Freeway.expandRules(pattern, Freeway(rules=rules)):
                    match = re.match(item.regex, path, re.IGNORECASE)

                    if match:
                        info = {pattern: value for pattern, value in match.groupdict().items() if not pattern.endswith('_')}
                        return info

        return {}

    @property
    def match(self):
        patterns = {}
        fullMatch = False
        for pattern in self.pattern:
            for rule in Freeway.expandRules(pattern, Freeway(rules=rules)):
                for field in rule.fields:
                    if self.data.get(field):
                        patterns[pattern] = True
                    else:
                        patterns[pattern] = False
                        break

        for pattern, match in patterns.items():
            if not match:
                self.pattern.remove(pattern)
            else:
                fullMatch = True

        return fullMatch

    @property
    def dirname(self):
        return os.path.dirname(self.filepath)

    @property
    def basename(self):
        return os.path.basename(self.filepath)

    @property
    def data(self):
        elements = self.__dict__.copy()
        elements.pop('_rules')
        elements.pop('_convertionTable')
        elements.pop('pattern')
        return elements

    @staticmethod
    def get_rules(allrules):
        for name, rules in allrules.items():
            if not name.startswith('_'):
                yield name, [RuleParser(name, rule) for rule in rules]

    @staticmethod
    def expandRules(attr, rules):
        rules._rules["_ignoreMissing"] = True

        for rule in rules._rules.get(attr, []):
            antiloop = 0
            rule = RuleParser(attr, unicode(rule))
            field = rule

            while set(rules._rules) & set(rule.fields):
                for field in rule.fields:
                    if field in rules:
                        rule.rule = rule.rule.replace('{%s}' % field,
                                                      rules.get(field, field))

                if antiloop > 10000:
                    raise Exception('Loop infinito en Freeway.expandRules(), variable> %s' % field)
                antiloop += 1

            yield rule

        rules._rules["_ignoreMissing"] = False

    def __getattribute__(self, attr):
        ignoreMissing = object.__getattribute__(self, '_rules').get("_ignoreMissing")
        rules = object.__getattribute__(self, '_rules').get(attr)

        if rules:
            for rule in rules:
                try:
                    name = rule.rule
                    for field in rule.fields:
                        value = getattr(self, field, None)
                        if value is not None:
                            name = name.replace('{%s}' % field, value)
                        else:
                            break

                    if not _PLACEHOLDER_REGEX.findall(name):
                        break

                except AttributeError:
                    raise Exception("Can't find '" + field + "' attribute.")

            missing = [part for part in _PLACEHOLDER_REGEX.findall(name)]

            if missing and not ignoreMissing:
                raise NoAttributes('No se ha encontrado el atributo: %s' % ', '.join(missing))

            return name
        else:
            try:
                return object.__getattribute__(self, attr)
            except Exception:
                switchs = object.__getattribute__(self, '_convertionTable') or {}

                for table, switch in switchs.items():
                    if attr in switch:
                        for key in switch:
                            try:
                                value = object.__getattribute__(self, key)
                                index = switchs[table][key].index(value)
                                return switchs[table][attr][index]

                            except (AttributeError, ValueError):
                                pass

    def __contains__(self, item):
        for rule in self._rules:
            if rule == item:
                return True
        return False

    def __getitem__(self, item):
        for rule in self._rules:
            if rule == item:
                return rule

        raise KeyError(item)

    def get(self, item, default=None):
        return getattr(self, item, default)

    def update(self, data):
        self.__dict__.update(data)

    def clean(self):
        for key, value in self.__dict__.items():
            if key not in ['pattern', '_rules', '_convertionTable']:
                delattr(self, key)


class RuleParser(object):
    def __init__(self, name, rule):
        self.name = name
        self.rule = unicode(rule)

    def __getitem__(self, item):
        index = 0
        if isinstance(item, int):
            for field in self.fields:
                if index == item:
                    return field
                index += 1

        elif isinstance(item, basestring):
            for field in self.fields:
                if field == item:
                    return index
                index += 1

    def __str__(self):
        return self.rule

    def __repr__(self):
        return str(self)

    def __contains__(self, item):
        if isinstance(item, basestring):
            for field in self.fields:
                if field == item:
                    return True

    @property
    def lenFields(self):
        index = 0
        for field in self.fields:
            index += 1
        return index

    @property
    def fields(self):
        for part in _PLACEHOLDER_REGEX.findall(self.rule):
            yield part

    @property
    def regex(self):
        duplis = []
        regexRule = self.rule
        for field in _FIELDPATTERN_REGEX.findall(self.rule):
            if field not in duplis:
                duplis.append(field)
                fieldReplace = field[1:-1]
            else:
                fieldReplace = field[1:-1] + '_'

            regexRule = regexRule.replace(field, _FIELDREPLACE % fieldReplace, 1)

        return '' + regexRule


class NoAttributes(Exception):
    pass


if __name__ == '__main__':
    ruta = r"C_Flower1_mesh|C_Flower1_meshShape"
    myPath = Freeway(ruta, pattern=['meshName','instanceMeshName'])
    print(myPath)
    ruta = r"C_Flower1_meshShape"
    myPath = Freeway(ruta, pattern=['meshName','instanceMeshName'])
    print(myPath)
