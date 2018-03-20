#!/usr/bin/env python
# python 3.x compatability
from __future__ import print_function
import os
import sys
import string
import argparse

def main():
	print("Remove duplicates from inservlist.full and build inservlist")
	infileObj = open("inservlist.full", "r")
	outfileObj = open("inservlist", "w")

	lastline = "zip"
	for line in infileObj:
		thisline = line.strip().split(" ")
		if thisline[0] != lastline:
			outfileObj.write(thisline[0]+" "+thisline[1]+"\n")
			lastline = thisline[0]

	infileObj.close()
	outfileObj.close()
	return

if __name__ == "__main__":
	main()
