import re

# ORACC_FILE = 'raw-data/p001.atf'
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'

NUM_TEXTS = 25
# things to keep:
#	set: (p_index)
#	dictionary: {p_index: transaction}
#	object transaction has p_index, source, receiver, 

complete_transaction_ls = list()
drehem_transaction_ls = list()

complete_drehem_p_sets = set()
p_sets_of_interest = set()
transaction_ls = list()

class Transaction:
	def __init__(self, p, line):
		self.p_index = p
		# can add date/place/etc.
		self.roles = {}
		# role name: name of person (ex. 'source': 'Turamdatan')
		self.people = set()

		self.line = line;

		self.year = None;
		

		self.ls_lines_containing_PN = list()
		# ls of lines containing PN

	def __str__(self):
		return 'P' + str(self.p_index) + '\nlines: ' + self.line 
		# + '\n\t' + str(self.people)
	def get_num_people(self):
		return len(self.people)

def get_p_index(line):
	# line of the form '&P100259 = ...': return '100259'
	return line.split(' ')[0][2:]


def get_drehem_p_ids():
	with open(DREHEM_P_IDS_FILE) as read_file:
		for line in read_file:
			complete_drehem_p_sets.add(line[:-1])
	return complete_drehem_p_sets

def collect_p_id_of_interest(file_name):
	get_drehem_p_ids();
	with open(file_name) as input_file:
		count = 0
		for line in input_file:
			line = line.strip()# remove \n
			if line.startswith('&P'):
				p_id = get_p_index(line);
				if p_id in complete_drehem_p_sets:
					p_sets_of_interest.add(p_id);
	# print( p_sets_of_interest)
	return p_sets_of_interest

def get_transactions(file_name, p_id_set_sort=None):
	
	with open(file_name) as input_file:
		currentTransaction = None;
		for line in input_file:
			line = line.strip() # remove \n
			if line.startswith('&P'):
				if currentTransaction is None:		
					p_index = get_p_index(line)
					currentTransaction = Transaction(p_index, line)
				else:
					if p_id_set_sort is None or currentTransaction.p_index in p_id_set_sort:
						transaction_ls.append(currentTransaction) # add the transaction to the list
					

					p_index = get_p_index(line)
					currentTransaction = Transaction(p_index, line) # start a new transaction
			else:
				currentTransaction.line += "\n" + line;

		# add the last transaction to the list
		if p_id_set_sort is None or currentTransaction.p_index in p_id_set_sort:
			transaction_ls.append(currentTransaction)
		
	# print(len(transaction_ls))
	# print(transaction_ls[-1])
	return transaction_ls


# with open(ORACC_FILE) as input_file:
# 	for line in input_file:
# 		line = line.strip()
# 		if not re.match(r'^&P|^#lem|^\d+\.|^@|^#|^\$|^\d+ʾ\.|^=:|^\s+$|^$', line):
# 			print(line);
		# if re.match(r'^&P|^#lem|^\d+\.|^\d+ʾ\.', line):
		# 	print(line)
		# elif re.match(r'|^\s+$|^$', line):
			#ignore
		# elif re.match(r'^@|^#|^\$|')
def clean_transaction(transaction):
	# change the whole transaction.line into
	# a list of important text, discarding unimportant lines
	# transaction.line = ["1. ~~ #lem: ~~" ... ]

	# print(transaction.p_index)
	searchObj = re.findall(r'(\d+ʾ\..*\n#lem:.*|\d+\..*\n#lem:.*)', transaction.line)
	
	transaction.line = searchObj


def get_PN(transaction):
	# get the list of lines containing PN --> transaction.ls_lines_containing_PN
	# get the set of PN --> transaction.people
	txt,translit = None, None
	for line in transaction.line:
		if "PN" in line:
			transaction.ls_lines_containing_PN.append(line)

			
	for line in transaction.ls_lines_containing_PN:
		txt,translit = line.split("\n")
		
		translit = translit.replace("#lem: ","")
		
		translit, txt = translit.split(";"), txt.split(" ")[1:]

		for index, word  in enumerate(translit):
		    if "PN" in word:
		        # print(translit, txt, index)

		        transaction.people.add(txt[index])
	# if len(transaction.people) == 0:
	# 	print(transaction.line,txt, translit, transaction.p_index)

	# print(transaction.people)


def process_files():
	#return a complete list of transactions out of all input files
	global p_sets_of_interest
	global transaction_ls
	global complete_transaction_ls
	global drehem_transaction_ls
	i = 1; # oracc file number


	
	while i <= 15:
		p_sets_of_interest = set()
		transaction_ls = list()
		if i < 10:
			ORACC_FILE = 'raw-data/p00'+str(i)+'.atf'
		else:
			ORACC_FILE = 'raw-data/p0'+str(i)+'.atf'
		collect_p_id_of_interest(ORACC_FILE);

		#get complete list of transactions
		get_transactions(ORACC_FILE);
		for trans in transaction_ls:		
			clean_transaction(trans)
			get_PN(trans)
		complete_transaction_ls += transaction_ls

		# get drehem list of transactions
		# TO CHANGE LATER (BAD IMPLEMENTATION; READING THE FILE TWICE)
		transaction_ls = list()
		get_transactions(ORACC_FILE,p_sets_of_interest);
		for trans in transaction_ls:		
			clean_transaction(trans)
			get_PN(trans)
		drehem_transaction_ls += transaction_ls


		print("Got transactions from "+ORACC_FILE)
		i+=1

	print("***FINISH***")
	print("***Total of ", len(complete_transaction_ls), " transactions.***")
	print("***Total of ", len(drehem_transaction_ls), " Drehem transactions.***")
	return complete_transaction_ls

def main():
	ls = process_files()
	no_PN_count = 0
	contain_ki_count = 0
	contain_subati_count = 0
	contain_ragaba_count = 0
	for trans in ls:
		if trans.get_num_people() == 0:
			no_PN_count+=1
		line = ''.join(trans.line)
		if "ki[place]" in line:
			contain_ki_count += 1
			
		if "šu ba-ti" in line:
			contain_subati_count += 1
		if "ra₂-gaba" in line:
			contain_ragaba_count += 1


	print(no_PN_count, " transactions do NOT have PN.")
	print(contain_ki_count, " transactions contain a word ki[place].")
	print(contain_subati_count, " transactions contain a word šu ba-ti.")
	print(contain_ragaba_count, " transactions contain a word ra₂-gaba.")

main()

