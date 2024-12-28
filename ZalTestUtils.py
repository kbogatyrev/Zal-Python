import toml
import re
import ctypes
import os


def run():
    return True

if __name__== "__main__":
    with open('ZalTestUtils.toml', mode='r') as f:
        config = toml.load(f)

    source_path = config['paths']['source_path']
    lib_path = config['paths']['lib_path_windows']
    db_path = config['paths']['db_path_windows']
    output_path = config['paths']['output_path_windows']

    zal_lib = ctypes.cdll.LoadLibrary(lib_path)
    if zal_lib is None:
        print('*** Unable to load Zal engine.')
        os._exit(1)

    ret = zal_lib.Init(db_path)
    if not ret:
        print('*** Unable to initialize Zal engine.')
        os._exit(1)

    out_file = open(output_path, mode='w', encoding='utf-8')

    count = 0;

    with open(source_path, 'r', encoding='utf-16') as source:
        for line in source:
            match = re.search(r"Noun_Sg_N\|(.+)\n|Inf\|(.+)\n", line)
#            match = re.search(r"Noun_Sg_N\|(.+)\n|AdjL_M_Sg_N\|(.+)\n", line)
            headword = ''
            if match:
                headword = match.group(1)
                if not headword:
                    headword = match.group(2)

            if headword:
                zal_lib.bDeleteRegressionData(headword)
                zal_lib.bSaveRegressionData(headword)
                print(headword)
                count += 1

    print(f'\nAdded {count} test records.')
