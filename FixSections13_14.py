import toml
import logging
import sqlite3

if __name__ == "__main__":
    with open('AddSection13or14.toml', mode='r') as f:
        config = toml.load(f)

    db_path = config['paths']['db_path_windows']
#    output_path = config['paths']['output_path_windows']

    db_connect = sqlite3.connect(db_path)
    db_read_cursor = db_connect.cursor()

    i_query = '''SELECT i.id, hw.source FROM headword AS hw INNER JOIN descriptor AS d ON d.word_id=hw.id 
                 INNER JOIN inflection AS i ON i.descriptor_id=d.id  
                 WHERE d.inflection_type='п' AND i.accent_type2 > 0
                 AND (d.main_symbol='мо' OR d.main_symbol='м');'''
    db_read_cursor.execute(i_query)
    i_rows = db_read_cursor.fetchall()

    update_query = '''UPDATE inflection 
                      SET accent_type2 = 0 
                      WHERE id = {}'''
    db_write_cursor = db_connect.cursor()

    for i_row in i_rows:
        i_id = i_row[0]
        db_write_cursor.execute(update_query.format(i_id))
        print(i_row[1])

    db_connect.commit()

    print('Done.')
