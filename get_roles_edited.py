ORACC_FILE = 'raw-data/p001.atf'
DREHEM_P_IDS_FILE = 'drehem_p_ids.txt'

NUM_TEXTS = 25
# things to keep:
#	set: (p_index)
#	dictionary: {p_index: transaction}
#	object transaction has p_index, source, receiver, 


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

	def __str__(self):
		return 'P' + str(self.p_index) + '\nlines: ' + self.line 
		# + '\n\t' + str(self.people)

def get_p_index(line):
	# line of the form '&P100259 = ...': return '100259'
	return line.split(' ')[0][2:]


def get_drehem_p_ids():
	with open(DREHEM_P_IDS_FILE) as read_file:
		for line in read_file:
			complete_drehem_p_sets.add(line[:-1])
	return complete_drehem_p_sets

def collect_p_id_of_interest():
	get_drehem_p_ids();
	with open(ORACC_FILE) as input_file:
		count = 0
		for line in input_file:
			line = line.strip()# remove \n
			if line.startswith('&P'):
				p_id = get_p_index(line);
				if p_id in complete_drehem_p_sets:
					p_sets_of_interest.add(p_id);
	# print( p_sets_of_interest)
	return p_sets_of_interest

def get_transactions(file_name):
	
	with open(file_name) as input_file:
		currentTransaction = None;
		for line in input_file:
			line = line.strip() # remove \n
			if line.startswith('&P'):
				if currentTransaction is None:		
					p_index = get_p_index(line)
					currentTransaction = Transaction(p_index, line)
				else:
					transaction_ls.append(currentTransaction) # add the transaction to the list

					p_index = get_p_index(line)
					currentTransaction = Transaction(p_index, line) # start a new transaction
			else:
				currentTransaction.line += "\n" + line;
		transaction_ls.append(currentTransaction) # add the last transaction to the list
	# print(len(transaction_ls))
	# print(transaction_ls[-1])
	return transaction_ls

					

				
# collect_p_id_of_interest()
get_transactions(ORACC_FILE);
