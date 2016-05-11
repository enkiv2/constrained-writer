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

import sys

top=Tk()

global whitelist, blacklist, autocorrect_corpus, invert_suggestions, suggestions, fname

fname=""
whitelist=None
blacklist=None
autocorrect_corpus=None
invert_suggestions=IntVar()
suggestions=[]

chars=",./<>?'\":;`~!@#$%^&*()_+-=\\|[]{}\r\n\t"

START="0.0"

top.wm_title("Constrained Writer")
cmdBarFrame=Frame(top)
editFrame=Frame(top)

openButton=Button(cmdBarFrame, text="Open")
saveButton=Button(cmdBarFrame, text="Save")
whitelistLabel=Label(cmdBarFrame, text="Whitelist: none")
whitelistButton=Button(cmdBarFrame, text="Set Whitelist")
blacklistLabel=Label(cmdBarFrame, text="Blacklist: none")
blacklistButton=Button(cmdBarFrame, text="Set Blacklist")
corpusLabel=Label(cmdBarFrame, text="Corpus: none")
corpusButton=Button(cmdBarFrame, text="Set autocorrect corpus")
invertLabel=Label(cmdBarFrame, text="Invert:")
invertCheckbox=Checkbutton(cmdBarFrame, variable=invert_suggestions)
exitButton=Button(cmdBarFrame, text="Exit")
openButton.pack(side=LEFT)
saveButton.pack(side=LEFT)
whitelistLabel.pack(side=LEFT)
whitelistButton.pack(side=LEFT)
blacklistLabel.pack(side=LEFT)
blacklistButton.pack(side=LEFT)
corpusLabel.pack(side=LEFT)
corpusButton.pack(side=LEFT)
invertLabel.pack(side=LEFT)
invertCheckbox.pack(side=LEFT)
exitButton.pack(side=LEFT)

editBox=Text(editFrame)
suggestionBox=Text(editFrame, width=20)
editBox.pack(side=LEFT, fill=BOTH, expand=True)
suggestionBox.pack()

cmdBarFrame.pack(side=TOP)
editFrame.pack(side=BOTTOM, fill=BOTH,  expand=True)

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

def handlePickWhitelist(*args):
	global whitelist
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		whitelist=loadBigrams(name)
		name=name[:-8]
		if(len(name)>10):
			name="..."+name[-7:]
		whitelistLabel.configure(text="Whitelist: "+name)
		handleKeyActivity()

def handlePickBlacklist(*args):
	global blacklist
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		blacklist=loadBigrams(name)
		name=name[:-8]
		if(len(name)>10):
			name="..."+name[-7:]
		blacklistLabel.configure(text="Blacklist: "+name)
		handleKeyActivity()

def handlePickCorpus(*args):
	global autocorrect_corpus
	name=tkFileDialog.askopenfilename(filetypes=[('Pickled bigram model', '.bigrams')])
	if(name):
		autocorrect_corpus=loadBigrams(name)
		name=name[:-8]
		if(len(name)>10):
			name="..."+name[-7:]
		corpusLabel.configure(text="Corpus: "+name)

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
exitButton.configure(command=handleExit)
whitelistButton.configure(command=handlePickWhitelist)
blacklistButton.configure(command=handlePickBlacklist)
corpusButton.configure(command=handlePickCorpus)

if(len(sys.argv)>1):
	with open(sys.argv[1], 'r') as f:
		fname=sys.argv[1]
		editBox.insert(START, f.read())
		top.wm_title("Constrained Writer: "+fname)
	

def handleSuggest(words, partial):
	global autocorrect_corpus, suggestions
	if(autocorrect_corpus):
		lastWords=words[-2:]
		suggestions=[]
		print("Partial: ", partial)
		if(partial):
			print("pfx:", lastWords[1])
			suggestions=bigramSuggestPfx(autocorrect_corpus, lastWords[0], lastWords[1], invert_suggestions.get()>0)
		else:
			suggestions=bigramSuggest(autocorrect_corpus, lastWords[1], invert_suggestions.get()>0)
		suggestionBox.delete(START, END)
		for w in suggestions:
			suggestionBox.insert(END, w+"\n")


editBox.tag_configure("inBlacklist", background="#ff0000", foreground="#ffffff")
editBox.tag_configure("notInWhitelist", background="#00ff00", foreground="#ffffff")
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
	text=editBox.get(START, END)
	if(args):
		text+=args[0].char
	for i in range(0, len(chars)):
		text=text.replace(chars[i], " ")
	words=["", "", ""];
	words.extend(text.split())
	partial=text[-1]!=" "
	stride=len(words[-1])+len(words[-2])+4
	if(partial and args):
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
		editBox.insert(END, suggestions[0]+" ")
		handleKeyActivity()
		return "break"
		
		

editBox.bind("<Key>", handleKeyActivity)
editBox.bind("<Control-Return>", handleAcceptSuggestion)

top.mainloop()

