import sys
import requests
from lxml import etree
import re

class cik:
	def __init__(self, cik):
		self.cik = str(cik)
		self.url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_arg}&type=13F-HR&dateb=&owner=exclude&count=40&output=atom".format(cik_arg=self.cik)
	
		# Uncomment to validate CIK:
		'''
		if not self.validate():
			sys.exit("Invalid CIK/Ticker.")
		'''

		# The etree.parse() method fetches atom feed from the URL constructed above.
		# This atom feed contains a list of all 13F-HR filings for the given CIK.
		self.parsed = etree.parse(self.url)
		self.txt_link = ""
		self.primary_doc = ""
		self.info_table = ""
	
	def validate(self):
		# Validate given ticker by making a call to EDGAR website with constructed URL.
		cik_validation = requests.get(self.url)
		if not '<?xml' in cik_validation.content[:10]:
			return False
		else:
			return True

	def find_first_txt_link(self):
		# Finds index link of the first filing and from that link, constructs the link
		# to the full txt submission and stores it in self.txt_link

		entry_tag = "{http://www.w3.org/2005/Atom}entry"
		link_tag = "{http://www.w3.org/2005/Atom}link"
		find_string = "{ent}/{link}".format(ent=entry_tag, link=link_tag)
		
		link = self.parsed.find(find_string).get("href")
		# Replaces "-index.htm" with ".txt"
		link_edit_index = link.find("-index.htm")
		self.txt_link = ''.join([link[:link_edit_index], ".txt"])

	def split_txt_file(self):
		# Splits the retrieved txt file into two parts:
		#
		# 1. The primary_doc which contains information about the institution (name,
		#    address etc.)
		# 2. The info_table which contains details regarding number of shares, value etc.

		txt_file = requests.get(self.txt_link).content
		iter_open_xml = re.finditer(r"<XML>", txt_file)
		iter_close_xml = re.finditer(r"</XML>",txt_file)
		
		opening_indices = [index.start()+len("<XML>\n") for index in iter_open_xml]
		closing_indices = [index.start() for index in iter_close_xml]

		self.primary_doc = txt_file[opening_indices[0]:closing_indices[0]]
		self.info_table = txt_file[opening_indices[1]:closing_indices[1]]

		# Uncomment the following if you want to see xml written to files:
		# 		
		# f_prim_doc = open("primary_doc.xml","w")
		# f_prim_doc.write(self.primary_doc)
		# f_prim_doc.close()
		# f_info_table = open("info_table.xml","w")
		# f_info_table.write(self.info_table)
		# f_info_table.close()
		
	def write_primary_doc_csv(self):
		# Although the spec lists a lot of information for primary_doc, a lot
		# of it is things like addresses and agent names. So I'm ignoring everything except
		# periodOfReport, tableEntryTotal and tableValueTotal

		primary_doc_parse = etree.fromstring(self.primary_doc)

		namespace = "{http://www.sec.gov/edgar/thirteenffiler}"
		headerData_tag = "".join([namespace, "headerData/"])
		filerInfo_tag = "".join([namespace, "filerInfo/"])
		formData_tag = "".join([namespace, "formData/"])
		summaryPage_tag = "".join([namespace, "summaryPage/"])

		periodOfReport_tag = "".join([headerData_tag, filerInfo_tag, namespace, "periodOfReport"])
		tableEntryTotal_tag = "".join([formData_tag, summaryPage_tag, namespace, "tableEntryTotal"])
		tableValueTotal_tag = "".join([formData_tag, summaryPage_tag, namespace, "tableValueTotal"])
		
		periodOfReport = primary_doc_parse.find(periodOfReport_tag).text
		tableEntryTotal = primary_doc_parse.find(tableEntryTotal_tag).text
		tableValueTotal = primary_doc_parse.find(tableValueTotal_tag).text
		commaSeparated = ",".join([periodOfReport, tableEntryTotal, tableValueTotal])
		print commaSeparated

		f = open("primary_doc.csv","w")
		f.write(commaSeparated)
		f.close()

	def write_info_table_csv(self):
		# I'm getting all the information in each infoTable tag and writing to a csv file

		info_table_parse = etree.fromstring(self.info_table)
		namespace = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"


if __name__ == '__main__':
	ticker = cik(sys.argv[1])
	ticker.find_first_txt_link()
	ticker.split_txt_file()
	ticker.write_primary_doc_csv()