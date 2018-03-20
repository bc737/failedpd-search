#!/usr/bin/env python
# python 3.x compatability
from __future__ import print_function
import os
import time
import sys
import string
import argparse

def main():
	monthdist = [0 for x in range(12)]
	print("Parse sqlout and build inservlist")
	infileObj = open("sqlout", "r")
	outfileObj = open("inservlist", "w")

	for line in infileObj:
		thisline = line.strip().split("\t")
		# print(thisline[0], thisline[2])
		if thisline[2].find("2017") > -1:
			thisdate = thisline[2].split("-")
			months = 14 - int(thisdate[1])
			print(thisline[0], thisdate[1], months)
			monthdist[int(thisdate[1])] += 1
			outfileObj.write(thisline[0]+" "+str(months)+"\n")

	infileObj.close()
	outfileObj.close()
	print("months distribution: ", monthdist)
	return

if __name__ == "__main__":
	main()
