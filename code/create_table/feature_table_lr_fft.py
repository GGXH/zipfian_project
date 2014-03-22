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
			lr_model.fit(np.array([[lr_length - i] for i in xrange(lr_length)]), np.array([[nlist_obj.element[i]] for i in xrange(lr_length)]))
			lr_slope.append(lr_model.coef_[0,0])
	return lr_slope

def get_fft(nlist_obj, point_number_list):
	'''
	Get the amplitude and wave phase from fft based on the values in previous days with number listed in point_number_list
	Input: 
		nlist_obj: nlist objective
		point_number_list: list of number of point used in fft
	Output
		fft_result: list of amplitude and theta of fft
	'''
	fft_result = []
	data_len = len(nlist_obj.element)
	for fft_length in point_number_list:
		if data_len >= fft_length:
			fft = np.fft.fft([nlist_obj.element[i] for i in xrange(fft_length)])[1]
			fft_result.append([abs(fft), np.angle(fft)])
	return fft_result


def get_lr_fft_data(database, table_name_raw, table_name_clean, point_number_lr_list=[3, 4, 5, 10, 20, 30], point_number_fft_list=[2, 4, 6, 8, 10, 20, 30]):
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
	##--create column for the slopes of linear regression in previous several days
	point_number_max = max(point_number_lr_list)
	for idx in point_number_lr_list:
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
			preC = nlist(point_number_max,line[6])
		else:
			preC.add(line[6])
		lr_slope_list = get_lr_slope(preC, point_number_lr_list)
		for i_idx in xrange(len(lr_slope_list)):
			value = lr_slope_list[i_idx]
			sql_comm = 'update %(table_name)s set pre_lr_slope_C%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_lr_list[i_idx], 'value': value}		
			database_pt.execute(sql_comm)						
		database.commit()
	##--create column for the slopes of linear regression in previous several days
	point_number_max = max(point_number_fft_list)
	for idx in point_number_fft_list:
		sql_comm = 'alter table %(table_name)s add pre_fft_amp%(idx)s float' \
			%{'table_name': table_name_clean, 'idx': idx}
		try:
			database_pt.execute(sql_comm)
		except:
			pass
		sql_comm = 'alter table %(table_name)s add pre_fft_theta%(idx)s float' \
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
		fft_result = get_fft(preC, point_number_fft_list)
		for i_idx in xrange(len(fft_result)):
			value = fft_result[i_idx]
			sql_comm = 'update %(table_name)s set pre_fft_amp%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_fft_list[i_idx], 'value': value[0]}		
			database_pt.execute(sql_comm)
			sql_comm = 'update %(table_name)s set pre_fft_theta%(i_idx)s = %(value)s \
				where tradeID = %(idx)s'%{'table_name': table_name_clean, 'idx': idx, \
				'i_idx': point_number_fft_list[i_idx], 'value': value[1]}		
			database_pt.execute(sql_comm)				
	database.commit()



if __name__ == "__main__":
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        table_name = cur_pair + '_db'
        get_lr_fft_data(database, table_name, table_name+'clean')
#        get_previous_data(database, table_name, table_name+'clean')
