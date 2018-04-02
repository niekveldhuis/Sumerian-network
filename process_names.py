import re

NAME_FILE = 'name_list.atf'

def get_norm_name_dict():
	# uses list of normalized names
	# returns dict unnormalized : normalized
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

			if norm == 'not PN':
				d[name] = 'not PN'
			elif norm != 'unkn':
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
	# print(unnorm)
	return None





