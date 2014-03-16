import glob

def rewrite_binary(address):
    '''
    Rewrite binary files into ascii csv files
    Input:
        address(string): Address contain binary files
    Output:
        write the ascii csv files into the same address
    '''
    for file_name in glob.glob(address+'/200[8,9]/*/*.csv'):
        with open(file_name, "rb") as f:
            with open(file_name[:-4]+'as'+file_name[-4:], 'w') as f_asc:
                byte = f.readline()
                while byte != "":
                    int_str = map(ord,byte)
                    result_string = ""
                    for item in int_str:
                        if item != 0 and item != 255 and item != 254:
                            result_string += chr(item)
                    f_asc.write(result_string)
                    byte = f.readline()

if __name__ == '__main__':
    rewrite_binary('/Users/xinguo/zipfian/project/data/EUR_USD')
    rewrite_binary('/Users/xinguo/zipfian/project/data/GBP_USD')