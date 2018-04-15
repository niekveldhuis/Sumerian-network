# originally written by Jason Kha in Spring 2017

import re

def fix_numbers(s):
	SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
	return s.translate(SUB).lower()


def parse():
	ogsl_array = []
	with open("ogsl.asl", "r", encoding='utf-8') as f:
	    for line in f:
	        ogsl_array.append(line)

	equivalencies = list()

	i = 0
	entry_words = list()
	while i < len(ogsl_array):
		if '@sign' in ogsl_array[i]:
			sign_name = re.split(r' |\t', ogsl_array[i])[1].rstrip('\n')
			entry_words.append(fix_numbers(sign_name))
		while '@v' not in ogsl_array[i]:
			i += 1
			if i >= len(ogsl_array):
				return equivalencies
		while '@end' not in ogsl_array[i]:
			if ogsl_array[i][:2] == '@v':
				arr = re.split(r'\t+', ogsl_array[i])
				if len(arr) > 1:
					only_word = re.split(r' +', arr[1])	
					only_word[0] = only_word[0].rstrip('\n')
					entry_words.append(fix_numbers(only_word[0]))
			i += 1
			if i >= len(ogsl_array):
				equivalencies.append(entry_words)
				return equivalencies
		i += 1
		while len(ogsl_array[i]) == 1:
			i += 1
		equivalencies.append(entry_words)
		entry_words = list()
		if i >= len(ogsl_array):
			return equivalencies
	return equivalencies


def make_dict():
	equivalencies = parse()

	ogsl_dict = dict()
	for eq in equivalencies:
		for i in range(len(eq)):
			for j in range(len(eq)):
				if i != j:
					try:
						ogsl_dict[eq[i]].add(eq[j])
					except KeyError:
						ogsl_dict[eq[i]] = set()
						ogsl_dict[eq[i]].add(eq[j])
	return ogsl_dict

# print(make_dict())













