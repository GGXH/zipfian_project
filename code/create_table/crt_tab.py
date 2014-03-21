import re
import sqlite3
import sys

def put_data_into_table(table_name, database_pointer, cur_pair):
    '''
    create a table to store highest, lowest, mean, standard deviation, and close rate per day
    Input:
        table_name: name of the table
        database_pointer: pointer to the database
        cur_pair: currency pair
    '''
    year_list = range(2004,2015)
    date_pat = re.compile('[0-9]+-[0-9]+-[0-9]+')
    for year in year_list:
        with open('../../data/%(cur_pair)s/clean/%(cur_pair)s_%(year)s' %{'cur_pair': cur_pair, 'year': year}) as fl:
            # print cur_pair, year
            for line in fl.readlines():
                date, rate_list = line.split('\t')
                rate_list = rate_list.replace('[','').replace(']','').replace('\n','').split(',')
                # if cur_pair == 'EUR_USD':
                #     print rate_list
                database_pointer.execute('insert into %(table_name)s (trade_date, highest_rate, lowest, mean, std, close_rate) values(%(date)s, %(high_rate)s, %(low_rate)s, %(mean_rate)s, %(std_rate)s, %(close_rate)s)'%{'table_name': table_name, 'date': date, 'high_rate': rate_list[0], \
                    'low_rate': rate_list[1], 'mean_rate': rate_list[2], 'std_rate': rate_list[3], \
                    'close_rate': rate_list[4]})


if __name__ == '__main__':
    database = sqlite3.connect('../../data/clean_data.db')
    database_pointer = database.cursor()
    cur_pair_list = ['USD_JPY', 'GBP_USD', 'EUR_USD']
    for cur_pair in cur_pair_list:
        # print cur_pair
        table_name = cur_pair + '_db'
        # print table_name
        database_pointer.execute('drop table if exists %s' %table_name)
        database_pointer.execute('create table %s(tradeID INTEGER PRIMARY KEY AUTOINCREMENT, trade_date date, highest_rate float, lowest float, mean float, std float, \
         close_rate float)'%table_name)
        put_data_into_table(table_name, database_pointer, cur_pair)
        database.commit()
        database_pointer.execute('select count(*) from %s'%table_name)
        print database_pointer.fetchone()
    # print cur_pair_list
