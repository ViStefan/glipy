"""This implements command-line arguments parsing."""

import sys
import re

VERSION = "0.2"

DEBUG = True

syntax = []
commandline = {}

class Type:
	VALUE = 0
	FLAG = 1
	STRING = 2

class Argument:
	def __init__(name, long, short, type, doc):
		this.name = name
		this.long = long
		this.short = short
		this.type = type
		this.doc = doc

def parse_commandline():

	cl = {}

	def get_typed_value(k, value=None, short=True):
		key = "-%s" % k if short else "--%s" % k
		t = [x for x in syntax if x[1] == k] if short else [x for x in syntax if x[0] == k]

		if t == []:
			raise Exception("Unknown key %s" % key)

		if t[0][2] == Type.FLAG:
			return True
		elif value is None:
			if short:
				raise Exception("Short key in group can't have a value until it goes last")
			else:
				raise Exception("Value for key %s is not present" % key)
		elif t[0][2] == Type.STRING:
			if not is_short(value) and not is_long(value):
				return value
			else:
				raise Exception("Value for key %s is not present" % key)

	def is_short(k):
		return len(k) > 1 and k[0] == "-" and k[1] != "-"

	def short(s, shorts, value=None):
		if s in cl or s in shorts:
			raise Exception("Duplicating short key %s" % s)
		
		return get_typed_value(s, value, short=True)

	def parse_shorts(k, v):
		shorts = {}
		for s in k[1:-1]:
			shorts[s] = short(s, shorts)

		shorts[k[-1]] = short(k[-1], shorts, value=v)
		
		return shorts

	def is_long(k):
		if k[2:] in cl:
			raise Exception("Duplicating long key %s" % k)
		return len(k) > 2 and k[0:2] == "--"

	def parse_long(k, v):
		return {k : get_typed_value(k, v, short=False)}

	sys.argv.append(None)
	state = 0
	for a, b in zip(sys.argv[1:], sys.argv[2:]):
		if is_short(a):
			cl = {**cl, **parse_shorts(a, b)}
		elif is_long(a):
			cl = {**cl, **parse_long(a[2:], b)}
		else:
			if "__files__" not in cl:
				cl["__files__"] = []
			cl["__files__"].append(a)

	return cl

def kebab(s):
	return re.sub(r'([^\-A-Z])([A-Z])', r'\1-\2', s.replace('_', '-')).lower()

def get_decorator(type, value, *args, **kwargs):
	def decorator(callable):
		n = kebab(callable.__name__)
		name = n
		short = kwargs["shortname"] if "shortname" in kwargs else n[0]
		if short in [x[1] for x in syntax]:
			raise Exception("Duplicating shortname for command-line argument --%s: '%s', is already in use by --%s" % (name, short, [x[0] for x in syntax if x[1] == short][0]))
		syntax.append((name, short, type, callable.__doc__))
		return value(name, short, type, callable.__doc__)
	return decorator

def flag(*args, **kwargs):
	def value(name, short, type, doc):
		def f():
			return name in commandline or short in commandline
		return f
	return get_decorator(Type.FLAG, value, *args, **kwargs)

def string(*args, **kwargs):
	def value(name, short, type, doc):
		def f():
			if name in commandline or short in commandline:
				return commandline[name] if name in commandline else commandline[short]
			else:
				return None
		return f
	return get_decorator(Type.STRING, value, *args, **kwargs)

@flag()
def help(): "Print this message"

@flag()
def version(): "Prints version"

@flag()
def debug(): "Whether print debug information"

def init():
	global commandline
	commandline = parse_commandline()

	if debug() or DEBUG:
		import pprint
		p = pprint.PrettyPrinter(indent="2", width=60)
		p.pprint(syntax)
		p.pprint(commandline)

	if not hasattr(sys.modules["__main__"], "VERSION"):
		raise Exception("VERSION is not defined! Command-line argument --version is not implemented.")
	if sys.modules["__main__"].__doc__ is None:
		raise Exception("Main description of program is not present.")
	sys.modules["__main__"].__doc__ = sys.modules["__main__"].__doc__.replace(r"${VERSION}", sys.modules["__main__"].VERSION)
	if help() or len(sys.argv) == 1:
		print(sys.modules["__main__"].__doc__)
		shorts = ''.join([x[1] for x in syntax])
		longs = ' --'.join([x[0] for x in syntax])
		print("Usage: -%s --%s" % (shorts, longs))
		for arg in syntax:
			print("\t--%s\t-%s\t%s" % (arg[0], arg[1], arg[3]))
		exit()

	if version():
		print(sys.modules["__main__"].VERSION)
		exit()

if __name__ == "__main__":
	init()