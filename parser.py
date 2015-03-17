import sys
import requests
from lxml import etree
import re

class cik:
	def __init__(self, cik):
		self.cik = str(cik)
		self.url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_arg}&type=13F-HR&dateb=&owner=exclude&count=40&output=atom".format(cik_arg=self.cik)
	
		#Uncomment to validate CIK:
		'''
		if not self.validate():
			sys.exit("Invalid CIK/Ticker.")
		'''

		self.parsed = etree.parse(self.url)	
		self.txt_link = ""
		self.primary_doc = ""
		self.info_table = ""
	
	def validate(self):
		#Validate given ticker by making call to EDGAR website.
		cik_validation = requests.get(self.url)
		if not '<?xml' in cik_validation.content[:10]:
			return False
		else:
			return True

	def find_first_txt_link(self):

		entry_tag = "{http://www.w3.org/2005/Atom}entry"
		link_tag = "{http://www.w3.org/2005/Atom}link"
		find_string = "{ent}/{link}".format(ent=entry_tag, link=link_tag)
		
		link = self.parsed.find(find_string).get("href")
		link_edit_index = link.find("-index.htm")
		self.txt_link = ''.join([link[:link_edit_index], ".txt"])

	def split_txt_file(self):
		txt_file = requests.get(self.txt_link).content
		
		iter_open = re.finditer(r"<XML>", txt_file)
		iter_close = re.finditer(r"</XML>",txt_file)
		
		opening_indices = [index.start()+len("<XML>\n") for index in iter_open]
		closing_indices = [index.start() for index in iter_close]

		self.primary_doc = txt_file[opening_indices[0]:closing_indices[0]]
		self.info_table = txt_file[opening_indices[1]:closing_indices[1]]

		f_prim_doc = open("primary_doc.xml","w")
		f_prim_doc.write(self.primary_doc)
		f_prim_doc.close()
		f_info_table = open("info_table.xml","w")
		f_info_table.write(self.info_table)
		f_info_table.close()

if __name__ == '__main__':
	ticker = cik(sys.argv[1])
	ticker.find_first_txt_link()
	ticker.split_txt_file()

