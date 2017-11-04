import csv

ORACC_FILES = ['raw-data/'+name for name in ['p001.atf', 'p002.atf', 'p003.atf', 'p004.atf',
'p005.atf', 'p006.atf', 'p007.atf', 'p008.atf', 'p009.atf', 'p010.atf',
'p011.atf', 'p012.atf', 'p013.atf', 'p014.atf', 'p015.atf']]
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'
PROFESSIONS_OUT = 'name_prof_pids.csv'

NUM_TEXTS = 20000

NOT_PROFESSIONS = {'dab[seize]', 'maškim[administrator]', 'šu[hand]'}

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

def main():
	drehem_texts = get_drehem_p_ids()

	# professions = {}
	# 	# dictionary from name -> lemmatization of profession
	# 							# (word that comes right after name)

	# count_num_names = 0
	# num_trans_dict = {}
	# 	# dictionary from name -> number of transactions they appear in

	all_professions = set()

	name_prof_pids = []

	for oracc_filename in ORACC_FILES:
		with open(oracc_filename) as input_file:
			count_texts = 0
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
				elif line.startswith('#lem'):
					# print(prev_line)
					# print(line)
					lems, words = get_lems_and_words(line, prev_line)
					line_length = min(len(lems), len(words))
					for i in range(line_length):
						curr_lem, curr_word = lems[i], words[i]
						if curr_word == 'mu':	# ignore names in year name
							break
						if curr_lem == 'PN':
							if curr_word[-3:] == '-ta':
								curr_word = curr_word[:-3]
							if i < line_length - 1:
								# count_num_names += 1
								if lems[i+1] not in NOT_PROFESSIONS:
									all_professions.add(lems[i+1])
									name_prof_pids.append([curr_word, lems[i+1], p_index])
									# if curr_word in professions:
									# 	# professions[curr_word].add((words[i+1], lems[i+1]))
									# 	professions[curr_word].add(lems[i+1])
									# 	num_trans_dict[curr_word] += 1
									# else:
									# 	professions[curr_word] = set()
									# 	# professions[curr_word].add((words[i+1], lems[i+1]))
									# 	professions[curr_word].add(lems[i+1])
									# 	num_trans_dict[curr_word] = 1
								# print(curr_word, ':', professions[curr_word])
							curr_trans.people.add(curr_word)
						# if curr_word == 'ki':
						# 	# print(words[i+1], 'is a source')
						# 	curr_trans.roles['source'] = words[i+1]
					# print('')
				prev_line = line

	# print(professions)
	with open(PROFESSIONS_OUT, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		csv_writer.writerow(['name', 'profession', 'p index'])
		for row in name_prof_pids:
			csv_writer.writerow(row)
		# for name, profession in sorted(professions.items(), key=lambda x: x[0]):
		# 	csv_writer.writerow([name] + [str(profession)])

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








