import csv

DATA_FILE = 'full_roles_profs.csv'
OUTPUT_FILE = 'pid_to_datedecimal.csv'

KINGS = {
	'Ur-Namma': (2112, 2095),
	'Shulgi': (2094, 2047),
	'Amar-Suen': (2046, 2038),
	'Shu-Suen': (2037, 2029),
	'Ibbi-Suen': (2028, 2004)
}

BIAS = 2112

INVALID_DATES = {'00', '--', '--,'}

# biases years start and end with BIAS
# to convert range (-2112 -> -2004) to (0 -> 108)
def bias_one_year_pair(start, end):
	return BIAS-start, BIAS-end

# calls bias_one_year_pair on all kings' reigns
def bias_years():
	kings_biased = {
		name: bias_one_year_pair(year[0], year[1])
		for name,year in KINGS.items()
	}
	return kings_biased

def write_output(pid_decimal_dict):
	with open(OUTPUT_FILE, 'w') as output_file:
		items = sorted(pid_decimal_dict.items(), key=lambda x: x[1])
		for pid, date in items:
			output_file.write(pid + ', ' + str(date[0]) + ', ' + str(date[1]) + '\n')

# call from outside
def get_pid_date_dict():
	king_years = bias_years()

	pid_decimal_dict = {}
	unusable_set = set()		# king name in INVALID (00 or --)
					# sometimes year/month/day not INVALID
	more_dates_set = set()		# more than one date in year column
					# currently, just using first one listed

	with open(DATA_FILE) as csv_file:
		csv_reader = csv.reader(csv_file)
		for row in csv_reader:
			if row[0] == 'name':	# first row: col labels
				year_index = row.index('year')
				pid_index = row.index('p id')
				continue
			pid = row[pid_index]
			if pid in pid_decimal_dict:		# only do this once per text
				continue
			year_name = row[year_index].split('.')
			if len(year_name) > 4:
				more_dates_set.add((pid, tuple(year_name)))
				year_name = year_name[:4]
			if len(year_name) == 1:		# empty string
				unusable_set.add((pid, tuple(year_name)))
				continue

			king, year, month, day = year_name
			# if king in INVALID_DATES and month not in INVALID_DATES:
			# 	print(pid, row[year_index])
			if king in INVALID_DATES:
				# print('king invalid', pid, king, year, month, day)
				unusable_set.add((pid, tuple(year_name)))
				continue
			# print(king, year, month, day)
			start, end = king_years[king]
			
			decimal = start
			decimal += catch_num_formatting(year, '')
			decimal += catch_num_formatting(month, '0.')
			day = day.split(' ')[0]
			decimal += catch_num_formatting(day, '0.00')

			# sometimes float adds something like 0.0000000000001 for no reason
			# so rounding to 4 decimal places (2 each for month and day)
			decimal = '%.4f' % decimal
			# print(year_name, decimal)
			pid_decimal_dict[pid] = ('{'+row[year_index]+'}', decimal)
	return pid_decimal_dict

	# print('\n# texts with 00 or -- for king name:', len(unusable_set))
	# print('# texts with more than one date:', len(more_dates_set))

	# write_output(pid_decimal_dict)

# fixes formatting in NUMBER (-m, -d) and adds value as
# appropriate place value, using DECIMAL
def catch_num_formatting(number, decimal):
	if number in INVALID_DATES:
		return 0

	try:
		return float(decimal + number[:2])
	except ValueError:
		print('num formatting', number)
		return 0

	# 09m for month, 12d for day: always with "(intercalated)"


# (intercalated), (us2 year), (us2-us2 year) ?
	# things that can come after date

# there are texts with no king, but with month and sometimes day

# number of texts with 00 or -- for king name: 384
# number of texts with more than one date: 728














