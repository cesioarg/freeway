"""
.. module:: Freeway
   :platform: Unix, Windows
   :synopsis: Freeway is a module for managing file system structures with recursive pattern rules.

.. moduleauthor:: Leandro Inocencio <cesio.arg@gmail.com>

"""

import os
import re
import json
from collections import OrderedDict
from .versioner import Version

_PLACEHOLDER_REGEX = re.compile('{(.+?)}')
_FIELDPATTERN_REGEX = re.compile('({.+?})')
_FIELDREPLACE = r'(?P<%s>[:a-zA-Z0-9_-]*)'

# Cached rules, avoid reading the disc a lot
global jsonData
jsonData = None


def loadRulesFromFile(filename):
    """
    Load pattern rules that structure the pipeline.
    """
    global jsonData
    
    if jsonData:
        # load jsonData from global, reduce disk usage
        return jsonData
    
    print("Loading JSON file:", filename)
    
    with open(filename, 'r') as jsonf:
        jsonData = json.loads(jsonf.read())
        return jsonData


class Freeway(object):
    """
    Freeway main class
    """
    
    def __init__(self, filepath=None, pattern=['auto'], rules=None,
                 convertionTable=None, rulesfile=None, **kwargs):

        if not rulesfile:
            # Load rules from enviroment
            rulesfile = os.environ.get('RULESFILE', None)
            assert rulesfile and os.path.exists(rulesfile), \
                "No RULESFILE env variable was detected."

        self._rulesfile = rulesfile
        jsonData = loadRulesFromFile(rulesfile)
        self._rules = OrderedDict(Freeway.get_rules(jsonData['rules']))
        self._convertionTable = jsonData['convertionTable']

        for key, value in kwargs.items():
            setattr(self, key, value)

        if filepath:
            self._filepath = filepath.replace('\\', '/')
            self.pattern = pattern

    def __str__(self):
        return '%s: %s' % (self.pattern, str(self.data))

    def __repr__(self):
        return str(self)

    @staticmethod
    def info_from_path(path, rules, patterns=['auto']):
        """
        Parse a path with pattern rules.
        """
        assert isinstance(path, str), 'Path isnt str type'
        for pattern in patterns:
            if pattern == 'auto':
                for key in rules:
                    for item in Freeway.expandRules(key, Freeway(rules=rules)):
                        match = re.match(item.regex, path, re.IGNORECASE)
                        if match:
                            for data in Freeway.info_from_path(path,
                                                               rules,
                                                               [item.name]):
                                yield data
            else:
                for item in Freeway.expandRules(pattern, Freeway(rules=rules)):
                    match = re.match(item.regex, path, re.IGNORECASE)
                    if match:
                        info = {pattern: value for pattern, value in match.groupdict(
                        ).items() if not pattern.endswith('_')}
                        yield info

    @property
    def match(self):
        """
        Check if it can build a complete path
        """
        patterns = {}
        fullMatch = False
        for pattern in self.pattern:
            for rule in Freeway.expandRules(pattern, Freeway(rules=self._rules)):
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
        """
        Current pattern in use.
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        """
        Setting a pattern and parse new fields.
        """
        self._pattern = [value] if isinstance(value, str) else value
        if self._filepath:
            for find in Freeway.info_from_path(self._filepath,
                                               self._rules,
                                               self._pattern):
                for key, value in find.items():
                    setattr(self, key, value)

    @property
    def data(self):
        """
        Return all parsed data inside Freeway object.
        """
        
        elements = self.__dict__.copy()
        for attr in ['pattern', '_pattern', '_filepath', '_rules',
                     '_convertionTable', '_rulesfile']:
            elements.pop(attr, None)

        return elements

    @staticmethod
    def get_rules(allrules):
        """
        Transform JSON pattern rules into RuleParser objects with name
        """
        for name, rules in allrules.items():
            if not name.startswith('_'):
                yield name, [RuleParser(name, rule) for rule in rules]

    @staticmethod
    def expandRules(attr, rules):
        """
        Evaluate recursively a pattern rule and return a full regex
        """
        rules._rules["_ignoreMissing"] = True

        for rule in rules._rules.get(attr, []):
            rule = RuleParser(attr, str(rule))
            while set(rules._rules) & set(rule.fields):
                for field in rule.fields:
                    if field in rules:
                        rule.rule = rule.rule.replace('{%s}' % field,
                                                      rules.get(field, field))

            yield rule

        rules._rules["_ignoreMissing"] = False

    def __getattribute__(self, attr):
        ignoreMissing = object.__getattribute__(
            self, '_rules').get("_ignoreMissing")
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
                raise AttributeError(
                    'No se ha encontrado el atributo: %s' % ', '.join(missing))

            return name
        else:
            try:
                return object.__getattribute__(self, attr)
            except Exception:
                switchs = object.__getattribute__(
                    self, '_convertionTable') or {}

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
        for key, rule in self._rules.items():
            if key == item:
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

    def version(self, attr):
        return Version(self.attr)


class RuleParser(object):
    """
    Extract fields from pattern rules
    """
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

        elif isinstance(item, str):
            for field in self.fields:
                if field == item:
                    return index
                index += 1

    def __str__(self):
        return self.rule

    def __repr__(self):
        return str(self)

    def __contains__(self, item):
        if isinstance(item, str):
            for field in self.fields:
                if field == item:
                    return True

    @property
    def lenFields(self):
        return len(list(self.fields))

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

            regexRule = regexRule.replace(
                field, _FIELDREPLACE % fieldReplace, 1)

        return '' + regexRule


if __name__ == '__main__':
    # "assetFile": ["{project}_{assetType}_{asset}_{task}_v.{version}.{ext}"]
    
    ruta = r"example_Character_Vidi_MOD_v001.ma"
    path = r"C:/example/assets/Character/Vidi/work/example_Character_Vidi_MOD_v001.ma"
    myPath = Freeway(path)
    print(myPath)
    
    print(myPath.assetPath)
