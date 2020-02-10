# Author: Leandro Inocencio aka Cesio (cesio.arg@gmail.com)

import os
import re
import json
from collections import OrderedDict


_PLACEHOLDER_REGEX = re.compile('{(.+?)}')
_FIELDPATTERN_REGEX = re.compile('({.+?})')
_FIELDREPLACE = r'(?P<%s>[:a-zA-Z0-9_-]*)'


def loadRulesFromFile(filename):
    print("Loading JSON file:", filename)

    with open(filename, 'r') as jsonf:
        jsonData = json.loads(jsonf.read())
        return jsonData


rulesfile = os.environ.get('RULESFILE', None)

if rulesfile and os.path.exists(rulesfile):
    jsonData = loadRulesFromFile(rulesfile)
    rules = jsonData['rules']
    convertionTable = jsonData['convertionTable']
else:
    rules = {}
    convertionTable = {}


class Freeway(object):
    def __init__(self, filepath=None, pattern=['auto'], rules=rules,
                 convertionTable=convertionTable, rulesfile=None, **kwargs):

        

        if rulesfile:
            self._rulesfile = rulesfile
            jsonData = loadRulesFromFile(rulesfile)
            self._rules = OrderedDict(Freeway.get_rules(jsonData['rules']))
            self._convertionTable = jsonData['convertionTable']
        else:
            self._rules = OrderedDict(Freeway.get_rules(rules))
            self._convertionTable = convertionTable

        if filepath:
            self._filepath = filepath.replace('\\', '/')
            self.pattern = pattern

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '%s: %s' % (self.pattern, str(self.data))

    def __repr__(self):
        return str(self)

    def parseFilepath(self, filepath, patterns=['auto']):
        if filepath:
            for key, value in Freeway.info_from_path(filepath,
                                                     self._rules,
                                                     self.pattern).items():
                setattr(self, key, value)

    @staticmethod
    def info_from_path(path, rules, patterns=['auto']):
        assert isinstance(path, str), 'Path isnt str type'
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
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = [value] if isinstance(value, str) else value
        self.parseFilepath(self._filepath, self._pattern)

    @property
    def data(self):
        elements = self.__dict__.copy()
        for attr in ['pattern', '_filepath', '_rules',
                     '_convertionTable', '_rulesfile']:
            elements.pop(attr, None)
 
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
            rule = RuleParser(attr, str(rule))
            field = rule

            while set(rules._rules) & set(rule.fields):
                for field in rule.fields:
                    if field in rules:
                        rule.rule = rule.rule.replace('{%s}' % field,
                                                    rules.get(field, field))

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
                raise AttributeError('No se ha encontrado el atributo: %s' % ', '.join(missing))

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
        return any(filter(lambda x: x == item, self._rules))

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
        notRemove = ['pattern', '_rules', '_convertionTable', '_rulesfile']
        for key in set(self.__dict__) ^ set(notRemove):
            self.__dict__.pop(key, None)


class RuleParser(object):
    def __init__(self, name, rule):
        self.name = name
        self.rule = str(rule)

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


if __name__ == '__main__':
    ruta = r"C_Flower1_meshShape"
    myPath = Freeway(ruta, pattern=['meshName','instanceMeshName'])
    print(myPath)
    myPath.clean()
    print(myPath)
