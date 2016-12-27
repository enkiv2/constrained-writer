#!/usr/bin/env python

import sys

global rules, random

import re
import json
from random import Random
random=Random()

rules={}

tag=re.compile("#[^# ]*#")

def expandTag(match):
	tname=match.string[match.pos+1:match.end()-1]
	if(tname in rules):
		rule=rules[tname]
		return random.choice(rule)
	return tname

def performExpansion(line):
	return tag.sub(expandTag, line)

def expandAll(line, ttl=9999):
	while(None!=tag.search(line) and ttl>0):
		ttl-=1
		line=expandForth(performExpansion(line))
		#print("Iter: "+line)
	return line

def addRule(name, opt):
	global rules
	rules[name]=opt

def mergeRule(name, opt):
	global rules
	if(name in rules):
		opt2=opt.extend(rules[name])
		rules[name]=opt2
	else:
		rules[name]=opt

def loadMergeRules(fname):
	global rules
	with open(fname, "r") as f:
		rules2=json.load(f)
		for rule in rules2:
			mergeRule(rule, rules2[rule])

def loadRules(fname):
	global rules
	with open(fname, "r") as f:
		rules=json.load(f)


def expandForth(line):
	return line
try:
	import templateScripting as forth
	forthSym=re.compile("$[a-zA-Z0-9]*")
	forthSubst=re.compile("$$[^$]*$")
	def evalWrap(match):
		line=match.string[match.pos:match.end()]
		if line[0]!="$":
			return line
		sys.stderr.write("Line: "+line+"\n")
		sys.stderr.flush()
		if(line[1]=="$"):
			line=line[2:-1]
		else:
			line=line[1:]
		ret=forth.evaluate(line)
		if(ret==None):
			ret=" ".join(forth.getStack())
		ret=" ".join(forth.getStack())
		return ret
	def expandForth(line):
		if(line.find("$")>=0):
			return line
		return forthSym.sub(evalWrap, forthSubst.sub(evalWrap, line))
except:
	sys.sterr.write("Could not import templateScripting\n")
	sys.stderr.flush()


def main():
	loadRules(sys.argv[1])
	print(expandAll("#origin#"))

if __name__=="__main__":
	main()

