import sqlite3
from nlist import nlist


def create_table(database, table_name_raw, table_name_clean):
	'''
	create table_name_clean in database_pt
	Input:
		database: pointer to the database
		table_name_raw: original table with raw data
		table_name_clean: name of table to create
	'''
	##--create database pointer
	database_pt = database.cursor()
	##--drop the table
	sql_comm = 'drop table if exists %(table_name)s'%{'table_name': table_name_clean}
	database_pt.execute(sql_comm)
	##--creat new table
	sql_comm = 'create table %(table_name)s (tradeID INTEGER PRIMARY KEY AUTOINCREMENT, trade_date date)'\
		%{'table_name': table_name_clean}
	database_pt.execute(sql_comm)
	##--copy tradeID and trade_date from table_raw to table_clean
	sql_comm = 'update %(new_table)s set trade_date = (select trade_date from %(old_table)s where tradeID = %(old_table)s.tradeID)' \
		%{'new_table': table_name_clean, 'old_table': table_name_raw}
	database_pt.execute(sql_comm)
	database.commit()
	

def get_average(nlist_obj, n_period):
	'''
	Get the average value based on the value in previous 2, 3, 4, ..., and n_period days
	Input: 
		nlist_obj: nlist objective
	Output
		avg: list of slopes
	'''
	avg = []
	data_len = len(nlist_obj.element)
	for avg_length in xrange(2, n_period+1):
		if data_len >= avg_length:
			avg.append(sum(nlist_obj.element[:avg_length]) * 1. / avg_length)
	return avg

def get_talyer_slope(nlist_obj):
	'''
	Get slope based on Taylor expension
	Input:
		nlist_obj: nlist objective
	Output:
		slope: list of slope
	'''
	slope = []
	data_len = len(nlist_obj.element)
	for slope_length in xrange(2, 6):
		if data_len >= slope_length:
			if slope_length == 2:
				slope.append(nlist_obj.element[0] - nlist_obj.element[1])
			elif slope_length == 3:
				slope.append(2.5 * nlist_obj.element[0] - 4 * nlist_obj.element[1] + 1.5 * nlist_obj.element[2])
			elif slope_length == 4:
				slope.append(13./3. * nlist_obj.element[0] - 9.5 * nlist_obj.element[1] + 7 * nlist_obj.element[2] - 11./6. * nlist_obj.element[3])
			elif slope_length == 5:
				slope.append(77./12. * nlist_obj.element[0] - 107./6. * nlist_obj.element[1] + 39./2. * nlist_obj.element[2] - 61./6. * nlist_obj.element[3] + 25./12. * nlist_obj.element[4])
	return slope


def get_previous_data(database, table_name_raw, table_name_clean, n_period = 5):
	'''
	Extract information from table_name_raw and insert important information into table_name_clean
	Important information includes:
		highest, lowest, closing, mean, and std in previous n_period days
		average value of the highest, lowest, closing, mean, and std based on previous 2, 3, 4, and 5 days
		Slope of closing rate predicted by Taylor expansion based on previous 2, 3, 4, and 5 days.
	Input:
		database: the pointer of the database
		table_name_raw: table name with raw data
		table_name_clean: table name with result to put in
		n_period: important information based on previous n_period days
	Output:
		All the information will be output to table_name_clean
	'''
	##--create pointer to the database
	database_pt = database.cursor()
	##--get number of data from table
	sql_comm = 'select count(*) from %(table_name)s'%{'table_name': table_name_raw}
	database_pt.execute(sql_comm)
	data_num = int(database_pt.fetchone()[0])
	##--create column for high, low, mean, close, and std in previous several days
	pre_name_list = ['H', 'L', 'M', 'C', 'Std', 'HL']
	for pre_name in pre_name_list:
		for idx in xrange(n_period):
			sql_comm = 'alter table %(table_name)s add pre%(pre_name)s%(idx)s float' \
				%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx}
			database_pt.execute(sql_comm)
	database.commit()
	##--Create column for the average high, low, mean ,close, and std in previous several days
	for pre_name in pre_name_list[:-2]:
		for idx in xrange(2, n_period+1):
			sql_comm = 'alter table %(table_name)s add pre_avg_%(pre_name)s%(idx)s float' \
				%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx}
			database_pt.execute(sql_comm)
	database.commit()
	##--Create slope of close using rates in previous 2, 3, 4, and 5 days
	for idx in xrange(2, n_period+1):
		sql_comm = 'alter table %(table_name)s add pre_slope_C%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		database_pt.execute(sql_comm)
	database.commit()
	##--insert date to table
	sql_comm = 'insert into %(table_name)s (trade_date) select trade_date from %(old_table)s'%{'table_name': table_name_clean, \
		'old_table': table_name_raw}
	database_pt.execute(sql_comm)
	database_pt.execute('select * from %(table_name)s'%{'table_name': table_name_clean})
	database.commit()
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		if idx == 1:
			preH = nlist(n_period,line[2])
			preL = nlist(n_period,line[3])
			preM = nlist(n_period,line[4])
			preStd = nlist(n_period,line[5])
			preC = nlist(n_period,line[6])
			preHL = nlist(n_period,(line[2]+line[3])/2.)
		else:
			preH.add(line[2])
			preL.add(line[3])
			preM.add(line[4])
			preStd.add(line[5])
			preC.add(line[6])
			preHL.add((line[2]+line[3])/2.)
		length_pre = min(n_period,idx)
		for pre_name in pre_name_list:
			for i_idx in xrange(length_pre):
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
				elif pre_name == 'HL':
					value = preHL.element[i_idx]
				sql_comm = 'update %(table_name)s set pre%(pre_name)s%(i_idx)s = %(value)s \
					where tradeID = %(idx)s'%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx, \
					'i_idx': i_idx, 'value': value}			
				database_pt.execute(sql_comm)
		database.commit()
		##--insert average values
		pre_avg_H = get_average(preH, n_period)
		pre_avg_L = get_average(preL, n_period)
		pre_avg_M = get_average(preM, n_period)
		pre_avg_Std = get_average(preStd, n_period)
		pre_avg_C = get_average(preC, n_period)
		length_pre = min(n_period-1,idx-1)
		for pre_name in pre_name_list[:-2]:
			for i_idx in xrange(length_pre):
				if pre_name == 'H':
					value = pre_avg_H[i_idx]
				elif pre_name == 'L':
					value = pre_avg_L[i_idx]
				elif pre_name == 'M':
					value = pre_avg_M[i_idx]
				elif pre_name == 'Std':
					value = pre_avg_Std[i_idx]
				elif pre_name == 'C':
					value = pre_avg_C[i_idx]
				sql_comm = 'update %(table_name)s set pre_avg_%(pre_name)s%(i_idx)s = %(value)s \
					where tradeID = %(idx)s'%{'table_name': table_name_clean, 'pre_name': pre_name, 'idx': idx, \
					'i_idx': i_idx + 2, 'value': value}		
				database_pt.execute(sql_comm)						
		database.commit()
		##--insert taylor-expansion based slope
		pre_slope_C = get_talyer_slope(preC)
		length_pre = min(4,idx-1)
		for i_idx in xrange(length_pre):
			value = pre_slope_C[i_idx]
			sql_comm = 'update %(table_name)s set pre_slope_C%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': i_idx + 2, 'value': value}		
			database_pt.execute(sql_comm)						
		database.commit()



if __name__ == "__main__":
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        table_name = cur_pair + '_db'
        create_table(database, table_name, table_name+'clean')
        get_previous_data(database, table_name, table_name+'clean')
