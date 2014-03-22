import sqlite3
from nlist import nlist
import numpy as np

def get_arn(nlist_obj, point_number_list):
	'''
	Get the aroon up and down values based on the values in previous days with number listed in point_number_list
	Input: 
		nlist_obj: nlist objective
		point_number_list: list of number of point used in linear regression model
	Output
		arn: list of [ aroon up, aroon down ]
	'''
	arn = []
	data_len = len(nlist_obj.element)
	for arn_length in point_number_list:
		if data_len >= arn_length:
			c_max = max(nlist_obj.element[:arn_length])
			c_min = min(nlist_obj.element[:arn_length])
			n_max = nlist_obj.element.index(c_max)
			n_min = nlist_obj.element.index(c_min)
			arn.append([(arn_length - n_max) * 100. / arn_length, (arn_length - n_min) * 100. / arn_length])
	return arn

def get_tr(cur_high, cur_low, pre_c):
	'''
	Get the true range based on the values in previous days with number listed in point_number_list
	Input: 
		cur_high: current high
		cur_low: current low
		pre_c: previous close
	Output
		tr: true range
	'''
	return max(cur_high - cur_low, abs(cur_high - pre_c), abs(cur_low - pre_c))

def get_tp(cur_high, cur_low, cur_close):
	'''
	Get the true price based on the values in previous days with number listed in point_number_list
	Input: 
		cur_high: current high
		cur_low: current low
		cur_close: current close
	Output
		tr: true range
	'''
	return ( cur_high + cur_low + cur_close ) / 3.


def get_wcp(cur_high, cur_low, cur_close):
	'''
	Get the true price based on the values in previous days with number listed in point_number_list
	Input: 
		cur_high: current high
		cur_low: current low
		cur_close: current close
	Output
		wcp: weighted close price
	'''
	return ( cur_high + cur_low + cur_close * 2. ) / 4.


def get_fi_p1_data(database, table_name_raw, table_name_clean, point_number_arn_list=[5, 10, 25], n_tr = 5, n_tp = 5, n_wcp = 5):
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
	##--get number of data from table and maximum number needed for the linear regression
	sql_comm = 'select count(*) from %(table_name)s'%{'table_name': table_name_raw}
	database_pt.execute(sql_comm)
	data_num = int(database_pt.fetchone()[0])
	##--create column for the aroon up and down in previous several days
	point_number_max = max(point_number_arn_list)
	for idx in point_number_arn_list:
		sql_comm = 'alter table %(table_name)s add pre_fi_arnup%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
	database.commit()
	for idx in point_number_arn_list:
		sql_comm = 'alter table %(table_name)s add pre_fi_arndown%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
	database.commit()
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		if idx == 1:
			preC = nlist(point_number_max,line[6])
		else:
			preC.add(line[6])
		arn_list = get_arn(preC, point_number_arn_list)
		for i_idx in xrange(len(arn_list)):
			value = arn_list[i_idx][0]
			sql_comm = 'update %(table_name)s set pre_fi_arnup%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_arn_list[i_idx], 'value': value}
			database_pt.execute(sql_comm)
			value = arn_list[i_idx][1]
			sql_comm = 'update %(table_name)s set pre_fi_arndown%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_arn_list[i_idx], 'value': value}
			database_pt.execute(sql_comm)
		database.commit()
	##--create column for true range in previous several days
	for idx in xrange(n_tr):
		sql_comm = 'alter table %(table_name)s add pre_fi_tr%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
	database.commit()
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		if idx == 1:
			preC = line[6]
		else:
			curH = line[2]
			curL = line[3]
			if idx == 2:
				preTR = nlist(n_tr, get_tr(curH, curL, preC))
			else:
				preTR.add(get_tr(curH, curL, preC))
			for i_idx in xrange(min(n_tr, len(preTR.element))):	
				sql_comm = 'update %(table_name)s set pre_fi_tr%(i_idx)s = %(value)s \
					where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
					'i_idx': i_idx, 'value': preTR.element[i_idx]}		
				database_pt.execute(sql_comm)
			preC = line[6]
	database.commit()
	##--create column for true price in previous several days
	for idx in xrange(n_tp):
		sql_comm = 'alter table %(table_name)s add pre_fi_tp%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
	database.commit()
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		curC = line[6]
		curH = line[2]
		curL = line[3]
		if idx == 1:
			preTP = nlist(n_tp, get_tp(curH, curL, curC))
		else:
			preTP.add(get_tp(curH, curL, curC))
		for i_idx in xrange(min(n_tp, len(preTP.element))):	
			sql_comm = 'update %(table_name)s set pre_fi_tp%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': i_idx, 'value': preTP.element[i_idx]}		
			database_pt.execute(sql_comm)
	database.commit()
	##--create column for weighted closing price in previous several days
	for idx in xrange(n_wcp):
		sql_comm = 'alter table %(table_name)s add pre_fi_wcp%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
	database.commit()
	##--insert data into database
	for idx in xrange(1,data_num+1):
		sql_comm = 'select * from %(table_name)s where tradeID = %(id)s'%{'table_name': table_name_raw, 'id': idx}
		database_pt.execute(sql_comm)
		line = database_pt.fetchone()
		curC = line[6]
		curH = line[2]
		curL = line[3]
		if idx == 1:
			preWCP = nlist(n_wcp, get_wcp(curH, curL, curC))
		else:
			preWCP.add(get_wcp(curH, curL, curC))
		for i_idx in xrange(min(n_wcp, len(preWCP.element))):	
			sql_comm = 'update %(table_name)s set pre_fi_wcp%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': i_idx, 'value': preWCP.element[i_idx]}		
			database_pt.execute(sql_comm)
	database.commit()



if __name__ == "__main__":
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        table_name = cur_pair + '_db'
        get_fi_p1_data(database, table_name, table_name+'clean')
#        get_previous_data(database, table_name, table_name+'clean')
