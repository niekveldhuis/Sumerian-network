import re
import ogsl

NAME_FILE = 'name_list.atf'
OGSL_DICT = ogsl.make_dict()

def get_norm_name_dict():
	# uses list of normalized names
	# returns dict unnormalized : normalized
		# if 'unkn', not put in dict
		# if 'not PN', mapped to 'not PN'
	d = {}
	with open(NAME_FILE) as f:
		for line in f:
			elems = [x.strip() for x in line.split('\t') if x]
			elems = elems[1:3]
			# very first line
			if len(elems) < 2:
				continue
			name, norm = elems
			name = name.lower()

			if norm != 'unkn':
				d[name] = norm
	return d

def clean_name(name):
	# remove stuff within << >>
	pattern = '<<.*>>'
	name = re.sub('-<<.*>>', '', name)
	name = re.sub('<<.*>>-', '', name)

	# remove various symbols
	remove = ['#', '[', ']', '?', '!', '<', '>']
	for r in remove:
		name = name.replace(r, '')

	return name

def lst_to_str(lst):
	s = ''
	for sign in lst:
		s += sign + '-'
	s = s[:-1]
	return s

def all_signs(word):
	signs = word.split('-')
	all_possible = set()
	# print(OGSL_DICT)
	for i, s in enumerate(signs):
		if s in OGSL_DICT:
			# print(OGSL_DICT[s])
			for other_s in OGSL_DICT[s]:
				new_form = list(signs)
				new_form[i] = other_s
				all_possible.add(lst_to_str(new_form))
	return all_possible


def norm_name(d, unnorm):
	unnorm = clean_name(unnorm)		# just in case

	unnorm = unnorm.lower()

	replace = dict([
				('₀', '0'),
				('₁', '1'),
				('₂', '2'),
				('₃', '3'),
				('₄', '4'),
				('₅', '5'),
				('₆', '6'),
				('₇', '7'),
				('₈', '8'),
				('₉', '9'),
				('š', 'c')  ])
	for r in replace:
		unnorm = unnorm.replace(r, replace[r])

	if unnorm in d:
		return d[unnorm]
	for other_possible in all_signs(unnorm):
		if other_possible in d:
			# print(unnorm, other_possible)
			return d[other_possible]
	# print(unnorm)
	return None









