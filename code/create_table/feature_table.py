import sqlite3

class nlist():

	def __init__(self, n, element):
		self.n = n
		self.element = [element]

	def add(self,element):
		if len(self.element) < self.n:
			self.element.append(element)
		else:
			self.element.pop(0)
			self.element.append(element)

def create_table(database_pt, table_name_raw, table_name_clean):
	'''
	create table_name_clean in database_pt
	Input:
		database_pt: pointer to the database
		table_name_raw: original table with raw data
		table_name_clean: name of table to create
	'''
	##--drop the table
	sql_comm = 'drop table if exists %(table_name)s'%{'table_name': table_name_clean}
	database_pt.execute(sql_comm)
	##--creat new table
	sql_comm = 'create table %(table_name)s (tradeID INTEGER PRIMARY KEY AUTOINCREMENT, trade_date date)'\
		%{'table_name': table_name_clean}
	database_pt.execute(sql_comm)
	##--copy tradeID and trade_date from table_raw to table_clean
	# sql_comm = 'select tradeID, trade_date into %(new_table)s from %(old_table)s' \
		# %{'new_table': table_name_clean, 'old_table': table_name_raw}
	sql_comm = 'update %(new_table)s set trade_date = (select trade_date from %(old_table)s where tradeID = %(old_table)s.tradeID)' \
		%{'new_table': table_name_clean, 'old_table': table_name_raw}
	database_pt.execute(sql_comm)
	# database_pt.execute('select count(*) from %(table_name)s'%{'table_name': table_name_raw})
	# # sql_comm = 'select trade_date from %(old_table)s' \
	# # 	%{'new_table': table_name_clean, 'old_table': table_name_raw}
	# # database_pt.execute(sql_comm)
	# print database_pt.fetchone()
	


def get_previous_data(database_pt, table_name_raw, table_name_clean, n_period = 5):
	'''

	'''
	##--get number of data from table
	sql_comm = 'select count(*) from %(table_name)s'%{'table_name': table_name_raw}
	database_pt.execute(sql_comm)
	data_num = int(database_pt.fetchone()[0])
	##--create column for high, low, mean, close, and std in previous several days
	pre_name_list = ['H', 'L', 'M', 'C', 'Std']
	for pre_name in pre_name_list:
		for idx in xrange(5):
			sql_comm = 'alter table %(table_name)s add pre%(pre_name)s%(idx)s float' \
				%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx}
			database_pt.execute(sql_comm)
	# sql_comm = 'alter table %(table_name)s add preH1 float, preH2 float, preH3 float, preH4 float, preH5 float, \
	# 			preL1 float, preL2 float, preL3 float, preL4 float, preL5 float, \
	# 			preM1 float, preM2 float, preM3 float, preM4 float, preM5 float, \
	# 			preC1 float, preC2 float, preC3 float, preC4 float, preC5 float, \
	# 			preStd1 float, preStd2 float, preStd3 float, preStd4 float, preStd5 float' \
	# 			%{'table_name': table_name_clean}
	# database_pt.execute(sql_comm)
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		print line
		if idx == 1:
			preH = nlist(5,line[2])
			preL = nlist(5,line[3])
			preM = nlist(5,line[4])
			preStd = nlist(5,line[5])
			preC = nlist(5,line[6])
		else:
			preH.add(line[2])
			preL.add(line[3])
			preM.add(line[4])
			preStd.add(line[5])
			preC.add(line[6])
			if idx >= 5:
				for pre_name in pre_name_list:
					for i_idx in xrange(5):
						if pre_name == 'H':
							value = preH.element[i_idx]
						elif pre_name == 'L':
							value = preL.element[i_idx]
						elif pre_name == 'M':
							value = preM.element[i_idx]
						elif pre_name == 'Std':
							value = preStd.element[i_idx]
						elif pre_name == 'C':
							value = preC.element[i_idx]
						sql_comm = 'update %(table_name)s set pre%(pre_name)s%(i_idx)s = %(value)s \
						where %(table_name)s.tradeID = %(idx)s'%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx, \
						'i_idx': i_idx, 'value': value}		
						# print sql_comm		
						database_pt.execute(sql_comm)
				# sql_comm = 'update %(table_name)s \
				# 	set preH1 = %(preH1)s, preH2 = %(preH2)s, preH3 = %(preH3)s, preH4 = %(preH4)s, preH5 = %(preH5)s, \
				# 	preL1 = %(preL1)s, preL2 = %(preL2)s, preL3 = %(preL3)s, preL4 = %(preL4)s, preL5 = %(preL5)s, \
				# 	preM1 = %(preM1)s, preM2 = %(preM2)s, preM3 = %(preM3)s, preM4 = %(preM4)s, preM5 = %(preM5)s, \
				# 	preC1 = %(preC1)s, preC2 = %(preC2)s, preC3 = %(preC3)s, preC4 = %(preC4)s, preC5 = %(preC5)s, \
				# 	preStd1 = %(preStd1)s, preStd2 = %(preStd2)s, preStd3 = %(preStd3)s, preStd4 = %(preStd4)s, \
				# 	preStd5 = %(preStd5)s'%{'table_name': table_name_clean, 'preH1': preH.element[0], \
				# 	'preH2': preH.element[1], 'preH3': preH.element[2], 'preH4': preH.element[3], 'preH5': preH.element[4], \
				# 	'preL1': preL.element[0], 'preL2': preL.element[1], 'preL3': preL.element[2], 'preL4': preL.element[3], \
				# 	'preL5': preL.element[4], 'preM1': preM.element[0], 'preM2': preM.element[1], 'preM3': preM.element[2], \
				# 	'preM4': preM.element[3], 'preM5': preM.element[4], 'preC1': preC.element[0], 'preC2': preC.element[1], \
				# 	'preC3': preC.element[2], 'preC4': preC.element[3], 'preC5': preC.element[4], 'preStd1': preStd.element[0], \
				# 	'preStd2': preStd.element[1], 'preStd3': preStd.element[2], 'preStd4': preStd.element[3], \
				# 	'preStd5': preStd.element[4]}
				# database_pt.execute(sql_comm)


if __name__ == "__main__":
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        # print cur_pair
        table_name = cur_pair + '_db'
        create_table(database_pointer, table_name, table_name+'clean')
        get_previous_data(database_pointer, table_name, table_name+'clean')
        database_pointer.execute('select * from %(table_name)s'%{'table_name': table_name+'clean'})
        print database_pointer.fetchone()
