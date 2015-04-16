import sys
import re

__author__ = 'Marc Schulder'

class Token:
    def __init__(self, features, label):
        self.features = features
        self.label = label

    def __str__(self):
        return "{0} -> {1}".format(self.features, self.label)

    def __repr__(self):
        items = self.features+[self.label]
        return items.__repr__()

    def getFeatures(self):
        return self.features

    def getFeature(self, index):
        return self.features[index]

    def getLabel(self):
        return self.label

class Sequence:
    def __init__(self, tokens=None):
        if tokens is None:
            self.tokens = list()
        else:
            self.tokens = tokens

    def __str__(self):
        return self.tokens.__str__()

    def __repr__(self):
        return self.tokens.__repr__()

    def __iter__(self):
        return self.tokens

    def __len__(self):
        return self.tokens.__len__()

    def addToken(self, token):
        self.tokens.append(token)

    def getTokens(self):
        return self.tokens

    def getToken(self, position):
        return self.tokens[position]

    def getFeature(self, tokenIndex, featureIndex):
        return self.tokens[tokenIndex].getFeature(featureIndex)

class Rule:
    ruleRE = re.compile('(.*?)(%x\[.+?,.+?\])+?(.*?)$')
    macroRE = re.compile('%x\[(.+?),(.+?)\]')

    def __init__(self, string):
        self.items = []
        rest = string
        while len(rest) > 0:
            m = self.ruleRE.match(rest)
            if m is None:
                break
            else:
                prefix, rule, rest = m.groups()
                if len(prefix) > 0:
                    self.items.append(RuleString(prefix))
                macro = self.macroRE.match(rule)
                row = macro.group(1)
                col = macro.group(2)
                self.items.append(Macro(row,col))
        if len(rest) > 0:
            self.items.append(RuleString(rest))

    def __str__(self):
        string = ''
        for item in self.items:
            string += item.__str__()
        return string

    def __repr__(self):
        return self.items.__repr__()

    def instantiate(self, position, sequence):
        string = ''
        for item in self.items:
            if item.isMacro():
                featureIndex = item.getCol()
                relativePos = item.getRow()
                itemIndex = position + relativePos
                if itemIndex >= 0 and itemIndex < len(sequence):
                    feature = sequence.getFeature(itemIndex, featureIndex)
                    string += feature
            else:
                string += item.getString()
        return string

class Macro:
    def __init__(self, row, col):
        self.row = int(row)
        self.col = int(col)

    def __str__(self):
        return '%x[{0},{1}]'.format(self.row, self.col)

    def __repr__(self):
        item = (self.row, self.col)
        return item.__repr__()

    def getRow(self):
        return self.row

    def getCol(self):
        return  self.col

    def isMacro(self):
        return True

class RuleString():
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string

    def getString(self):
        return self.string

    def isMacro(self):
        return False

def loadCRFppData(dataFile):
    sequences = list()
    sequence = None
    with open(dataFile) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                # Start of new sequence
                sequence = None
            else:
                # Check if new sequence has started
                if sequence is None:
                    sequence = Sequence()
                    sequences.append(sequence)
                # Add token
                items = line.split()
                token = Token(items[:-1], items[-1])
                sequence.addToken(token)
    return sequences

def loadCRFppTemplate(templateFile):
    rules = list()
    with open(templateFile) as f:
        for line in f:
            line = line.strip()
            if len(line) > 0 and not line.startswith('#'):
                rule = Rule(line)
                rules.append(rule)
    return rules


def convertPP2Suite(inputDataFile, templateFile, outputDataFile):
    sequences = loadCRFppData(inputDataFile)
    rules = loadCRFppTemplate(templateFile)
    for sequence in sequences:
        #print 'Seq', sequence
        for rule in rules:
            #print ' rule:', rule
            for position in range(len(sequence)):
                #print '  pos:', position, sequence.getToken(position)
                string = rule.instantiate(position, sequence)
                #print '  out:', string


def main(args):
    if len(args) != 4:
        print 'USAGE: python crfpp2suite.py INPUT_DATA TEMPLATE OUTPUT_DATA'
    else:
        inputDataFile = args[1]
        templateFile = args[2]
        outputDataFile = args[3]
        convertPP2Suite(inputDataFile, templateFile, outputDataFile)


if __name__ == '__main__':
    main(sys.argv)