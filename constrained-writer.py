#!/usr/bin/env python
# -*- coding: utf-8

try:
	from Tkinter import *
	import tkFileDialog
except:
	from tkinter import *
	from tkinter import filedialog
	tkFileDialog=filedialog

from autosuggest import *

has_nltk=False
try:
	import nltk
	try:
		from nltk.corpus import wordnet
	except:
		nltk.download("wordnet")
	try:
		from nltk.corpus import cmudict
	except:
		nltk.download("cmudict")
	from word_transformations import *
	import re
	has_nltk=True
except:
	print("We don't have NLTK or can't download some corpora.")


import sys, math

top=Tk()

global whitelist, blacklist, autocorrect_corpus, invert_suggestions, suggestions, current_suggestion, fname, random

from random import Random
random=Random()

fname=""
whitelist=None
blacklist=None
autocorrect_corpus=None
invert_suggestions=IntVar()
suggestions=[]
current_suggestion=0

chars=",./<>?'\":;`~!@#$%^&*()_+-=\\|[]{}\r\n\t"

START="0.0"

top.wm_title("Constrained Writer")
cmdBarFrame=Frame(top)
corpusFrame=Frame(top)
editFrame=Frame(top)

openButton=Button(cmdBarFrame, text="Open")
saveButton=Button(cmdBarFrame, text="Save")
speakButton=Button(cmdBarFrame, text="Speak")
stfuButton=Button(cmdBarFrame, text="STFU")
exitButton=Button(cmdBarFrame, text="Exit")
activityLabel=Label(cmdBarFrame, text="")

whitelistFrame=Frame(corpusFrame)
whitelistLabel=Label(whitelistFrame, text="Whitelist: none")
whitelistButton=Button(whitelistFrame, text="Set Whitelist")
blacklistFrame=Frame(corpusFrame)
blacklistLabel=Label(blacklistFrame, text="Blacklist: none")
blacklistButton=Button(blacklistFrame, text="Set Blacklist")
acFrame=Frame(corpusFrame)
corpusLabel=Label(acFrame, text="Corpus: none")
corpusButton=Button(acFrame, text="Set autocorrect corpus")
invertLabel=Label(acFrame, text="Invert:")
invertCheckbox=Checkbutton(acFrame, variable=invert_suggestions)
sPlusButton=Button(acFrame, text="S++")

if(has_nltk):
	mutateBarFrame=Frame(top)
	synonymButton=Button(mutateBarFrame, text="Synonymize")
	antonymButton=Button(mutateBarFrame, text="Antonymize")
	hypernymButton=Button(mutateBarFrame, text="Hypernymize")
	hyponymButton=Button(mutateBarFrame, text="Hyponymize")
	rhymeButton=Button(mutateBarFrame, text="Rhyme")


openButton.pack(side=LEFT)
saveButton.pack(side=LEFT)
speakButton.pack(side=LEFT)
stfuButton.pack(side=LEFT)
exitButton.pack(side=LEFT)
activityLabel.pack(side=LEFT)

whitelistLabel.pack(side=LEFT)
whitelistButton.pack(side=LEFT)
blacklistLabel.pack(side=LEFT)
blacklistButton.pack(side=LEFT)
corpusLabel.pack(side=LEFT)
corpusButton.pack(side=LEFT)
invertLabel.pack(side=LEFT)
invertCheckbox.pack(side=LEFT)
sPlusButton.pack(side=LEFT)

editBox=Text(editFrame)
suggestionBox=Text(editFrame, width=20)
editBox.pack(side=LEFT, fill=BOTH, expand=True)
suggestionBox.pack(fill=Y, expand=True)

cmdBarFrame.pack(side=TOP, fill=X)
whitelistFrame.pack(side=TOP, fill=X)
blacklistFrame.pack(side=TOP, fill=X)
acFrame.pack(side=TOP, fill=X)
corpusFrame.pack(side=TOP, fill=X)
if(has_nltk):
	synonymButton.pack(side=LEFT)
	antonymButton.pack(side=LEFT)
	hypernymButton.pack(side=LEFT)
	hyponymButton.pack(side=LEFT)
	rhymeButton.pack(side=LEFT)
	mutateBarFrame.pack(side=TOP, fill=X)
editFrame.pack(side=BOTTOM, fill=BOTH,  expand=True)

global busyLevel
busyLevel=1
def busy(isBusy=True):
	global busyLevel
	msg="Working.."+("."*busyLevel)
	if(not isBusy):
		msg=""
	else:
		busyLevel+=1
		if(busyLevel>3): busyLevel=1
	activityLabel.configure(text=msg)
	top.update_idletasks()
def handleStfu(*args):
	(stdin, stdout)=os.popen2("killall flite")
	stdin.close()
def handleSpeak(*args):
	text=editBox.get(START, END)
	(stdin, stdout)=os.popen2("flite")
	stdin.write(text)
	stdin.write("\n")
	stdin.close()
	

def handleExit(*args):
	sys.exit(0)

def handleOpen(*args):
	global fname
	name=tkFileDialog.askopenfilename(filetypes=[('text', '.txt')])
	if(name):
		if(name!=fname):
			with open(name, 'r') as f:
				fname=name
				try:
					editBox.delete(START, END)
				except:
					pass
				editBox.insert(START, f.read())
				top.wm_title("Constrained Writer: "+fname)
				editBox.mark_set("matchStart", START)
				editBox.mark_set("matchEnd", START)
			handleKeyActivity()

def handlePickWhitelist(*args):
	global whitelist
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		whitelist=loadBigrams(name)
		name=name[:-8]
		if(len(name)>100):
			name="..."+name[-97:]
		whitelistLabel.configure(text="Whitelist: "+name)
		handleKeyActivity()

def handlePickBlacklist(*args):
	global blacklist
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		blacklist=loadBigrams(name)
		name=name[:-8]
		if(len(name)>100):
			name="..."+name[-97:]
		blacklistLabel.configure(text="Blacklist: "+name)
		handleKeyActivity()

def handlePickCorpus(*args):
	global autocorrect_corpus
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		autocorrect_corpus=loadBigrams(name)
		name=name[:-8]
		if(len(name)>100):
			name="..."+name[-97:]
		corpusLabel.configure(text="Corpus: "+name)
		handleKeyActivity()

def handleSave(*args):
	global fname
	name=tkFileDialog.asksaveasfilename(initialfile=fname, filetypes=[('text', '.txt')])
	if(name):
		if(name!=fname):
			with open(name, 'w') as f:
				fname=name
				f.write(editBox.get(START, END))
				top.wm_title("Constrained Writer: "+fname)


openButton.configure(command=handleOpen)
saveButton.configure(command=handleSave)
speakButton.configure(command=handleSpeak)
stfuButton.configure(command=handleStfu)
exitButton.configure(command=handleExit)
whitelistButton.configure(command=handlePickWhitelist)
blacklistButton.configure(command=handlePickBlacklist)
corpusButton.configure(command=handlePickCorpus)
def handleMutate(fn):
	busy()
	if(whitelist):
		old_fn=fn
		def wrap_wl(word):
			ret=old_fn(word)
			if(ret.lower() in whitelist):
				return ret
			return word
		fn=wrap_wl
	if(blacklist):
		old_fn_2=fn
		def wrap_bl(word):
			ret=old_fn_2(word)
			if(ret.lower() in blacklist):
				return word
			return ret
	editBuf=editBox.get(START, END)
	currLine=1
	for line in editBuf.split("\n"):
		newLine=""
		for word in re.split(r'([A-Za-z0-9]+|[^A-Za-z0-9]+)', line):
			newLine+=fn(word)
			busy()
		editBox.delete(str(currLine)+".0", str(currLine)+".end")
		editBox.insert(str(currLine)+".0", newLine)
		editBox.mark_set("matchStart", str(currLine)+".0")
		editBox.mark_set("matchEnd", str(currLine)+".0")
		handleKeyActivity()
		currLine+=1
		top.update_idletasks()
		busy()
	busy(False)
if(has_nltk):
	def handleMutateSyn(*arg, **kw_args): handleMutate(randomSyn)	
	def handleMutateAnt(*arg, **kw_args): handleMutate(randomAnt)	
	def handleMutateHyper(*arg, **kw_args): handleMutate(randomHyper)	
	def handleMutateHypo(*arg, **kw_args): handleMutate(randomHypo)	
	def handleMutateRhyme(*arg, **kw_args): handleMutate(randomRhyme)	
	synonymButton.configure(command=handleMutateSyn)
	antonymButton.configure(command=handleMutateAnt)
	hypernymButton.configure(command=handleMutateHyper)
	hyponymButton.configure(command=handleMutateHypo)
	rhymeButton.configure(command=handleMutateRhyme)
def handleMutateSPlus(*arg, **kw_args):
	def randomSPlus(word):
		if(word.isalpha() and len(word)>0 and autocorrect_corpus):
			ret=bigramSuggest(autocorrect_corpus, word, invert_suggestions.get()>0)
			ret2=[]
			for i in range(0, len(ret)) :
				ret2.extend([ret[i]]*int(math.ceil(math.log(len(ret)-i+2))))
			if(len(ret2)>0):
				return random.choice(ret)
		return word
	handleMutate(randomSPlus)
sPlusButton.configure(command=handleMutateSPlus)
if(len(sys.argv)>1):
	with open(sys.argv[1], 'r') as f:
		fname=sys.argv[1]
		editBox.insert(START, f.read())
		top.wm_title("Constrained Writer: "+fname)
	

def handleSuggest(words, partial):
	global autocorrect_corpus, suggestions, current_suggestion
	if(autocorrect_corpus):
		lastWords=words[-2:]
		suggestions=[]
		if(partial):
			suggestions=bigramSuggestPfx(autocorrect_corpus, lastWords[0], lastWords[1], invert_suggestions.get()>0)
		else:
			suggestions=bigramSuggest(autocorrect_corpus, lastWords[1], invert_suggestions.get()>0)
		if(current_suggestion>=len(suggestions)):
			current_suggestion=len(suggestions)-1
			if(current_suggestion<0):
				current_suggestion=0
		suggestionBox.delete(START, END)
		suggestionBox.tag_configure("sug"+str(current_suggestion), background="#aaaaff", foreground="#000000")
		i=0
		for w in suggestions:
			before=suggestionBox.index(CURRENT)
			suggestionBox.insert(CURRENT, w)
			after=suggestionBox.index(CURRENT)
			suggestionBox.insert(CURRENT, "\n")
			suggestionBox.tag_add("sug"+str(i), before, after)
			i+=1


editBox.tag_configure("inBlacklist", background="#ffaaaa")
editBox.tag_configure("notInWhitelist", background="#aaffaa")
editBox.mark_set("matchStart", START)
editBox.mark_set("matchEnd", START)

def handleCheckWhitelist(words, partial):
	if(whitelist):
		for w in words[:-1]:
			if(not checkWhiteList(whitelist, w)):
				start=START
				editBox.mark_set("searchLimit", END)
				count=IntVar()
				while True:
					index=editBox.search(w, "matchEnd", "searchLimit", count=count, nocase=True)
					if(index==""): break
					if(count.get()==0): break
					editBox.mark_set("matchStart", index)
					editBox.mark_set("matchEnd", str(index)+"+"+str(count.get())+"c")
					editBox.tag_add("notInWhitelist","matchStart", "matchEnd")

def handleCheckBlacklist(words, partial):
	if(blacklist):
		for w in words[:-1]:
			if(checkWhiteList(blacklist, w)):
				start=START
				editBox.mark_set("searchLimit", END)
				count=IntVar()
				while True:
					index=editBox.search(w, "matchEnd", "searchLimit", count=count, nocase=True)
					if(index==""): break
					if(count.get()==0): break
					editBox.mark_set("matchStart", index)
					editBox.mark_set("matchEnd", str(index)+"+"+str(count.get())+"c")
					editBox.tag_add("inBlacklist","matchStart", "matchEnd")

def handleKeyActivity(*args):
	busy()
	text=editBox.get(START, END)
	if(args):
		text+=args[0].char
	for i in range(0, len(chars)):
		text=text.replace(chars[i], " ")
	words=["", "", ""];
	words.extend(text.split())
	partial=text[-1]!=" "
	stride=len(words[-1])+len(words[-2])+4
	if(partial and args and len(words[-1])>1):
		words[-2]+=words[-1]
		words=words[:-1]
	handleSuggest(words, partial)
	matchStart=editBox.index("matchStart")+"-"+str(stride)+"c"
	matchEnd=editBox.index("matchEnd")+"-"+str(stride)+"c"
	editBox.mark_set("matchStart", matchStart)
	editBox.mark_set("matchEnd", matchEnd)
	handleCheckWhitelist(words, partial)
	editBox.mark_set("matchStart", matchStart)
	editBox.mark_set("matchEnd", matchEnd)
	handleCheckBlacklist(words, partial)
	busy(False)

def handleAcceptSuggestion(*args):
	handleKeyActivity()
	if(len(suggestions) > 0):
		text=editBox.get(START, END)
		if(args):
			text+=args[0].char
		if(not (text[-1] in ["", " ", "\n", "\t", "\r"])):
			wl=len(text)-text.rfind(" ")
			editBox.delete(END+"-"+str(wl-1)+"c", END)
			editBox.insert(END, " ")
		editBox.insert(END, suggestions[current_suggestion]+" ")
		handleKeyActivity()
		return "break"
		
def handleSuggestionNext(*args):
	global suggestions, current_suggestion
	suggestionBox.tag_configure("sug"+str(current_suggestion), background="#ffffff")
	current_suggestion+=1
	if(current_suggestion>=len(suggestions)):
		current_suggestion=0
	suggestionBox.tag_configure("sug"+str(current_suggestion), background="#aaaaff")
	return "break"
def handleSuggestionPrev(*args):
	global suggestions, current_suggestion
	suggestionBox.tag_configure("sug"+str(current_suggestion), background="#ffffff")
	current_suggestion-=1
	if(current_suggestion<0):
		current_suggestion=len(suggestions)-1
		if(current_suggestion<0):
			current_suggestion=0
	suggestionBox.tag_configure("sug"+str(current_suggestion), background="#aaaaff")
	return "break"

editBox.bind("<Key>", handleKeyActivity)
editBox.bind("<Control-Return>", handleAcceptSuggestion)
editBox.bind("<Control-Up>", handleSuggestionPrev)
editBox.bind("<Control-Down>", handleSuggestionNext)

top.mainloop()

