import toml
import logging
import sqlite3
import ctypes
import os

def add(config, zal_lib):
    headwords_to_add = config['data']['add']
    if len(headwords_to_add) > 0:
        print('--- Adding test entries')
        for headword in headwords_to_add:
            print(f'{headword}')
            zal_lib.bDeleteRegressionData(headword)
            zal_lib.bSaveRegressionData(headword)
    else:
        print('\n--- Nothing to add')

def remove(config, zal_lib):
    headwords_to_remove = config['data']['remove']
    if len(headwords_to_remove) > 0:
        print('--- Removing test entries')
        for headword in headwords_to_remove:
            print(f'{headword}')
            zal_lib.bDeleteRegressionData(headword)
    else:
        print('\n--- Nothing to remove')

def run():
    return True

if __name__== "__main__":
    with open('ZalTest.toml', mode='r', encoding='utf-8') as f:
        config = toml.load(f)

    lib_path = config['paths']['lib_path_windows']
    db_path = config['paths']['db_path_windows']
    zal_lib = ctypes.cdll.LoadLibrary(lib_path)
    if zal_lib is None:
        print('*** Unable to load Zal engine.')
        os._exit(1)
    ret = zal_lib.Init(db_path)
    if not ret:
        print('*** Unable to initialize Zal engine.')
        os._exit(1)

    add(config, zal_lib)
    remove(config, zal_lib)
