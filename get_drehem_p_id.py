# Adding onto Tiffany's code (to avoid merge conflicts)
# Create a text file containing drehem's p-id

import csv
import codecs
file = open("p_id_drehem.txt","w") 

CDLI_FILE = 'cdli_catalogue.csv'

def find_drehem():
	print('Reading CDLI...')
	with open(CDLI_FILE) as csvfile:
		col_labels = csvfile.readline().split(',')
		p_id_index = col_labels.index('id_text')
		location_index = col_labels.index('provenience')

		csv_reader = csv.reader(x.replace('\0', '') for x in csvfile) # see check_null_bytes()
		count = 0
		p_id_set = set()
		for row in csv_reader:
			if 'Drehem' in row[location_index]:
				p_id_set.add(row[p_id_index])
				file.write(row[p_id_index]+"\n")
				count += 1
		print(count, 'texts found from Drehem')
	# print(p_id_set)
	 
 
	file.close() 
	return p_id_set

def check_null_bytes(csvfile):
	# conclusion: (only) line 124250 in the csv has a mysterious NULL byte:
		#,,,,21198/zz001w65mw,"no atf",,nn,,,,,"University of Pennsylvania Museum of Archaeology and Anthropology, Philadelphia, Pennsylvania, USA",,"obv damaged",10/24/2005,,,8/16/2017,,"20051024 fitzgerald_upenn","N 2004",,,,,,,,,Administrative,,,?,839471570,0,277115,,Akkadian,,clay,"N 2004",,tablet,"Neo-Babylonian (ca. 626-539 BC)",,"600ppi 20160630","unpublished unassigned ?","Nippur (mod. Nuffar)",,nd,,,,,,,"Account; payments of shekel of ?; 10x16x2(u.e.)x2(le.e.
	for x in csvfile:
		if '\0' in x:
			print(x)

check_null_bytes(open(CDLI_FILE))
find_drehem()