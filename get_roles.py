import csv
from process_names import get_norm_name_dict, norm_name, clean_name

ORACC_FILES = ['raw-data/'+name for name in ['p001.atf', 'p002.atf', 'p003.atf', 'p004.atf',
'p005.atf', 'p006.atf', 'p007.atf', 'p008.atf', 'p009.atf', 'p010.atf',
'p011.atf', 'p012.atf', 'p013.atf', 'p014.atf', 'p015.atf']]
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'
PEOPLE_FILE = 'people.csv'
PID_DATE_FILE = 'pid_to_datedecimal.csv'

NUM_TEXTS = 20000

FAMILY_WORDS = ['dumu', 'dumu-munus', 'dam', 'um-me-da', 'nin₉', 'šeš']

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
	def __init__(self, p, date=''):
		self.p_index = p
		# can add date/place/etc.
		self.roles = {}
			# role name: name of person (ex. 'source': 'Turamdatan')
		self.people = set()
		self.date = date

	def __str__(self):
		return 'P' + str(self.p_index) + ': \n\t' + str(self.roles) + '\n\t' + str(self.people)

class Person:
	def __init__(self):
		self.family = ''
		self.professions = set()
		self.pids = []
		self.dates = []
		self.roles = []
		self.name = None

	def __str__(self):
		return self.name

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
	return [x for x in lst if len(x) > 0 and not (x.startswith('<<') or x.endswith('>>'))]

def get_lems_and_words(lem_line, word_line):
	# lem_line: semicolon-separated list of lemmatizations, starts with '#lem: '
	# word_line: space-separated line of transliterations, starts with line number ex. '3. '
	# return: (string) list of lemmatizations/words
	lems = remove_empty_strings(lem_line[6:].split('; '))
	words = remove_empty_strings(word_line.split(' ')[1:])
	return lems, words

def process_PN(first_line_len, word_list, lem_list, trans, norm_name_dict):
	# first PN in file
	if not first_line_len:
		return

	new_person = Person()
	new_person.pids.append(trans.p_index)
	roles = set()

	i = 0
	while i < len(word_list):
		word, lem = word_list[i], lem_list[i]
		# ignore date
		if lem == 'mu[year]':
			break
		elif lem == 'PN':
			possible_name = clean_name(word)
			possible_norm_name = norm_name(norm_name_dict, possible_name)
			if not new_person.name:
				if possible_norm_name != 'not PN':
					new_person.name = possible_name
					new_person.norm_name = possible_norm_name
			# elif possible_norm_name and possible_norm_name != 'not PN':
				# there's another PN
				# ** this may not be the right way to process this. seems complicated.
				# process_PN(output_data, word_list[i:], lem_list[i:], p_index, date)
				# break
				# print('another name?', word, word_list, lem_list)
		elif word in ROLE_KEYWORDS:
			role_info = ROLE_KEYWORDS[word]
			role_name, PN_relative = role_info[0], role_info[1]

			found_other_part = len(role_info) != 3
			# 'su ba-ti' and 'su ba-an-ti' are keywords that are more than one word
				# so ROLE_KEYWORDS just has 'su', and then here I check
					# if it is followed by 'ba-ti' or 'ba-an-ti'
			if len(role_info) == 3:
				for other_part in role_info[2]:
					if i < len(word_list)-1 and word_list[i+1] == other_part:
						found_other_part = True

			if found_other_part:
				roles.add(role_name)

		elif lem != 'PN' and new_person.name != None:
			for family_word in FAMILY_WORDS:
				if word == family_word and i < len(word_list)-1 and lem_list[i+1] == 'PN':
					possible_name = clean_name(word_list[i+1])
					possible_norm_name = norm_name(norm_name_dict, possible_name)
					if possible_norm_name != 'not PN':
						i += 1
						if possible_norm_name != None:
							new_person.family = family_word + ' ' + possible_norm_name
						else:
							new_person.family = family_word + ' ' + possible_name
			# all words that come after the name in the same LINE are being treated as possible professions
				# with the one that comes first having precedence
				# and '[' in lemmatization
					# to remove things like PN, GN, DN
						# if these things are actually useful, can add them back
			if i < first_line_len and word not in FAMILY_WORDS and '[' in lem:
				new_person.professions.add(lem)
				i = first_line_len - 1 		# each person only has one profession

		i += 1

	if not new_person.name:
		return

	trans.people.add(new_person)
	if len(roles) == 0:
		# print(new_person, roles, new_person.family, new_person.professions)
		# print(new_person, lem_list)
		return 0, new_person
	new_person.roles.append(roles)
	return 1, new_person

	# output_data.append([name, PN_info['role'], PN_info['profs'], PN_info['family'], p_index, date])

def lst_to_str(lst):
	lst = list(lst)    # sometimes it's a set
	lst = [x for x in lst if len(x) > 0]
	if len(lst) == 0:
		return ''
	else:
		return lst

def make_csv_row(person):
	return person.name, person.norm_name, lst_to_str(person.roles), lst_to_str(person.professions), \
				person.family, lst_to_str(person.pids), lst_to_str(person.dates)

def main():
	drehem_texts = get_drehem_p_ids()
	pid_date_dict = get_pid_dates()
	norm_name_dict = get_norm_name_dict()

	count_texts = 0
	count_no_role = 0

	all_people_list = []

	curr_PN_words, curr_PN_lems = [], []
	first_PN_line_len = None

	for oracc_filename in ORACC_FILES:
		with open(oracc_filename) as input_file:
			all_trans = {}		# P_index : Transaction object
			curr_trans = None
			for line in input_file:
				line = line.strip()		# remove \n
				if line.startswith('# '):    # comments
					continue
				if line.startswith('&P'):	# new text
					p_index = get_next_text(input_file, line, drehem_texts)
					if p_index == None: # reached end of file
						break
					# print(p_index)
					count_texts += 1
					if count_texts > NUM_TEXTS:
						break

					date = pid_date_dict[p_index] if p_index in pid_date_dict else ''
					curr_trans = Transaction(p_index, date)
					all_trans[p_index] = curr_trans
					curr_line_queue = []
				if 'PN' in line:
					result = process_PN(first_PN_line_len, curr_PN_words, curr_PN_lems, curr_trans, norm_name_dict)
					if result:
						has_role, new_person = result
						count_no_role += has_role
						all_people_list.append(new_person)
						new_person.dates.append(date)

					# reset to new PN
					curr_PN_lems, curr_PN_words = get_lems_and_words(line, prev_line)
					first_PN_line_len = len(curr_PN_lems)

				elif line.startswith('#lem'):
					lem_list, word_list = get_lems_and_words(line, prev_line)
					curr_PN_lems.extend(lem_list)
					curr_PN_words.extend(word_list)

				prev_line = line

	count_no_norm_name = 0
	no_norm_name_set = set()
	all_unnorm_names, all_norm_names = set(), set()

	with open(PEOPLE_FILE, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		csv_writer.writerow(['name', 'normalized name', 'roles', 'profession', 'family', 'p index', 'date'])
		for person in sorted(all_people_list, key=lambda x: x.name + str(x.dates)):
			row = make_csv_row(person)
			if not row[1]:
				no_norm_name_set.add(row[0])
				count_no_norm_name += 1
			else:
				all_norm_names.add(row[1])
			all_unnorm_names.add(row[0])

			csv_writer.writerow(row)

	print()
	print('fraction of PNs with no normalization', count_no_norm_name / len(all_people_list))
	print('total number of PNs (rows in people.csv):', len(all_people_list))
	print()

	print('fraction of unique names with no normalization found', len(no_norm_name_set) / len(all_unnorm_names))
	print('total number of unique (unnormalized) names:', len(all_unnorm_names))
	print()

	print('total number of unique unnormalized names for which normalization was found:', len(all_unnorm_names) - len(no_norm_name_set))
	print('total number of unique normalized names', len(all_norm_names))
	print()

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








