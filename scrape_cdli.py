import csv
import codecs

CDLI_FILE = 'cdli_catalogue.csv'
OUTPUT_PID_DATE_FILE = 'drehem_pid_year.csv'
OUTPUT_PID_FILE = 'drehem_p_ids.txt'
INPUT_DREHEM_LIST_FILE = 'query_cat_19_02_12-014312.txt'

# gets list of p ids of texts from Drehem from BTDNS
# writes the list to output file
def get_drehem_pids():
	print('Reading BDTNS file...')
	pid_set = set()
	with open(INPUT_DREHEM_LIST_FILE) as f1:
		for line in f1:
			line = line.split('\t')
			if len(line) > 1 and len(line[1]) > 1:
				pid = line[1][1:-1]    # second column, remove P and \n
				pid_set.add(pid)
	with open(OUTPUT_PID_FILE, 'w') as f2:
		for pid in sorted(list(pid_set)):
			f2.write(pid + '\n')

	return pid_set

# matches PID (from above function) to dates from CDLI
def find_drehem(drehem_pid_set):
	print('Reading CDLI...')
	with open(CDLI_FILE) as csvfile:
		col_labels = csvfile.readline().split(',')
		p_id_index = col_labels.index('id_text')
		location_index = col_labels.index('provenience')
		year_index = col_labels.index('dates_referenced')

		csv_reader = csv.reader(x.replace('\0', '') for x in csvfile) # see check_null_bytes()
		pid_year_dict = {}
		for row in csv_reader:
			# print(row[p_id_index])
			if row[p_id_index] in drehem_pid_set:
				pid_year_dict[row[p_id_index]] = row[year_index]

	with open(OUTPUT_PID_DATE_FILE, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		for text in pid_year_dict.items():
			csv_writer.writerow(text)

	return pid_year_dict

def check_null_bytes(csvfile):
	# conclusion: (only) line 124250 in the csv has a mysterious NULL byte:
		#,,,,21198/zz001w65mw,"no atf",,nn,,,,,"University of Pennsylvania Museum of Archaeology and Anthropology, Philadelphia, Pennsylvania, USA",,"obv damaged",10/24/2005,,,8/16/2017,,"20051024 fitzgerald_upenn","N 2004",,,,,,,,,Administrative,,,?,839471570,0,277115,,Akkadian,,clay,"N 2004",,tablet,"Neo-Babylonian (ca. 626-539 BC)",,"600ppi 20160630","unpublished unassigned ?","Nippur (mod. Nuffar)",,nd,,,,,,,"Account; payments of shekel of ?; 10x16x2(u.e.)x2(le.e.
	for x in csvfile:
		if '\0' in x:
			print(x)

# check_null_bytes(open(CDLI_FILE))
# find_drehem()
find_drehem(get_drehem_pids())