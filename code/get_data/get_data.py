#!/usr/bin/python

import urllib
import subprocess
import datetime

def get_file(url_address,currency1,currency2,year_start,year_end):
	'''
	Get currency exchange rate files from url_address.
	The subroutine is designed to get files from http://ratedata.gaincapital.com
	For other website, some modification maybe needed.
	Input:
		url_address (string): the website url_address
		currency1, currency2 (string): the name of two currency
		year_start, year_end (integer/string): the start and end year of the data
	Output:
		the file will be saved to ../data/currency1_currency2/year/month
	'''
	##---check build up data folder if needed
	check_result = check_folder("../data")
	if check_result != 0:
		return None
	##--find if the currency exchange rate exists and the right file name structure
	cur1 = currency1
	cur2 = currency2
	test_file = urllib.urlopen("%(url)s/%(year_start)s/01%%20January/%(cur1)s_%(cur2)s_Week2.zip" % {'url': url_address, 'year_start':year_start, 'cur1': cur1, 'cur2': cur2})
	if test_file.code != 200:
		cur1 = currency2
		cur2 = currency1
		test_file = urllib.urlopen("%(url)s/%(year_start)s/01%%20January/%(cur1)s_%(cur2)s_Week2.zip" % {'url': url_address, 'year_start':year_start, 'cur1': cur1, 'cur2': cur2})
		if test_file.code != 200:
			print 'there is no exchange rate for %(cur1)s and %(cur2)s'%{'cur1': cur1, 'cur2': cur2}
			return None
	##--check if the folder for currency1 and currency2 exists
	check_result = check_folder("../data/%(cur1)s_%(cur2)s"%{'cur1':cur1, 'cur2': cur2})
	if check_result != 0:
		return None	
	##--download data from year_start to year_end
	for year_no in xrange(year_start,year_end+1):
		##--check if the year folder exists
		check_result = check_folder("../data/%(cur1)s_%(cur2)s/%(year)s"%{'cur1': cur1, 'cur2': cur2, 'year': year_no})
		if check_result != 0:
			return None
		##--go over each month of the year and prepare month folder
		for month_no in xrange(1,13):
			month_name = datetime.date(2008, month_no, 1).strftime('%B')
			folder_address = '../data/%(cur1)s_%(cur2)s/%(year_no)s/%(month_name)s/'%{'cur1':cur1,'cur2': cur2, 'year_no': year_no, 'month_name': month_name}
			check_result = check_folder(folder_address)
			if check_result != 0:
				return None
			week_no = 1
			file_address = "%(url)s/%(year_no)s/%(month_no)02d%%20%(month_name)s/" % {'url': url_address, 'year_no':year_no, 'month_no': month_no, 'month_name': month_name}
			file_name = "%(cur1)s_%(cur2)s_Week%(week_no)s"%{'cur1':cur1, 'cur2':cur2, 'week_no': week_no}
##--test
			print file_address+file_name+'.zip'
			print urllib.urlopen(file_address+file_name+'.zip').code 
##--end test
			##--go over each week of the month
			while week_no < 7:
				if urllib.urlopen(file_address+file_name+'.zip').code == 200:
					##--download the file
					response = urllib.urlretrieve(file_address+file_name+'.zip',folder_address+file_name+'.zip')
					print "Downloading %(file_name)s.zip to %(folder_address)s"%{'file_name': file_name, 'folder_address': folder_address}
					call_return = subprocess.call("unzip -o %(folder_address)s%(file_name)s.zip -d %(folder_address)s"%{'folder_address': folder_address, 'file_name': file_name}, shell=True)
					if call_return == 0:
						print "Unzip %(file_name)s.zip"%{'file_name': file_name}
					else:
						print "Warning %(file_name)s.zip is not unzipped"%{'file_name': file_name}
				week_no += 1
				file_address = "%(url)s/%(year_no)s/%(month_no)02d%%20%(month_name)s/" % {'url': url_address, 'year_no':year_no, 'month_no': month_no, 'month_name': month_name}
				file_name = "%(cur1)s_%(cur2)s_Week%(week_no)s"%{'cur1':cur1, 'cur2':cur2, 'week_no': week_no}
##--test
				print file_address+file_name+'.zip'
				print urllib.urlopen(file_address+file_name+'.zip').code 
##--end test

		

def check_folder(folder_address):
	'''
	Check if the folder exists, return 0
	If not build one, and return 0
	If can not sucessfully build one, print out information and return 1
	'''
	if subprocess.call("test -d %(folder_address)s"%{'folder_address':folder_address}, shell=True) != 0:
		call_return = subprocess.call("mkdir %(folder_address)s"%{'folder_address':folder_address}, shell=True)
		if call_return == 1:
			print "No %(folder_address)s folder and did not sucessfully build one"%{'folder_address': folder_address}
			return 1	
	print "%(folder_address)s is prepared!"%{'folder_address': folder_address}
	return 0

if __name__ == "__main__":
	url_address = "http://ratedata.gaincapital.com"
	currency1 = "USD"
	currency2 = "EUR"
	year_start = 2013
	year_end = 2013
	get_file(url_address, currency1, currency2, year_start, year_end)
