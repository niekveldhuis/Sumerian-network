import csv
from collections import defaultdict
from get_roles_json_by_text import Transaction, Person

PEOPLE_FILE = 'people.csv'
NODE_FILE = 'nodes_gn.csv'
EDGE_FILE = 'edges_gn.csv'
GEO_FILE = 'geo_names.csv'

NUM_ROWS_TO_READ = 100000000    # for debugging

# Represents one node in the network (one row of nodes list)
# To keep track of what was merged.
class Node:
	def __init__(self, i, n):
		self.index = i
		self.name = n
		self.roles = []
		self.p_ids = []
		self.professions = []
		self.date_names = []
		self.processed_dates = []

		self.people_node_indices = []    # only used for GN nodes.

	# modify this (and hash) if want to merge in different ways
	def __equals__(self, other):
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)

# Returns dictionary of {p index : set of GNs mentioned}
	# using GEO_FILE
def make_geo_names_dict():
	p_to_geo = defaultdict(set)    # p number : set of GNs
	with open(GEO_FILE) as geo_f:
		csv_reader = csv.reader(geo_f)
		for row in csv_reader:
			gn = row[0]
			p_numbers = eval(row[1])
			for p in p_numbers:
				p_to_geo['P' + p].add(gn)

	return p_to_geo

# Returns dictionary of {p index : Transaction object}
	# using PEOPLE_FILE
	# every text (p index) is assumed to correspond to one Transaction
def make_all_trans():
	all_trans = {}    # P_index : Transaction object

	# count_roles = defaultdict(int)
	# count_len_roles = defaultdict(int)
	# count_num_people = defaultdict(int)
	# count_all_people = 0
	# count_no_role_people = 0
	# count_single_roles = defaultdict(int)

	with open(PEOPLE_FILE) as f:
		csv_reader = csv.reader(f)

		curr_p_index = -1
		curr_trans = None
		count_rows = 0
		for row in csv_reader:
			count_rows += 1
			if count_rows > NUM_ROWS_TO_READ:
				break
			if row[0] == 'name':
				continue

			unnorm = row[0]
			norm = row[1]
			name = norm if len(norm) > 0 else unnorm
			role = row[2]
			if role == 'new owner':  # seems the same. maybe not.
				role = 'recipient'
			profession = row[3]
			family = row[4]

			new_person = Person()
			new_person.name = name    # just using the name field of the Person object
			new_person.role = role
			new_person.profession = profession
			new_person.family = family

			p_index = row[5]
			if p_index != curr_p_index:
				# if curr_trans:
				# 	count_len_roles[len(curr_trans.roles)] += 1
				# 	if len(curr_trans.roles) == 1:
				# 		count_single_roles[list(curr_trans.roles.keys())[0]] += 1
				# 	count_num_people[len(curr_trans.roles)+len(curr_trans.no_role_people)] += 1

				curr_trans = Transaction(p_index)
				curr_p_index = p_index
				all_trans[p_index] = curr_trans

			curr_trans.original_date = row[6]
			curr_trans.date = row[7]

			if len(role) > 0:
				curr_trans.roles[role] = new_person
			else:
				curr_trans.no_role_people.add(new_person)
			# else:
			# 	count_no_role_people += 1
			# 	curr_trans.no_role_people.add(name)
			# count_all_people += 1

			# count_roles[role] += 1

	# print(count_roles)
	# print(len(all_trans))
	# print(count_len_roles)
	# print(count_num_people)
	# print(count_no_role_people, count_all_people)
	# print(count_single_roles)

	return all_trans

# returns the node indices corresponding to role1, role2 in roles
	# if either role doesn't exist in this transaction, returns None, None
def get_node_indices_if_exist(role1, role2, roles, name_to_index_dict):
	if role1 in roles and role2 in roles:
		return name_to_index_dict[roles[role1].name], name_to_index_dict[roles[role2].name]
	else:
		return None, None

# writes one row to edges csv
def write_edge_row(role1, role2, trans, name_to_index_dict, csv_writer, edge_index):
	roles =  trans.roles
	index1, index2 = get_node_indices_if_exist(role1, role2, roles, name_to_index_dict)
	if index1 == None:
		return 0
	csv_writer.writerow([edge_index, index1, index2, 'Directed', role1, role2, trans.p_index])
	return 1

# main function that makes node and edges csvs
# dummy: if dummy nodes for each text should be made
def make_node_edge_lists(all_trans, p_to_geo, dummy=False):
	with open(NODE_FILE, 'w') as node_f:
		with open(EDGE_FILE, 'w') as edge_f:
			csv_writer_node = csv.writer(node_f)
			csv_writer_edge = csv.writer(edge_f)
			csv_writer_node.writerow(['', 'name', 'roles', 'professions', 'processed dates', 'p indices'])
			csv_writer_edge.writerow(['id', 'source', 'target', 'type', 'role 1', 'role 2', 'p index'])

			existing_nodes = {}        # index : Node object. doesn't include GN nodes
			name_to_index_dict = {}    # if want to merge by not name, need to change keys: perhaps make hash for Person obj
			edge_index = 1
			node_index = 1
			geo_nodes = {}             # GN : Node object

			# count_gn = 0

			for trans in all_trans.values():
				# if trans.p_index in p_to_geo:
				# 	count_gn += 1
				# nodes
				for person_obj in trans.roles.values():
					name = person_obj.name
					# this person's name hasn't been seen yet: make new Node()
					if name not in name_to_index_dict:
						node = Node(node_index, name)
						node.name = name
						existing_nodes[node_index] = node
						name_to_index_dict[name] = node_index
						node_index += 1
					else:
						node = existing_nodes[name_to_index_dict[name]]
					node.roles.append(person_obj.role)
					node.p_ids.append(trans.p_index)
					node.professions.append(person_obj.profession)
					node.date_names.append(trans.original_date)
					node.processed_dates.append(trans.date)

					if trans.p_index in p_to_geo:
						geo_names = p_to_geo[trans.p_index]
						for gn in geo_names:
							if gn in geo_nodes:
								geo_node = geo_nodes[gn]
							else:
								geo_node = Node(node_index, gn)
								node_index += 1
							geo_node.people_node_indices.append((node_index, trans.p_index))
							geo_nodes[gn] = geo_node

				# edges
				edge_index += write_edge_row('source', 'recipient', trans, name_to_index_dict, csv_writer_edge, edge_index)
				edge_index += write_edge_row('source', 'intermediary', trans, name_to_index_dict, csv_writer_edge, edge_index)
				edge_index += write_edge_row('intermediary', 'recipient', trans, name_to_index_dict, csv_writer_edge, edge_index)
				edge_index += write_edge_row('source', 'representative', trans, name_to_index_dict, csv_writer_edge, edge_index)
				edge_index += write_edge_row('representative', 'recipient', trans, name_to_index_dict, csv_writer_edge, edge_index)

				if dummy and len(trans.roles) == 1:
					# dummy node: only add it if actually need it for this text
					dummy_obj = Node(node_index, str(trans.p_index)+'_dummy')    # dummy node for this text: name = p index
					existing_nodes[node_index] = dummy_obj
					name_to_index_dict[dummy_obj.name] = node_index
					node_index += 1
					# csv_writer_node.writerow([len(existing_nodes), dummy_obj.name])
					if 'source' in trans.roles:
						csv_writer_edge.writerow([edge_index, name_to_index_dict[trans.roles['source'].name], node_index, 'Directed', 'source', 'dummy', trans.p_index])
						edge_index += 1
					if 'recipient' in trans.roles:
						csv_writer_edge.writerow([edge_index, node_index, name_to_index_dict[trans.roles['recipient'].name], 'Directed', 'dummy', 'recipient', trans.p_index])
						edge_index += 1

			# now write nodes
			for i, node_obj in sorted(existing_nodes.items(), key=lambda x: x[0]):
				csv_writer_node.writerow([i, node_obj.name, node_obj.roles, node_obj.professions, node_obj.processed_dates, node_obj.p_ids])

			# GN nodes (and edges)
			for node_obj in sorted(geo_nodes.values(), key=lambda x: x.index):
				csv_writer_node.writerow([node_obj.index, node_obj.name, [], [], [], []])
				for person_node_i, p_index in node_obj.people_node_indices:
					csv_writer_edge.writerow([edge_index, person_node_i, node_obj.index, 'Directed', '', 'GN', p_index])
					edge_index += 1

		# print(count_gn, 'transactions have geographical names, out of', len(all_trans))


all_trans = make_all_trans()
p_to_geo = make_geo_names_dict()
# print(p_to_geo)
make_node_edge_lists(all_trans, p_to_geo, True)















































