#!/usr/bin/env python
try:
	from Tkinter import *
	import tkFileDialog
except:
	from tkinter import *
	from tkinter import filedialog
	tkFileDialog=filedialog

class Toolbar:
	def __init__(self, parent, items):
		self.frame=Frame(parent)
		self.items=items
		self.parent=parent
		self.buttonL=[]
		self.buttonD={}
		for item in items:
			name=item[0]
			command=item[1]
			if(len(item)>2):
				text=item[2]
			else:
				text=name
			bt=Button(self.frame, text=text)
			bt.configure(command=command)
			self.buttonL.append(bt)
			self.buttonD[name]=bt
	def pack(self):
		for button in self.buttonL:
			button.pack(side=LEFT)
		self.frame.pack(side=TOP, fill=X)

