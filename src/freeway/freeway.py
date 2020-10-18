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
    
    print("Loading JSON file: %s" % filename)
    
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
        
        if not rules:
            jsonData = loadRulesFromFile(rulesfile)
            rules = jsonData.get('rules', None)
  
            if not convertionTable:
                convertionTable = jsonData.get('convertionTable', None)

        self._rules = OrderedDict(Freeway.get_rules(rules))
        self._convertionTable = convertionTable

        for key, value in kwargs.items():
            setattr(self, key, value)

        if filepath:
            self._filepath = filepath.replace('\\', '/')
        
        self.pattern = pattern

    def __str__(self):
        return '%s: %s' % (self.pattern, str(self.data))

    def __repr__(self):
        return str(self)

    def info_from_path(self, firstMatch=True):
        """
        Parse a path with pattern rules.
        """
        patterns = list(self._rules.keys()) if self._pattern == ["auto"] else self._pattern

        self._pattern = []

        for pattern in patterns:
            data = self.resolve_pattern(pattern)
            if data:
                yield data
                self._pattern.append(pattern)
                if firstMatch:
                    break

    def ensureCompiledRegex(self, pattern):
        for rule in self._rules.get(pattern):
            if not rule.compiled:
                rules = list(self.expandRules(pattern))
                self._rules[pattern] = rules
        
    def resolve_pattern(self, pattern):
        resolved = {}

        self.ensureCompiledRegex(pattern)
                
        for rule in self._rules.get(pattern):
            match = rule.compiled.match(self._filepath)

            if match:
                resolved.update({pattern: value for pattern, value in match.groupdict(
                ).items() if not pattern.endswith('_')})

        return resolved

    @property
    def match(self):
        """
        Check if it can build a complete path
        """
        patterns = {}
        fullMatch = False
        for pattern in self.pattern:
            for rule in self.expandRules(pattern):
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

    def _parsePath(self):
        if self._filepath:
            for find in self.info_from_path():
                for key, value in find.items():
                    setattr(self, key, value)
                    
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
        self._parsePath()
        
    @property
    def filepath(self):
        """
        Current filepath in use.
        """
        return self._filepath
    
    @filepath.setter
    def filepath(self, value):
        """
        Setting a filepath and parse new fields.
        """
        self._filepath = value
        self._parsePath()
        
    @property
    def data(self):
        """
        Return all parsed data inside Freeway object.
        """
        
        elements = self.__dict__.copy()
        for attr in ['pattern', '_pattern',
                     'filepath', '_filepath', '_rules',
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

    def expandRules(self, attr):
        """
        Evaluate recursively a pattern rule and return a full regex
        """
        rules = self._rules.copy()
        self._rules["_ignoreMissing"] = True
        
        for rule in rules.get(attr, []):
            rule = RuleParser(attr, str(rule))
            while set(rules) & set(rule.fields):
                for field in rule.fields:
                    if field in rules:
                        rule.rule = rule.rule.replace('{%s}' % field,
                                                      rules.get(field, field)[0].rule)
            rule.compile(re.IGNORECASE)
            yield rule

        self._rules["_ignoreMissing"] = False

    def __getattribute__(self, attr):
        ignoreMissing = object.__getattribute__(
            self, '_rules').get("_ignoreMissing")
        rules = object.__getattribute__(self, '_rules').get(attr)

        if rules:
            for rule in rules:
                try:
                    data = {field: getattr(self, field, None) for field in rule.fields}
                    missing = [k for k, v in data.items() if v is None]
                    if missing:
                        raise AttributeError

                    name = rule.rule.format(**data)

                except AttributeError:
                    if not ignoreMissing:
                        raise Exception("Can't find [%s] attribute(s)." % ', '.join(missing))

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

    def copy(self):
        return Freeway(self.filepath, pattern=self.pattern, rules=self._rules,
                       convertionTable=self._convertionTable, **self.data)

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
        self.compiled = None

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
        if "_regex" in self.__dict__:
            return self._regex

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

        self._regex = "^%s$" % regexRule
        return self._regex
    
    def compile(self, flag):
        self.compiled = re.compile(self.regex, flag)
