#!/usr/bin/env python

from autosuggest import *
import os, sys
from sys import argv, exit

def printUsage():
	print("Usage: constraintWriterTool action [options]\nActions:\n\tsuggest\t\tbigramfile word\n\tsuggestPfx\tbigramfile word prefix\n\tinWhitelist\tbigramfile word\n\tinBlacklist\tbigramfile word\n\tcompile\t\tcorpus bigramfile\n\tcompileMulti\tbigramfile corpus [corpus_2 ... corpus_n]\n\tcombine\t\tbigramfile_out [bigramfile_in ... ]\n")
	exit(1)

if len(argv)<4:
	printUsage()

world={}
if argv[1] in ["suggest", "suggestPfx", "inWhitelist", "inBlacklist"]:
	def inBlacklist(world, word):
		return checkWhiteList(world, word, True)
	def pfx(world, word):
		return bigramSuggestPfx(world, word, argv[4])
	funcs={"suggest":bigramSuggest, "inWhitelist":checkWhiteList, "inBlacklist":inBlacklist, "suggestPfx":pfx}
	world=loadBigrams(argv[2])
	print(funcs[argv[1]](world, argv[3]))
	exit(0)
elif argv[1]=="compile":
	with open(argv[2], 'r') as f:
		saveBigrams(corpus2bigrams(f.read()), argv[3])

elif argv[1]=="compileMulti":
	corpora=[]
	for fname in argv[3:]:
		with open(fname, 'r') as f:
			corpora.append(f.read())
	saveBigrams(corpus2bigrams("\n".join(corpora)), argv[2])
elif argv[1]=="combine":
	bigrams={}
	for fname in argv[3:]:
		world=loadBigrams(fname)
		for w1 in world.keys():
			if not (w1 in bigrams):
				bigrams[w1]={}
			for w2 in world[w1].keys():
				if not w2 in bigrams[w1]:
					bigrams[w1][w2]=0
				bigrams[w1][w2]+=world[w1][w2]
	saveBigrams(bigrams, argv[2])

				
	
