#!/usr/bin/env python3


"""
ChartyPy3.py

This is a small incremental bottom-up chart parser for context free grammars.

(C) 2005-2011 by Damir Cavar <damir@cavar.me>

This code is written and distributed under the
Lesser GNU General Public License version 3 or newer.

See http://www.gnu.org/copyleft/lesser.html for details
on the license or the the file lgpl-3.0.txt that should always be
distributed with this code.



Used data structures:

chart:
   list of edges

edge:
   list of integers and symbols
   [start, end, dotindex, LHS, RHS]
   start:    integer, start of the edge
   end:      integer, end of the edge
   dotindex: integer, position of the dot in the RHS
   LHS:      string, left-hand side symbol
   RHS:      list of strings, symbols in right-hand side


Properties:
Incremental (left-to-right) bottom-up chart parser.
Select only potentially appropriate rules from grammar
   - length of RHS is less or equal to remaining words/symbols


Processing steps:
   Word by word:
      Initialise chart with word (add edge for word)
      Do until no further improvement:
         Add new rules from grammar that consume inactive edges
         Apply the fundamental rule to induce new edges


Calling via command line:
If ChartyPy3.py is made executable, one can call it:

./ChartyPy3.py -g PSG1.txt -i "John loves Mary"

or start Python with the script otherwise:

python ChartyPy3.py -g PSG1.txt -i "John loves Mary"

Start the script with as:

python ChartyPy3.py -h

for instructions about the parameters.


This code can be opimized. However, its main purpose is to help students understand a simple algorithm for chart parsing. If there are any bugs, please let me know:

Damir Cavar <damir@cavar.me>
"""

__author__  = "Damir Cavar <damir@cavar.me>"
__date__    = "$May 29, 2005 10:36:30 AM$"
__version__ = "0.5"


import sys
from PSGParse3 import PSG
import argparse
import math
DEBUG = False       # set this to 0 if you do not want tracking
QTREE = False


def isActive(edge):
   """Return 1 if edge is active, else return 0."""
   if edge[2] < len(edge[4]): return True
   return False


def isInactive(edge):
   """Return True if edge is active, else returns False."""
   if edge[2] >= len(edge[4]): return True
   return False


def match(aedge, iedge):
   """Returns True if the active edge and the inactive edge match,
      otherwise False.
   """
   if aedge[1] == iedge[0]:
      if aedge[4][aedge[2]] == iedge[3]: return True # scaning
   return False


def getParse(inputlength, chart, grammar):
   """TODO: Returns a list of all parses in bracketing notation."""
   parses = []
   for i in range(len(chart)):
      if not isActive(chart[i]):
         if chart[i][0] == 0 and chart[i][1] == inputlength: # got spanning edge
            print("Successfully parsed!")
            parses.append(struct2Str(chart[i],chart,grammar))
   return parses

def getProb(inputlength, chart, grammar):
   prob = []
   for i in range(len(chart)):
      if not isActive(chart[i]):
         if chart[i][0] == 0 and chart[i][1] == inputlength: # got spanning edge
            prob.append(calculateProb(chart[i],chart,grammar))
   return prob
def calculateProb(edge, chart, grammar):
   prob = 0
   lhs=grammar.id2s(edge[3]) # get the left hand side string
   rhs=grammar.idl2s(edge[4]) # get the right hand side string
   if edge[5] == (): # get the probablity of a terminal, end this DFS
      prob += math.log(float(grammar.possibility[(lhs,rhs)]))
      return prob
   for i in range(len(edge[5])):# DFS the current non-terminal
      prob += math.log(float(grammar.possibility[(lhs,rhs)]))+calculateProb(chart[edge[5][i]],chart,grammar)
   return prob
   pass
def struct2Str(edge, chart, grammar):
   """TODO: Returns a string representation of the parse with
      labled brackets.

      Parameters:
      edges - the list of edges that make a parse
      chart - the current chart (list of edges)
   """
   tmpstr = ""
   if edge[5] == (): # when get a terminal (fpron->'I'), str = fpron['i']
      tmpstr += str(grammar.id2s(edge[3])) + '[' + str(grammar.idl2s(edge[4])[0]) + ']'
      return tmpstr
   tmpstr += str(grammar.id2s(edge[3])) + '[' + struct2Str(chart[edge[5][0]], chart, grammar) # get the left bracket and the begining of the parsing string
   if len(edge[5])>=2: #get
         for i in range(1,len(edge[5])):
            tmpstr +=  struct2Str(chart[edge[5][i]],chart,grammar) # backtrack the children of the current production
   tmpstr += ']'# get the right bracket
   return tmpstr


def edgeStr(edge, grammar):
   """ """
   return str( (edge[0], edge[1], edge[2],
           grammar.id2s(edge[3]),
           grammar.idl2s(edge[4]),
           edge[5]) )


def ruleInvocation(lststart, chart, inputlength, grammar):
   """Add all the rules of the grammar to the chart that
      are relevant:
      Find the rule with the LHS of edge as the leftmost RHS
      symbol and maximally the remaining length of the input.

      Parameters:
      lststart - start position at edge in chart
      chart - the current chart
      inputlength - the length of the input sentence
      grammar - the grammar object returned by PSGParse3
   """
   change = False
   for i in range(lststart, len(chart)):
      if chart[i][2] >= len(chart[i][4]): # only inactive edge
         (start, end, index, lhs, rhs, consumed) = chart[i]
         for k in grammar.rhshash.get(lhs, ()):
            if len(k[1]) > inputlength - start: # scanning upward
               continue
            newedge = ( start, end, 1, k[0], k[1], (i,) )
            if newedge in chart:
               continue
            chart.append(newedge)
            change = True
            if DEBUG:
               print("RI Adding edge:", edgeStr(newedge, grammar))
   return change


def fundamentalRule(chart, grammar):
   """The fundamental rule of chart parsing generates new edges by
      combining fitting active and inactive edges.

      Parameters:
      chart - the current chart
   """
   change = False
   for aedge in chart:
      if isActive(aedge):
         for k in range(len(chart)):
            if isInactive(chart[k]):
               if match(aedge, chart[k]):
                  newedge = (aedge[0], chart[k][1], aedge[2] + 1,
                             aedge[3], aedge[4], tuple(list(aedge[5]) + [ k ]))
                  print('this is fundemantal' + str(newedge))
                  if newedge not in chart:
                     chart.append(newedge)
                     change = True
                     if DEBUG:
                        print("FR Adding edge:", edgeStr(newedge, grammar))
   return change


def parse(inp, grammar):
   """Parse a list of tokens.

      Arguments:
      inp = a list of tokens
      grammar = an object returned by PSGParse3
   """

   chart = []
   inputlength = len(inp)

   chartpos = 0  # remember start-position in chart
   for i in range(inputlength):
      # initialize with input token
      rules = grammar.rhshash.get(grammar.symb2id[inp[i]], ( ("", ()) ) )
      for rule in rules:
         if rule[0]: # non-terminal
            chart.append( ( i, i + 1, 1, rule[0], rule[1], () ) )
      if DEBUG:
         print("Adding edge:", edgeStr(chart[len(chart) - 1], grammar))
      change = 1
      while change:
         change = 0
         chartlen = len(chart)
         i= 0
         if ruleInvocation(chartpos, chart, inputlength, grammar):
            change = 1
         chartpos = chartlen  # set pointer to new edge in chart
         if fundamentalRule(chart, grammar):
            change = 1
   if DEBUG:
      print("Chart:")
      for i in range(len(chart)):
         if isActive(chart[i]):
            print(i, "Active:", end=" ")
         else:
            print(i, "Inactive:", end=" ")
         print(edgeStr(chart[i], grammar))
   if QTREE:
      return getQtreeParse(inputlength, chart, grammar)
   return getParse(inputlength, chart, grammar), getProb(inputlength, chart, grammar)


def printParses(parses, prob):
   """TODO: Prints the parse as brackated string to the screen."""
   print(parses)
   print(prob)

if __name__ == "__main__":
   usage = "usage: %(prog)s [options]"
   parser = argparse.ArgumentParser(prog="ChartyPy", usage=usage,
            description='A chart parser, based on the Earley algorithm.',
            epilog="(C) 2005-2011 by Damir Cavar <damir@cavar.me>")
   parser.add_argument('--version', action='version', version="ChartyPy "+__version__)
   parser.add_argument("-g", "--grammar", dest="grammar", required=True,
            help="name of the file with the context-free grammar")
   parser.add_argument("-i", "--input", dest="sentence", required=True,
            help="input sentence, e.g. \"John kissed Mary\"")
   parser.add_argument("-l", "--latex", dest="latex", action="store_true",
            required=False,
            help="output of parse structure in LaTeX notation for qtree.sty")
   parser.add_argument("-q", "--quiet",
            action="store_false", dest="DEBUG", default=True,
            help="don't print the chart content  [default True]")
   args = parser.parse_args()
   if args:
      DEBUG = args.DEBUG
      QTREE = args.latex
      try:
         mygrammar = PSG(args.grammar) # initialization of the grammar
      except IOError:
         print("Cannot load grammar:, args.grammar")
      else:
         parse,prob = parse(args.sentence.split(), mygrammar)
         printParses(parse,prob)



