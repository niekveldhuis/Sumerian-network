import csv
from process_names import get_norm_name_dict, norm_name, clean_name
from process_dates import get_pid_date_dict
from collections import defaultdict

DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'
PEOPLE_FILE = 'people.csv'
ORACC_CSV = 'oracc_json/output/parsed.csv'
NUM_TEXTS = 1000000

FAMILY_WORDS = ['dumu', 'dumu-munus', 'dam', 'um-me-da', 'nin₉', 'šeš']

# all words that come directly after PNs, filtered by Niek.
POSSIBLE_PROFESSIONS = {'enkud[tax-collector]N', 'malah[sailor]N', 'engar[farmer]N', 'kakaku[profession]N', 'šuʾi[barber]N', 'gardu[soldier]N', 'lugalraʾusa[body-guard]N', 'geme[worker]N', 'ušbar[weaver]N', 'irara[oil-presser]N', 'zadim[stone-cutter]N', 'nagada[herdsman]N', 'azu[doctor]N', 'arua[offering]N', 'gala[singer]N', 'uddatuš[jester]N', 'šabra[administrator]N', 'luʾurak[profession]N', 'abgal[sage]N', 'MAR.TU[westerner]N', 'dubsar[scribe]N', 'bisaŋdubak[archivist]N', 'muhaldim[cook]N', 'saŋŋa[official]N', 'ŋuruš[male]N', 'susig[flayer]N', 'eme[nurse]N', 'nubanda[overseer]N', 'ugula[overseer]N', 'hedab[worker]N', 'idu[doorkeeper]N', 'zabardab[official]N', 'gugal[inspector]N', 'namuddatuš[entertainment]N', 'atu[doorkeeper?]N', 'šukud[fisherman]N', 'saŋ.DUN₃[recorder]N', 'lumah[priest]N', 'kugdim[smith]N', 'gudgaz[butcher]N', 'simug[smith]N', 'ragaba[rider]N', 'udul[herdsman]N', 'šidim[builder]N', 'galamah[singer]N', 'ad.KID[weaver]N', 'luʾennuŋ[guard]N', 'dikud[judge]N', 'UN.IL₂[menial]N', 'šarrabdu[administrator]N', 'emeda[nursemaid]N', 'guzala[official]N', 'tugdu[felter]N', 'ukul[profession]N', 'nukirik[gardener]N', 'kaguruk[supervisor]N', 'azlag[fuller]N', 'gabar[herder]N', 'šaŋanla[trader]N', 'tibira[sculptor]N', 'hazanum[mayor]N', 'santanak[gardener]N', 'šakkanak[general]N', 'lunisiga[profession]N', 'nin[lady]N', 'erešdiŋir[priestess]N', 'sukkalmah[official]N', 'sipad[shepherd]N', 'šatam[official]N', 'luhuŋa[hireling]N', 'unud[cowherd]N', 'ensik[ruler]N', 'nar[musician]N', 'ummia[expert]N', 'agaʾus[soldier]N', 'ziʾa[worker]N', 'arad[slave]N', 'mušendu[bird-catcher]N', 'salhuba[fisherman]N', 'maššugidgid[diviner]N', 'sukkal[secretary]N', 'ašgab[leatherworker]N', 'damgar[merchant]N', 'kurušda[fattener]N', 'en[priest]N', 'kaš[runner]N', 'lupana[archer]N', 'lukur[priestess]N', 'gallagal[policeman]N', 'lungak[brewer]N', 'šagia[cup-bearer]N', 'lumumun[priest]N', 'gabus[shepherd]N', 'lugal[king]N', 'erin[people]N', 'lutukul[soldier]N', 'šagud[drover]N', 'gudug[priest]N', 'išib[priest]N', 'dubsarmah[official]N', 'nagar[carpenter]N', 'kuš[official]N', 'mušlah[charmer]N'}

# using keywords to find role of PNs in transactions
# dictionary from KEYWORD(lemma) : (meaning, where PN is relative to keyword)
	# ex. {'ki[place]N', ('source', 1)} means 'ki PN' means PN is a source
		# {('dab[seize]V/t', ('recipient', -1))} means 'PN dab' means PN is a recipient
ROLE_KEYWORDS = {  
					'ki[place]N':				('source', 1),
					'dab[seize]V/t':			('recipient', -1),
					'mu.DU[delivery]N':			('new owner', 1),
					'šu[hand]N':				('recipient', -1),
					'ŋiri[foot]N':				('intermediary', 1),
					'maškim[administrator]N':	('representative', -1),
					'ziga[expenditure]N':		('source', 1)
				}

# Represents one transaction, which for now means one for each p index.
class Transaction:
	def __init__(self, p, date='', og_date = ''):
		self.p_index = p
		self.roles = {}        # role name: Person object (ex. 'source': Person('Turamdatan'))
		self.no_role_people = set()    # set of Person objects who DON'T have roles
		self.date = date
		self.original_date = og_date

	def __str__(self):
		return 'P' + str(self.p_index) + ': \n\t' + str(self.roles) + '\n\t' + str(self.no_role_people)

# Represents one person in one transaction
# Used in make_node_edge_lists.py, so if want to merge in a different way,
	# should modify equals/hash here
class Person:
	def __init__(self):
		self.family = ''
		self.profession = ''
		self.role = None
		self.name = None
		self.norm_name = ''

	def __str__(self):
		name = self.name
		if self.norm_name:
			name = self.norm_name
		return 'Person(' + name + ')'

	def __repr__(self):
		return str(self)

	# equals and hash just use the normalized name if it exists, or name if it doesn't
	def __equals__(self, other):
		if len(self.norm_name) > 0 and len(other.norm_name) > 0:
			return self.norm_name == other.norm_name
		# if they had the same unnormalized name, it's impossible for one
			# normalized name to be defined and the other to not be
		return self.name == other.name

	def __hash__(self):
		if self.norm_name and len(self.norm_name) > 0:
			return hash(self.norm_name)
		if self.name:
			return hash(self.name)
		return 0

def get_drehem_p_ids():
	p_sets = set()
	with open(DREHEM_P_IDS_FILE) as read_file:
		for line in read_file:
			p_sets.add(line[:-1])
	return p_sets

# splits a lemma into (form, guideword, POS)
def split_lemma(lemma):
	return lemma.replace(']', '[').split('[')

# Processes one entire text, stores parsed information in trans (Transaction object)
	# people, roles, professions, etc
# lemmas: list of lemmas in text
def process_text(lemmas, trans, norm_name_dict):
	# print("\n" + trans.p_index)
	curr_person = None
	right_after_PN = False
	unassigned_positive_role = None

	# failed_normalisations = defaultdict(int)
	# all_unnorm = []

	i = 0
	while i < len(lemmas):
		lemma = lemmas[i]
		# years mostly come at ends of texts (though not always ex. P101786)
			# and years always have PNs in them that aren't part of transaction
		if 'mu[year]' in lemma:
			break

		form, gw, pos = split_lemma(lemma)
		# print(lemma, form, gw, pos)

		# a boolean flag that stays true if neither of the first two outer IFs are entered
			# not a PN and not a role keyword
		not_PN_or_role_flag = True

		# if see PN
		if gw == 'PN':
			# print('\nNEW PERSON:', lemma)
			# print(lemmas[i-5:i+5])
			not_PN_or_role_flag = False

			# switching to new person so if no role found for previous, add to trans.no_role_people
			if curr_person != None and curr_person.role == None:
				trans.no_role_people.add(curr_person)

			possible_name = clean_name(form)
			possible_norm_name = norm_name(norm_name_dict, possible_name)
			# print('found name', lemma, possible_norm_name)
			if possible_norm_name != 'not PN':
				curr_person = Person()
				curr_person.name = possible_name
				curr_person.norm_name = possible_norm_name

				# all_unnorm.append(possible_name)

				# if possible_norm_name == None:
				# 	failed_normalisations[possible_name] += 1

			# a not very interesting note: curr_person is only = None in ONE text:
				# P128887: ša-gu-ul-tum is marked PN but normalised as 'not PN', but comes right after a ziga, indicating a role
			if curr_person != None and lemmas[i-1] in ROLE_KEYWORDS and unassigned_positive_role != None:
				# print('positive', curr_person.name, 'change role from', curr_person.role, 'to', unassigned_positive_role)
				curr_person.role = unassigned_positive_role
				trans.roles[unassigned_positive_role] = curr_person
				unassigned_positive_role = None

		if lemma in ROLE_KEYWORDS:
			not_PN_or_role_flag = False
			role_info = ROLE_KEYWORDS[lemma]
			role_name, PN_relative = role_info[0], role_info[1]

			if PN_relative > 0:
				unassigned_positive_role = role_name
				# print('unassigned_positive_role =', role_name)
			# elif 'PN' in lemmas[i-1]:    # this doesn't work because of professions.
			elif curr_person != None:
				# print('negative', curr_person.name, 'change role from', curr_person.role, 'to', role_name)
				curr_person.role = role_name
				trans.roles[role_name] = curr_person

		# not a PN or role and not before the very first PN => is a possible family or profession
		# as long as come RIGHT AFTER PN
		if not_PN_or_role_flag and curr_person != None:
			found_family = False
			for family_word in FAMILY_WORDS:
				if form == family_word and i < len(lemmas)-1 and 'PN' in lemmas[i+1]:
					next_form, _, _ = split_lemma(lemmas[i+1])
					possible_name = clean_name(next_form)
					possible_norm_name = norm_name(norm_name_dict, possible_name)
					if possible_norm_name != 'not PN':
						found_family = True
						i += 1  # found ex. 'dumu PN' so skip to after the family's PN
						if possible_norm_name != None:
							curr_person.family = family_word + ' ' + possible_norm_name
						else:
							curr_person.family = family_word + ' ' + possible_name

			# eventually use 'found_family' flag to not add the family member's professions as this person's
			if i < len(lemmas) and 'PN' in lemmas[i-1] and lemmas[i] in POSSIBLE_PROFESSIONS:
				curr_person.profession = lemma
				# possible_professions_dict[lemma] += 1
			curr_person = None    # past the very next word, can't be related to this person.

		i += 1

	# return failed_normalisations, all_unnorm

def merge_dicts(mutate_this_d, d2):
	for k in d2:
		mutate_this_d[k] += d2[k]

# Returns list of Transaction objects, one for each text!
def make_all_trans():
	drehem_texts = get_drehem_p_ids()
	pid_date_dict = get_pid_date_dict()
	norm_name_dict = get_norm_name_dict()

	# to see what possible professions exist
	# all_possible_professions = defaultdict(int)	

	# to see what common names aren't getting normalised
	# failed_normalisations = defaultdict(int)
	# all_unnorm = []

	with open(ORACC_CSV) as csvfile:
		csv_reader = csv.reader(csvfile)

		curr_trans = None
		all_trans = {}		# P_index : Transaction object

		count_texts = 0

		for row in csv_reader:
			# first line
			if row[0] == 'id_text':
				continue
			p_index = row[0].split('/')[1]
			# print(drehem_texts)
			if p_index[1:] in drehem_texts:
				count_texts += 1
				if count_texts > NUM_TEXTS:    # for testing
					break

				date_name, processed_date = '', ''
				if p_index[1:] in pid_date_dict:
					date_name, processed_date = pid_date_dict[p_index[1:]]

				curr_trans = Transaction(p_index, date=processed_date, og_date=date_name)
				all_trans[p_index] = curr_trans

				lemmas = row[1].split(' ')
				process_text(lemmas, curr_trans, norm_name_dict)
				# merge_dicts(failed_normalisations, curr_failed_norms)
				# all_unnorm.extend(curr_all_unnorm)
				# print(curr_trans.roles)

	return all_trans

def write_to_people_csv(filename, all_trans):
	with open(PEOPLE_FILE, 'w') as output_file:
		csv_writer = csv.writer(output_file)
		csv_writer.writerow(['name', 'normalised name', 'role', 'profession', 'family', 'p index', 'date name', 'processed date'])

		for trans_pid in sorted(all_trans.keys()):
			trans = all_trans[trans_pid]
			for role, p in trans.roles.items():
				csv_writer.writerow([p.name, p.norm_name, role, p.profession, p.family, trans.p_index, trans.original_date, trans.date])
			for p in trans.no_role_people:
				csv_writer.writerow([p.name, p.norm_name, '', p.profession, p.family, trans.p_index, trans.original_date, trans.date])



all_trans = make_all_trans()
write_to_people_csv(PEOPLE_FILE, all_trans)


# total_num_names = len(all_unnorm)
# num_failed = sum(failed_normalisations.values())

# total_unique = len(set(all_unnorm))
# num_unique_failed = len(failed_normalisations)

# print()
# print('fraction of PNs with normalisation', 1 - (num_failed / total_num_names))
# print('total number of PNs (rows in people.csv):', total_num_names)
# print()

# print('fraction of unique names with normalisation found', 1 - (num_unique_failed / total_unique))
# print('total number of unique unnormalised names for which normalisation was found:', total_unique - num_unique_failed)
# print('total number of unique (unnormalised) names:', total_unique)
# print()



# with open('failed_normalisations.txt', 'w') as f:
# 	for name, count in sorted(failed_normalisations.items(), key=lambda x: x[1], reverse=True):
# 		f.write(str(count) + '\t' + name + '\n')

























