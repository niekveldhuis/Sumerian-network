import csv

ORACC_FILES = ['raw-data/'+name for name in ['p001.atf', 'p002.atf', 'p003.atf', 'p004.atf',
'p005.atf', 'p006.atf', 'p007.atf', 'p008.atf', 'p009.atf', 'p010.atf',
'p011.atf', 'p012.atf', 'p013.atf', 'p014.atf', 'p015.atf']]
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'
OUTPUT_FILE = 'people.csv'
PID_DATE_FILE = 'pid_to_datedecimal.csv'

NUM_TEXTS = 20000

# using keywords to find role of PNs in transactions
# dictionary from KEYWORD : (meaning, where PN is relative to keyword)
	# ex. {'ki', ('source', 1)} means 'ki PN' means PN is a source
		# {('i₃-dab₅', ('recipient', -1))} means 'PN i₃-dab₅' means PN is a recipient
	# script does not currently use the +1/-1
		# just associates keywords in the same line as a PN with that PN
# 'šu ba-ti' and 'šu ba-an-ti' are in the dictionary as 'šu', and then checked later
ROLE_KEYWORDS = {  
					'ki':			('source', 1),
					'i₃-dab₅':		('recipient', -1),
					# 'mu-kuₓ(DU)':	('new owner', 1),
					'šu':			('recipient', -1, ['ba-ti', 'ba-an-ti']),
					'giri₃':		('intermediary', 1),
					'maškim':		('representative', -1),
					'zi-ga':		('source', 1)
				}
# 'i₃-dab₅' is extremely rarely a suffix on the PN instead of a separate word afterwards
	# this may be true of other keywords too
	# these cases will not be found by this script.

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

def is_bazi(s):
	return 'ba' in s and 'zi' in s

def process_PN(output_data, word_list, lem_list, p_index, date):
	name = None

	PN_info = {}
	PN_info['role'] = []
	
	# ignore PNs in lines about dates
	if lem_list[0] == 'mu[year]':
		return

	line_length = min(len(word_list), len(lem_list))
	i = 0
	while i < line_length:
		word, lem = word_list[i], lem_list[i]
		# there is a lemmatization error with 'ba-zi' as a PN. it is not.
		if lem == 'PN' and not is_bazi(word):
			if not name:
				name = word
			else:
				# there's another PN in the same line
				# ** this may not be the right way to process this. seems complicated.
				process_PN(output_data, word_list[i:], lem_list[i:], p_index, date)
				break
				# print('another name?', name, word, word_line, lem_line)
		if word in ROLE_KEYWORDS:
			role_info = ROLE_KEYWORDS[word]
			role_name, PN_relative = role_info[0], role_info[1]

			found_other_part = len(role_info) != 3
			# 'su ba-ti' and 'su ba-an-ti' are keywords that are more than one word
				# so ROLE_KEYWORDS just has 'su', and then here I check
					# if it is followed by 'ba-ti' or 'ba-an-ti'
			if len(role_info) == 3:
				for other_part in role_info[2]:
					if word_list[i+1] == other_part:
						found_other_part = True

			if found_other_part:
				PN_info['role'].append(role_name)
		elif lem != 'PN' and name != None:
			if word == 'dumu' and i < line_length-1:
				PN_info['family'] = 'dumu ' + word_list[i+1]
				i += 1
			# all words that come after the name in the same line are being treated as possible professions
				# with the one that comes first having precedence
				# and '[' in lemmatization
					# to remove things like PN, GN, DN
						# if these things are actually useful, can add them back
			elif 'profs' not in PN_info and '[' in lem:
				PN_info['profs'] = lem

		i += 1

	# if len(set(PN_info['role'])) > 1:
	# 	print(PN_info['role'])
	# 	print(lem_list)

	# 3 times total in all the texts, 'PN' is the last lemma
	# in the line, but the transliteration line is shorter
	# than the lemmatization line
		# ex. text 105224: '2(diš)', 'gin₂',        'ku₃',      'sa₁₀', 'a-ba-dingir-mu-gin₇'
							# 'n', 'giŋ[unit]', 'kug[metal]', 'sa[pay', 'for]',     'PN'
		# not sure what it means, but not important, probably.
	if not name:
		return

	if 'profs' not in PN_info or PN_info['profs'] == 'PN':
		PN_info['profs'] = ''
	if 'family' not in PN_info:
		PN_info['family'] = ''
	if len(PN_info['role']) == 0:
		PN_info['role'] = ''
	else:
		PN_info['role'] = list(set(PN_info['role']))

	# if PN_info['profs'] and '[' not in PN_info['profs']:
	# 	print(PN_info['profs'])
	# 	print(word_list)
	# 	print('#lem', lem_list)

	output_data.append([name, PN_info['role'], PN_info['profs'], PN_info['family'], p_index, date])


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
						# print(p_index)
					else:
						# count_pids_without_dates += 1
						date = ''
					lem_list, word_list = get_lems_and_words(line, prev_line)
					process_PN(output_data, word_list, lem_list, p_index, date)

				prev_line = line

	with open(OUTPUT_FILE, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		csv_writer.writerow(['name', 'role', 'profession', 'family', 'p index', 'date'])
		for row in sorted(output_data, key=lambda x: x[0]+str(x[-1])):		# sorted alphabetically by name, then date
			csv_writer.writerow(row)

	# print(count_pids_without_dates, 'texts without dates?? out of', count_texts, 'total texts')

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








