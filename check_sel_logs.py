#!/usr/bin/python2.6

# Description : 
# -----------
#
# This script will check the occupency of the IPMI SEL Logs and if the threshold is affected it will dump the logs and erase the IPMI SEL logs 
# The dump of the IPMI SEL Logs will be stored into /var/log/ directory into the following format ipmi_sel_logs.log
# A mechanism of logrotate will rotate the dump and error log each month 
# The script should be generic and robbust to handle all the brands and model of BMC  
# It will use the third party tool ipmitool 

from datetime import date
import subprocess
import re
import os
import sys

class SelLogs():

	# Contructor SelLogs
	def __init__(self):

		# Declaration of attributes 
		self.path_ipmitool = None
		self.option_sel_ipmitool = None
		self.option_clear_ipmitool = None
		self.option_elist_ipmitool = None
		self.date_for_logs = None
		self.path_to_dump_logs = None
		self.name_of_sel_logs = None
		self.percentage_used = None

		try:
			# Definition of attributes
			self.path_ipmitool = "/usr/bin/ipmitool"
			self.option_sel_ipmitool = "sel"
			self.option_clear_ipmitool = "clear"
			self.option_elist_ipmitool = "elist"

			try:
				self.date_for_logs = date.today().strftime("%m/%d/%Y")
			except Exception:
				self.date_for_logs = "00-00-0000"

			self.path_to_dump_logs = "/var/log/"
			self.name_of_sel_logs = "ipmi_sel_logs.log"

		except Exception:
			sys.exit("[ERROR] - " + str(self.date_for_logs) + " The assignement of the attributes has failed\n")

	# Function that check the SEL logs of the BMC 
	def check_logs(self):

		try:
			# Running the command ipmitool to get the SEL informations
			ipmitool_output = subprocess.Popen([self.path_ipmitool,self.option_sel_ipmitool], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()

		except Exception:
			sys.exit("[ERROR] - " + str(self.date_for_logs) + " The command ipmitool sel has failed...\n")


		try:

			# Definition of the regex for the needed values  
			alloc_unit_size = re.search('^Alloc\\s+Unit\\s+Size\\s+:\\s+(\\d+)$', ipmitool_output, re.MULTILINE)
			alloc_total_size = re.search('^#\\s+of\\s+Alloc\\s+Units\\s+:\\s+(\\d+)$', ipmitool_output, re.MULTILINE)
			alloc_free_size = re.search('^#\\s+Free\\s+Units\\s+:\\s+(\\d+)$', ipmitool_output, re.MULTILINE)
			entries = re.search('^Entries\\s+:\\s+(\\d+)$', ipmitool_output, re.MULTILINE)

		except Exception:
                	sys.exit("[ERROR] - " + str(self.date_for_logs) + " An error occured on the regex search...\n")

		try:
		
			# Compute the percentage used 	
			number_of_bytes_used = float(entries.group(1)) * float(alloc_unit_size.group(1))
			number_of_bytes_total = float(alloc_total_size.group(1)) * float(alloc_unit_size.group(1))
			percentage_used = ( number_of_bytes_used / number_of_bytes_total ) * 100 	 

		except Exception:
			sys.exit("[ERROR] - " + str(self.date_for_logs) + " Something is wrong in computing the percentage used...\n")
				
		try:
	
			percentage = int(percentage_used)
			self.percentage_used = percentage

		except Exception:	

			sys.exit("[ERROR] - " + str(self.date_for_logs) + " Something is wrong in casting to integer the percentage...\n")	

		if percentage >= 80:
			return True
		else:
			return False

	# Function that clear the SEL Logs of the BMC
	def clear_logs(self):

		try: 
			# Running the command ipmitool to clear the SEL logs
			ipmitool_clear_output = subprocess.Popen([self.path_ipmitool,self.option_sel_ipmitool,self.option_clear_ipmitool], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()
		
		except Exception:

			sys.exit("[ERROR] - " + str(self.date_for_logs) + " The command ipmitool sel clear has failed...\n")

	# Function that dump the logs 
	def dump_logs(self):

		try:
			# Check first if the log file exist ?
			if os.path.isfile(self.path_to_dump_logs + self.name_of_sel_logs) == False:
				file = open(self.path_to_dump_logs + self.name_of_sel_logs, "w")
				file.close()

			# Opening the log file for adding some data
			file = open(self.path_to_dump_logs + self.name_of_sel_logs, "a")
			file.write("\n################# START : " + str(self.date_for_logs) + " #################\n")
			ipmitool_sel_logs = subprocess.Popen([self.path_ipmitool,self.option_sel_ipmitool,self.option_elist_ipmitool], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].strip()

			# Writing on the Log file
			for line in ipmitool_sel_logs.split('\n'):
				file.write(str(line) + "\n")

			file.write("\n################# END : " + str(self.date_for_logs) + " #################\n")

			# Closing the Log file
			file.close()

		except Exception:
			sys.exit("[ERROR] - " + str(self.date_for_logs) + " An error has occured in openning/writting to the file log in the dump_logs function...\n")


# Main function 
def main():
	
	# Instanciate the SelLogs object
	AnalyseSelLogs = SelLogs()

	try:

		# Checking if the restore_kipmi_kernel_helper_thread file is present
		if os.path.isfile('/var/lock/subsys/restore_kipmi_kernel_helper_thread'):
			sys.exit("[ERROR] - " + str(AnalyseSelLogs.date_for_logs) + " Exiting, the kipmi kernel helper thread is being restored...\n") 
		else:
			# If the Sel logs are almost full we dump the logs and clear the BMC 	
			if AnalyseSelLogs.check_logs() == True:
				AnalyseSelLogs.dump_logs()
 				AnalyseSelLogs.clear_logs()
			else:
				# Check first if the log file exist ?
        			if os.path.isfile(AnalyseSelLogs.path_to_dump_logs + AnalyseSelLogs.name_of_sel_logs) == False:
                			file = open(AnalyseSelLogs.path_to_dump_logs + AnalyseSelLogs.name_of_sel_logs, "w")
                			file.close()
		
				# Writing to the Log file that nothing need to be dump	
				file = open(AnalyseSelLogs.path_to_dump_logs + AnalyseSelLogs.name_of_sel_logs, "a")
				file.write("\n################# START : " + str(AnalyseSelLogs.date_for_logs) + " #################\n")
                		file.write("\nThe percentage used of the SEL logs is : " + str(AnalyseSelLogs.percentage_used) + " %\n")
                		file.write("\n################# END : " + str(AnalyseSelLogs.date_for_logs) + " #################\n")
                		file.close()
			return 0	
	except Exception:
		sys.exit("[ERROR] - " + str(AnalyseSelLogs.date_for_logs) + " An error has occured in openning/writting to the file log in the main funtion ...\n")


if __name__ == '__main__':
    main() 
