import sqlite3
from nlist import nlist
from sklearn.linear_model import LinearRegression
import numpy as np

def get_lr_slope(nlist_obj, point_number_list):
	'''
	Get the slope from linear regression based on the values in previous days with number listed in point_number_list
	Input: 
		nlist_obj: nlist objective
		point_number_list: list of number of point used in linear regression model
	Output
		slope: list of slopes
	'''
	lr_slope = []
	data_len = len(nlist_obj.element)
	lr_model = LinearRegression()
	for lr_length in point_number_list:
		if data_len >= lr_length:
			lr_model.fit(np.array([[i] for i in range(lr_length)]), np.array([[nlist_obj.element[i]] for i in range(data_len-lr_length, data_len)]))
			lr_slope.append(lr_model.coef_[0,0])
	return lr_slope


def get_lr_data(database, table_name_raw, table_name_clean, point_number_list=[3, 4, 5, 10, 20, 30]):
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
	pointer_number_max = max(point_number_list)
	##--create column for high, low, mean, close, and std in previous several days
	for idx in point_number_list:
		sql_comm = 'alter table %(table_name)s add pre_lr_slope_C%(idx)s float' \
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
			preC = nlist(pointer_number_max,line[6])
		else:
			preC.add(line[6])
		lr_slope_list = get_lr_slope(preC, point_number_list)
		for i_idx in xrange(len(lr_slope_list)):
			value = lr_slope_list[i_idx]
			sql_comm = 'update %(table_name)s set pre_lr_slope_C%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_list[i_idx], 'value': value}		
			database_pt.execute(sql_comm)						
		database.commit()



if __name__ == "__main__":
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        table_name = cur_pair + '_db'
        get_lr_data(database, table_name, table_name+'clean')
#        get_previous_data(database, table_name, table_name+'clean')
