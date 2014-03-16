
from mrjob.job import MRJob
from mrjob.runner import MRJobRunner
from datetime import datetime
import re
import numpy as np

class Information_Extraction(MRJob):

    def mapper_tick_value(self, _, tick):
        '''
        Extract price of every tick from the raw data
        Input: line of raw data file
        Output:
          key: string of date time (YYYY-MM-DD)
          value: value of the rate
        '''
        info_list = tick.split(",")
        date_pat = re.compile('[0-9]+-[0-9]+-[0-9]+')
        for idx in range(len(info_list)):
            try:
                yield date_pat.search(info_list[idx]).group(), float(info_list[idx+1])
                break
            except:
                pass

    def reducer_tick_value(self, date, rate):
        '''
        Find the highest, lowest, mean, and standard deviation of rate on a day
        '''
        rate = np.array(list(rate))
        yield date, [rate.max(), rate.min(), rate.mean(), rate.std()]

    def steps(self):
        return [self.mr(mapper = self.mapper_tick_value, \
                       reducer = self.reducer_tick_value)]


if __name__ == '__main__':
    Information_Extraction.run()
        # print 'haha', day, value
    # print test
    # for day_rate in Information_Extraction.stream_output():
    #     day, rate_list = MRJob.parse_output(day_rate)
    #     print day, rate_list