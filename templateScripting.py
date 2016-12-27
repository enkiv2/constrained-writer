#!/usr/bin/env python

import sys
import json
import re

global symbols, stack, callStack, errorState, currLine, currWord, DEBUGMODE
DEBUGMODE=False

symbols={}
stack=[]
callStack=[]
errorState=False
currLine=""
currWord=""


def dbg(msg):
	if(DEBUGMODE):
		print(msg)

def err(msg):
	global errorState
	errorState=True
	msg=msg+"\n\tStack:"+json.dumps(stack)+"\n\tCallStack:"+json.dumps(callStack)+"\n\tcurrWord:"+currWord
	sys.stderr.write("".join(["CWTS syntax error: ", msg, "\n"]))
	return "!!!"+msg+"!!!"

def getStack():
	global stack
	return stack

functionType=type(err)

def evaluate(line):
	global callStack, stack, symbols, errorState, currLine, currWord
	currLine=line
	words=line.split()
	count=len(words)
	i=0
	while i<count:
		word=words[i]
		currWord=word
		dbg(word)
		if(word==":"):
			i+=1
			if(i>=count):
				return err("Start of function at end of input: <<"+line+">>")
			name=words[i]
			i+=1
			if(i>=count):
				return err("Function with no body: <<"+line+">>")
			body=[]
			while(i<count and words[i]!=";;"):
				body.append(words[i])
				i+=1
			if(words[i]!=";;"):
				return err("Expected ';;' at end of function: <<"+line+">>")
			bodyStr=" ".join(body)
			symbols[name]="^ "+bodyStr
		elif word=="^":
			pass
		elif word=="(":
			i+=1
			while (i<count and words[i]!=")"):
				i+=1
			if(i>=count):
				return err("Expected end of comment: <<"+line+">>")
		elif(word[0]=="'"):
			stack.append(word[1:])
		elif(word[0]=="\""):
			temp=[word[1:]]
			i+=1
			while(i<count and words[i][-1]!="\""):
				temp.append(words[i])
				#print("String thus far: "+(" ".join(temp)))
				i+=1
			if(i==count):
				return err("Mismatched double-quote at end of input: <<"+line+">>")
			else:
				temp.append(words[i][:-1])
				stack.append(" ".join(temp))
		elif word=="if":
			i+=1
			res=stack.pop()
			if(res):
				res2=words[i]
				if(words[i] in symbols):
					res2=symbols[res2]
					if(type(res2)==functionType):
						ret=res2(None)
					elif(type(res2)==str and res2[0]=="^"):
						ret=evaluate(res2)
						if(ret!=None):
							stack.append(ret)
						if(errorState):
							return stack.pop()
					else:
						stack.append(res2)
				else:
					stack.append(res2)
			if(words[i+1]=="else"):
				i+=2
				if(not res):
					res2=words[i]
					if(words[i] in symbols):
						res2=symbols[res2]
						if(type(res2)==functionType):
							ret=res2(None)
							if(ret!=None):
								stack.append(ret)
							if(errorState):
								return stack.pop()
					elif(type(res2)==str and res2[0]=="^"):
						ret=evaluate(res2)
						if(ret!=None):
							stack.append(ret)
						if(errorState):
							return stack.pop()
						else:
							stack.append(res2)
					else:
						stack.append(res2)
					
		elif(word in symbols):
			res=symbols[word]
			if(type(res)==functionType):
				ret=res(None)
				if(ret!=None):
					stack.append(ret)
				if(errorState):
					return stack.pop()
			elif(type(res)==str and res[0]=="^"):
				ret=evaluate(res)
				if(ret!=None):
					stack.append(ret)
				if(errorState):
					return stack.pop()
			else:
				stack.append(res)
		else:
			stack.append(word)
		i+=1
		dbg(callStack)
		dbg(stack)
def wrap(name, func):
	global callStack, stack
	ret=None
	callStack.append(name)
	try:
		ret=func(None)
	except:
		ret=err(str(sys.exc_info())+" at line: <<"+currLine+">>")
	callStack.pop()
	return ret

def fnReg(name, fn):
	symbols[name]=lambda x:wrap(name, fn)

def t_write(_):
	global stack
	sys.stdout.write(str(stack.pop()))
	sys.stdout.flush()
def t_pop(_):
	global stack
	stack.pop()
def t_add(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	stack.append(a+b)
def t_sub(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	stack.append(a-b)
def t_mul(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	stack.append(a*b)
def t_div(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	stack.append(a/b)
def t_floor(_):
	global stack
	a=int(float(stack.pop()))
	stack.append(a)
def t_gt(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	if(a>b):
		stack.append(True)
	else:
		stack.append(False)
def t_lt(_):
	global stack
	a=float(stack.pop())
	b=float(stack.pop())
	if(a<b):
		stack.append(True)
	else:
		stack.append(False)
def t_or(_):
	global stack
	a=stack.pop()
	b=stack.pop()
	stack.append(a or b)
def t_and(_):
	global stack
	a=stack.pop()
	b=stack.pop()
	stack.append(a and b)
def t_dup(_):
	global stack
	a=stack.pop()
	stack.append(a)
	stack.append(a)
def t_2dup(_):
	global stack
	b=stack.pop()
	a=stack.pop()
	stack.append(a)
	stack.append(b)
	stack.append(a)
	stack.append(b)
def t_swp(_):
	global stack
	a=stack.pop()
	b=stack.pop()
	stack.append(a)
	stack.append(b)
def t_rot(_):
	global stack
	c=stack.pop()
	b=stack.pop()
	a=stack.pop()
	stack.append(b)
	stack.append(c)
	stack.append(a)
def t_not(_):
	global stack
	a=stack.pop()
	push(not a)

fnReg("dup",t_dup)
fnReg("2dup",t_2dup)
fnReg("swp",t_swp)
fnReg("rot",t_rot)

fnReg(".",t_write)
fnReg("pop",t_pop)
fnReg("+",t_add)
fnReg("-",t_sub)
fnReg("*",t_mul)
fnReg("/",t_div)
fnReg("floor",t_floor)
fnReg(">",t_gt)
fnReg("<",t_lt)
fnReg("|",t_or)
fnReg("&",t_and)
fnReg("!",t_not)

symbols["nl"]="\n"

def repl(_):
	sys.stdout.write("> ")
	sys.stdout.flush()
	line=sys.stdin.readline()
	while line:
		evaluate(line)
		print(stack)
		sys.stdout.write("> ")
		sys.stdout.flush()
		line=sys.stdin.readline()
symbols["repl"]=repl

boot=""" ( bootloader for our scripting language, defining non-primitive functions )
: = 2dup > rot rot < | ! ;;
: print nl swp . . ;;
: // / floor ;;
: ciel 0.5 + floor ;;
( "CWTS (ConstrainedWriter Template Scripting) starting up..." print )
( repl ) ( disabled by default )
"""

evaluate(boot)

