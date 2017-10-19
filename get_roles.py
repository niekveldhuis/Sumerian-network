from scrape_cdli import find_drehem

ORACC_FILE = 'raw-data/p001.atf'

NUM_TEXTS = 25

class Transaction:
	def __init__(self, p):
		self.p_index = p
		# can add date/place/etc.
		self.roles = {}
			# role name: name of person (ex. 'source': 'Turamdatan')
		self.people = set()

	def __str__(self):
		return 'P' + str(self.p_index) + ': \n\t' + str(self.roles) + '\n\t' + str(self.people)

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
			line = next(input_file).strip()

		p_index = get_p_index(line)
	print(line, '\n')
	return p_index

def get_lems_and_words(lem_line, word_line):
	# lem_line: semicolon-separated list of lemmatizations, starts with '#lem: '
	# word_line: space-separated line of transliterations, starts with line number ex. '3. '
	# return: (string) list of lemmatizations/words
	lems = lem_line[6:].split('; ')
	words = word_line.split(' ')[1:]
	return lems, words

def main():
	drehem_texts = find_drehem()

	professions = {}
		# dictionary from name -> lemmatization of profession
								# (word that comes right after name)

	with open(ORACC_FILE) as input_file:
		count_texts = 0
		prev_line_ki = False
		all_trans = {}		# P_index : Transaction object
		curr_trans = None
		for line in input_file:
			line = line.strip()		# remove \n
			if line.startswith('&P'):	# new text
				p_index = get_next_text(input_file, line, drehem_texts)
				# print(p_index)
				count_texts += 1
				if count_texts > NUM_TEXTS:
					break
				curr_trans = Transaction(p_index)
				all_trans[p_index] = curr_trans
			elif line.startswith('#lem'):
				print(prev_line)
				print(line)
				lems, words = get_lems_and_words(line, prev_line)
				for i in range(len(lems)):
					curr_lem, curr_word = lems[i], words[i]
					if curr_lem == 'PN':
						if i < len(lems) - 1:
							professions[curr_word] = (words[i+1], lems[i+1])
							# print(curr_word, ':', professions[curr_word])
						curr_trans.people.add(curr_word)
					if prev_line_ki and i == 0 and curr_lem == 'PN':
						print(curr_word, 'is a receiver')
						curr_trans.roles['receiver'] = curr_word
						prev_line_ki = False
					elif curr_word == 'ki':
						print(words[i+1], 'is a source')
						curr_trans.roles['source'] = words[i+1]
						prev_line_ki = True
				print('')
			prev_line = line

	print(professions)
	for t in all_trans.values():
		print(t)

main()

# possible questions about professions:
	# I'm going line by line: could the profession of someone
		# be not on the same line as their name?
	# Could the profession not be only one word?
		# If so, would it extend all the way to the end of the
			# line with the name?
	# People's names can probably come in different forms










