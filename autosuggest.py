#!/usr/bin/env python

import pickle
import sys, os

def bigramSuggest(world, word, invert=False):
	""" world format: { word1 : { word2 : count } }
	"""
	ret=[]
	word=word.lower()
	if(word in world):
		items=world[word]
		invertedList={}
		vals=[]
		for item in items.keys():
			vals.append(items[item])
			if (not (items[item] in invertedList)):
				invertedList[items[item]]=[]
			invertedList[items[item]].append(item)
		vals=list(set(vals))
		vals.sort()
		for val in vals:
			ret.extend(invertedList[val])
	if(invert):
		ret.reverse()
	return ret

def corpus2bigrams(text):
	world={}
	chars=",./<>?'\":;`~!@#$%^&*()_+-=\\|[]{}\r\n\t"
	for i in range(0, len(chars)):
		text=text.replace(chars[i], " ")
	lastWord=""
	for w in text.split():
		word=w.lower()
		if(not(lastWord in world)):
			world[lastWord]={}
		if(not(word in world[lastWord])):
			world[lastWord][word]=1
		else:
			world[lastWord][word]+=1
		lastWord=word
	return world

def checkWhiteList(world, word, blacklist=False):
	ret=(word in world)
	if(blacklist): 
		ret=not ret
	return ret

def loadBigrams(filename):
	with open(filename, 'r') as f:
		return pickle.load(f)

def saveBigrams(world, filename):
	with open(filename, 'w') as f:
		return pickle.dump(world, f)


		

