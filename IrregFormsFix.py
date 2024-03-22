import toml
import sys
import logging
import sqlite3
from RefactorTables.ZalDbUtils import *

if __name__ == "__main__":
    logger = logging.getLogger()
    with open('irreg_forms_table_fix.toml', mode='r') as f:
        config = toml.load(f)
    db_path = config['paths']['db_path_windows']
    out_path = config['paths']['output_path']

    output = open(out_path, mode='w', encoding='UTF-8')

    try:
        db_connect = sqlite3.connect(db_path)
        db_cursor = db_connect.cursor()
    except Exception as e:
        logger.error('Failed to connect to DB: {}.'.format(e))
        sys.exit()

    create_new_tables(db_cursor)
    update_irregular_forms(db_cursor, logger, output)
    rename_new_tables(db_cursor, logger)

    db_connect.commit()
