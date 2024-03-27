import toml
import sys
import logging
import sqlite3
from ZalDbUtils import *

if __name__ == "__main__":
    logger = logging.getLogger()
    with open('tables_fix.toml', mode='r') as f:
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

    fix_inflection_table(db_cursor, logger, output)
#    fix_second_genitive(db_cursor, logger, output)
    update_irregular_forms(db_cursor, logger, output)
    update_missing_and_difficult_forms(db_cursor, logger, output)
    update_second_locative(db_cursor, logger, output)

    db_connect.commit()
