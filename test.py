#!/bin/env -S python
"""This is the program GliPy Demo v${VERSION}
Copyright (C) 2007 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""

VERSION = "0.1.2"

import glipy as cli

@cli.flag(shortname="r")
def a(): "first argument"

@cli.flag()
def b(): "second one"

@cli.flag()
def start(): "Starts the process"

cli.init()

if start():
	print(a() or b())
