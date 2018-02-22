import csv

ORACC_FILES = ['raw-data/'+name for name in ['p001.atf', 'p002.atf', 'p003.atf', 'p004.atf',
'p005.atf', 'p006.atf', 'p007.atf', 'p008.atf', 'p009.atf', 'p010.atf',
'p011.atf', 'p012.atf', 'p013.atf', 'p014.atf', 'p015.atf']]
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'
OUTPUT_FILE = 'people.csv'
PID_DATE_FILE = 'pid_to_datedecimal.csv'

NUM_TEXTS = 20000

NOT_PROFESSIONS = {'dab[seize]', 'maškim[administrator]', 'šu[hand]', 'teŋ[approach]',
					'ŋiri[foot]', 'X', 'FN'}

class Transaction:
	def __init__(self, p):
		self.p_index = p
		# can add date/place/etc.
		self.roles = {}
			# role name: name of person (ex. 'source': 'Turamdatan')
		self.people = set()

	def __str__(self):
		return 'P' + str(self.p_index) + ': \n\t' + str(self.roles) + '\n\t' + str(self.people)

def get_drehem_p_ids():
	p_sets = set()
	with open(DREHEM_P_IDS_FILE) as read_file:
		for line in read_file:
			p_sets.add(line[:-1])
	return p_sets

def get_pid_dates():
	pid_date_d = {}
	with open(PID_DATE_FILE) as input_file:
		csv_reader = csv.reader(input_file)
		for row in csv_reader:
			pid_date_d[row[0]] = row[1]
	return pid_date_d

def get_p_index(line):
	# line of the form '&P100259 = ...': return '100259'
	return line.split(' ')[0][2:]

def get_next_text(input_file, line, drehem_texts):
	# gets next text that is from Drehem
	# and mutates input_file object to be at that line
	# returns P index of first file found that is from Drehem
	# currently will break if actually reach end of file.
	p_index = get_p_index(line)
	while p_index not in drehem_texts:
		line = next(input_file)
		# find next text that IS from Drehem
		while not line.startswith('&P'):
			try:
				line = next(input_file).strip()
			except StopIteration:
				return None

		p_index = get_p_index(line)
	# print(line, '\n')
	return p_index

def remove_empty_strings(lst):
	return [x for x in lst if len(x) > 0]

def get_lems_and_words(lem_line, word_line):
	# lem_line: semicolon-separated list of lemmatizations, starts with '#lem: '
	# word_line: space-separated line of transliterations, starts with line number ex. '3. '
	# return: (string) list of lemmatizations/words
	lems = remove_empty_strings(lem_line[6:].split('; '))
	words = remove_empty_strings(word_line.split(' ')[1:])
	# if (len(lems) != len(words)):
	# 	print('word', words)
	# 	print('lem', lems)
	return lems, words

def process_PN(output_data, word_line, lem_line, p_index, date):
	name = None
	found_name = False

	PN_info = {}

	lem_line, word_line = get_lems_and_words(lem_line, word_line)

	line_length = min(len(word_line), len(lem_line))
	i = 0
	while i < line_length:
		word, lem = word_line[i], lem_line[i]
		if lem == 'PN':
			if not found_name:
				name = word 
				found_name = True
		elif found_name:
			if word == 'dumu' and i < line_length-1:
				PN_info['dumu'] = word_line[i+1]
				i += 1
			elif 'profs' not in PN_info and lem not in NOT_PROFESSIONS:
				PN_info['profs'] = lem
		i += 1

	# 3 times total in all the texts, 'PN' is the last lemma
	# in the line, but the transliteration line is shorter
	# than the lemmatization line
		# ex. text 105224: '2(diš)', 'gin₂',        'ku₃',      'sa₁₀', 'a-ba-dingir-mu-gin₇'
							# 'n', 'giŋ[unit]', 'kug[metal]', 'sa[pay', 'for]',     'PN'
		# not sure what it means, but not important, probably.
	if not name:
		return

	# if 'dumu' in PN_info and 'profs' in PN_info:
	# 	print(name, PN_info['profs'], PN_info['dumu'], p_index)
	# 	print(word_line, '|||', lem_line)

	if 'profs' not in PN_info:
		PN_info['profs'] = ''
	if 'dumu' not in PN_info:
		PN_info['dumu'] = ''

	output_data.append([name, PN_info['profs'], PN_info['dumu'], p_index, date])


def main():
	drehem_texts = get_drehem_p_ids()
	pid_date_dict = get_pid_dates()
	all_professions = set()

	output_data = []
	count_texts = 0

	count_pids_without_dates = 0

	for oracc_filename in ORACC_FILES:
		with open(oracc_filename) as input_file:
			all_trans = {}		# P_index : Transaction object
			curr_trans = None
			for line in input_file:
				line = line.strip()		# remove \n
				if line.startswith('&P'):	# new text
					p_index = get_next_text(input_file, line, drehem_texts)
					if p_index == None: # reached end of file
						break
					# print(p_index)
					count_texts += 1
					if count_texts > NUM_TEXTS:
						break
					curr_trans = Transaction(p_index)
					all_trans[p_index] = curr_trans
					curr_line_queue = []
				if 'PN' in line:
					if p_index in pid_date_dict:
						date = pid_date_dict[p_index]
					else:
						count_pids_without_dates += 1
						date = ''
					process_PN(output_data, prev_line, line, p_index, date)

				prev_line = line

	with open(OUTPUT_FILE, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		csv_writer.writerow(['name', 'profession', 'family (dumu)', 'p index', 'date'])
		for row in sorted(output_data, key=lambda x: x[0]+str(x[-1])):		# sorted alphabetically by name, then date
			csv_writer.writerow(row)

	print(count_pids_without_dates, 'texts without dates?? out of', count_texts, 'total texts')

	# print(professions)
	# with open(PROFESSIONS_OUT, 'w') as output_file:
	# 	csv_writer = csv.writer(output_file)
	# 	csv_writer.writerow(['name', 'profession', 'p index'])
	# 	for row in name_prof_pids:
	# 		csv_writer.writerow(row)
	# 	# for name, profession in sorted(professions.items(), key=lambda x: x[0]):
	# 	# 	csv_writer.writerow([name] + [str(profession)])
	# print(num_PNs, 'PNs found')

	# print('number of PNs found vs. number of unique names:', count_num_names, len(professions))
	# print('number of unique professions found:', len(all_professions))

	# with open('transactions_count.csv', 'w') as output_file:
	# 	csv_writer = csv.writer(output_file)
	# 	csv_writer.writerow(['name', 'number of transactions'])
	# 	for name, num in sorted(num_trans_dict.items(), key=lambda x:x[1], reverse=True):
	# 		csv_writer.writerow([name, num])


	# for t in all_trans.values():
	# 	print(t)

main()

# a thing:
	# transliteration of a word with '<< >>' doesn't have
		# corresponding lemmatization
	# these words look unimportant, generally








