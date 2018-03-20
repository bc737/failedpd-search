#!/usr/bin/env python
##################
### scan the event logs for failed PD messages and calculate the pd failed time, pd rebuild complete time and pd replaced time
### Author: Bryan Carroll
###
### Take 1 parameter which is an inserv id
##################
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
import datetime

class pdfail_class:
	def __init__(self):
		# print("ddsscan class")
		self.logrecords =  " "
		self.eventlogpaths = []
		self.inservid = " "
		self.tpdver = " "
		self.model = " "
		self.numnodes = " "
		self.failedpdid = "Unknown"
		self.pdfailtime = "Unknown"
		self.pdrebuildtime = "Unknown"
		self.pdcagemag = "Unknown"
		self.pdreplacetime = "Unknown"


	def get_inserv_info(self):
		# con = mdb.connect('vasa0098.cxo.hp.com','readonlyuser','readonlypass','stats_config')
		con = mdb.connect('engstats.3pardata.com','readonlyuser','readonlypass','stats_config')

		cur=con.cursor()
		#query="select TPDVER,CUSTNAME,SYSNAME,SITE,MODEL,NUMNODES from inservs where INSERV_SERIAL = 1611046"
		query="select TPDVER,MODEL,NUMNODES from inservs where INSERV_SERIAL = '" + self.inservid + "'"
		# print("query: ", query)
		cur.execute(query)

		for row in cur.fetchall():
			self.tpdver,self.model,self.numnodes=row
        		# print("inserv info: ", row)
        		# print("inserv model: ", self.model)
		if con:
			con.close()

	def getlogdir(self, inserv_id, filetype, nummonths):
		eventlogpaths = []
		self.inservid = inserv_id
	
		current_month=int(time.strftime("%m"))
		current_year=int(time.strftime("%Y"))
		base="/share/st%s/prod/data/files/3PAR.INSERV/TierTwo/%s-%s/%s/%s"
		months_checked=0

		while (months_checked < nummonths):
			#limit scope to a maximum if 2 years
			month=current_month-months_checked
			year=current_year
			if month < 1:
				month=12+month
				year=current_year-1
		
			month=str(month).zfill(2)
			for i in range(0,250):
				try: 
					thisdir=base% (i,year,month,inserv_id,filetype)
					found=os.listdir(thisdir)
					if found: 
						self.eventlogpaths.append(thisdir)
						# print("check ", thisdir)
				except:
					#traceback.print_exc()
					continue
			months_checked+=1
		return 1

	def grep_diskfail(self, directory):
		# grep directory for PD failed messages
		self.logrecords = ""
		# -h = skip the filename in the output
		cmd='grep -h "Disk fail chunklets relocated" ' + directory + '/*'
		print("cmd: ", cmd)
		self.logfileObj.write("cmd: {}\n".format(cmd))
		self.logrecords=commands.getoutput(cmd).strip()

	def grep_diskrebuild(self, directory):
		# grep directory for PD failed messages
		self.logrecords = ""
		# -h = skip the filename in the output
		cmd='grep -h "Physical Disk {} Failed" '.format(self.failedpdid) + directory + '/*'
		print("cmd: ", cmd)
		self.logfileObj.write("cmd: {}\n".format(cmd))
		self.logrecords=commands.getoutput(cmd).strip()

	def grep_diskreplace(self, directory):
		# grep directory for servicemag -mag #:# messages
		self.logrecords = ""
		# -h = skip the filename in the output
		cmd='grep -h "servicemag resume" ' + directory + '/* | grep "mag {}"'.format(self.pdcagemag)
		print("cmd: ", cmd)
		self.logfileObj.write("cmd: {}\n".format(cmd))
		self.logrecords=commands.getoutput(cmd).strip()

	def capturediskfail(self):
		# logrecords contains a disk failure signature.  Capture
		j = self.logrecords.find("sw_pd:")
		j += 6
		k = self.logrecords.find(" ", j)
		self.failedpdid = self.logrecords[j:k]
		# first 26 characters is the timestamp - only take the first 16...
		self.pdfailtime = self.logrecords[:16]

	def capturerebuild(self):
		# logrecords contains a disk rebuild complete signature.  Capture
		# first 26 characters is the timestamp
		self.pdrebuildtime = self.logrecords[:16]
		j = self.logrecords.find("Magazine")
		j += 9
		k = self.logrecords.find(":", j)
		k = self.logrecords.find(":", k+1)
		self.pdcagemag = self.logrecords[j:k]

	def capturereplace(self):
		# logrecords contains a servicemag -mag #:# signature.  Capture
		# first 26 characters is the timestamp
		self.pdreplacetime = self.logrecords[:16]

	def getfailedpddata(self, inserv_id, nummonths):
		self.logfileObj = open("failedpd.log", "a")
		self.logfileObj.write("***** starting inserv {} at {}\n".format(inserv_id, str(datetime.datetime.now())))
		self.failedpdid = "Unknown"
		self.pdfailtime = "Unknown"
		self.pdrebuildtime = "Unknown"
		self.pdcagemag = "Unknown"
		self.pdreplacetime = "Unknown"
		self.getlogdir(inserv_id, "evtlog", int(nummonths))
		print(len(self.eventlogpaths), " log directories found.")
		self.logfileObj.write("{} log directories found.\n".format(len(self.eventlogpaths)))

		# self.get_inserv_info()
		lookingfordrivefail = True
		lookingforrebuild = False
		lookingforreplace = False
		for i in range(len(self.eventlogpaths)-1, -1, -1):
			# print(self.eventlogpaths[i])
			if lookingfordrivefail:
				self.grep_diskfail(self.eventlogpaths[i])
				if len(self.logrecords) > 0:
					# found a failed drive.  Capture the data
					print(self.logrecords)
					self.logfileObj.write(self.logrecords+"\n")
					self.capturediskfail()
					print("pd, time: ", self.failedpdid, self.pdfailtime)
					self.logfileObj.write("failed PDid: {} {}\n".format(self.failedpdid, self.pdfailtime))
					lookingfordrivefail = False
					lookingforrebuild = True
			if lookingforrebuild:
				self.grep_diskrebuild(self.eventlogpaths[i])
				if len(self.logrecords) > 0:
					# found rebuild complete signature
					print(self.logrecords)
					self.capturerebuild()
					print("rebuild complete: ", self.pdrebuildtime, self.pdcagemag)
					self.logfileObj.write("rebuild complete: {} {}\n".format(self.pdrebuildtime, self.pdcagemag))
					lookingforrebuild = False
					lookingforreplace = True
			if lookingforreplace:
				self.grep_diskreplace(self.eventlogpaths[i])
				if len(self.logrecords) > 0:
					# found replace signature
					print(self.logrecords)
					self.capturereplace()
					print("replace complete: ", self.pdreplacetime)
					self.logfileObj.write("replace complete: {}\n".format(self.pdreplacetime))
					lookingforreplace = False
					break
		# found what was there
		print("done.", inserv_id, self.failedpdid, self.pdfailtime, self.pdrebuildtime, self.pdreplacetime)
		fileObj = open("failedpd.data", "a")
		fileObj.write(inserv_id+","+self.failedpdid+","+self.pdfailtime+","+self.pdrebuildtime+","+self.pdreplacetime+"\n")
		fileObj.close()
		self.logfileObj.write("***** finished inserv {} at {}\n".format(inserv_id, str(datetime.datetime.now())))
		self.logfileObj.close()

def main():
	print("Failed PD Event Log Extract Tool.  {}".format(str(datetime.datetime.now())))

	inservlistfilename = sys.argv[1] # file with inserv #'s
	inservlistfileObj = open(inservlistfilename, "r")

	pd = pdfail_class()

        for line in inservlistfileObj:
                thisline = line.strip().split(" ")
                # print(thisline[0], thisline[1])

		pd.getfailedpddata(thisline[0], int(thisline[1]))
	
	return

if __name__ == "__main__":
	main()
