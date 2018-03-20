#!/usr/bin/env python
# python 3.x compatability
from __future__ import print_function
import os
import time
import MySQLdb as mdb 
import sys
import commands
import string
import argparse
import traceback

def get_inserv_info(self, inservid):
	con = mdb.connect('engstats.3pardata.com','readonlyuser','readonlypass','stats_config')

	cur=con.cursor()
	query="select TPDVER,MODEL,NUMNODES,CUSTNAME from inservs where INSERV_SERIAL = '" + inservid + "'"
	# print("query: ", query)
	cur.execute(query)

	for row in cur.fetchall():
		tpdver,model,numnodes,custname=row
       		# print("inserv info: ", row)
	if con:
		con.close()

def main():
	print("Add Cust data to failedpd")

	infilename = sys.argv[1] # only parameter is failedpd.data filename
	infileObj = open(infilename, "r")
	outfileObj = open(infilename+".out", "w")

	for line in infileObj:
		thisline = line.strip().split(",")
		print("inservid: ", thisline[0])
		outfileObj.write(thisline[0]+" "+thisline[1]+"\n")

	infileObj.close()
	outfileObj.close()
	return

if __name__ == "__main__":
	main()
