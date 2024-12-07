import toml
import logging
import sqlite3
import csv
from collections import namedtuple

def get_part_of_speech(db_read_cursor, lex_hash):
    pos_query = f'''SELECT DISTINCT hw.source, d.inflection_type FROM lexeme_hash_to_descriptor AS lhtd 
                   INNER JOIN descriptor AS d ON d.id = lhtd.descriptor_id 
                   INNER JOIN headword AS hw ON d.word_id=hw.id 
                   WHERE lhtd.lexeme_hash='{lex_hash}';'''
    part_of_speech = ''
    db_read_cursor.execute(pos_query)
    lex_rows = db_read_cursor.fetchall()
    if len(lex_rows) < 1:
        print(f'No descriptor for lex hash {lex_hash}')
    else:
        for row in lex_rows:
            print(f'{row[0]} ----> {row[1]}')
        part_of_speech = row[1]

    return True, part_of_speech

def insert_wf(db_write_cursor, values):
    return True, ''

if __name__== "__main__":
    with open('ConvertTestData.toml', mode='r') as f:
        config = toml.load(f)

    db_path = config['paths']['db_path_windows']
    output_path = config['paths']['output_path_windows']
    csv_path_wordforms = config['paths']['wf_input_path']
    csv_path_stress = config['paths']['stress_input_path']

    out_file = open(output_path, mode='w', encoding='utf-8')
    csv_file_wf = open(csv_path_wordforms, mode='r', encoding='utf-16-le')
    csv_file_stress = open(csv_path_stress, mode='r', encoding='utf-16-le')

    db_connect = sqlite3.connect(db_path)
    db_read_cursor = db_connect.cursor()
    db_write_cursor = db_connect.cursor()
    db_write_cursor_stress = db_connect.cursor()

    csv_reader_wf = csv.DictReader(csv_file_wf, delimiter='|', fieldnames=['id', 'lexeme_id', 'gram_hash', 'wordform'])
    csv_reader_stress = csv.DictReader(csv_file_stress, delimiter='|', fieldnames=['id', 'test_data_id', 'position', 'is_primary'])

    insert_query = 'INSERT INTO test_data (paradigm_hash, part_of_speech, gram_hash, wordform) \
                    VALUES (?,?,?,?)'

    insert_stress_query = 'INSERT INTO test_data_stress (test_data_id, position, is_primary) \
                           VALUES (?,?,?)'
    fields = []
    wf_rows = []
    stress_rows = {}        # wf.id --> stress data

    for row in csv_reader_wf:
        wf_rows.append(row)

    wf_rows.pop(0)

    for wf_row in wf_rows:
        ret, pos = get_part_of_speech(db_read_cursor, wf_row['lexeme_id'])
        wf_row['part_of_speech'] = pos
        koko = 'jj'

    for stress_row in csv_reader_stress:
        stress_rows[stress_row['test_data_id']] = stress_row

    for wf_row in wf_rows:
        values = (wf_row['lexeme_id'], wf_row['part_of_speech'], wf_row['gram_hash'], wf_row['wordform'])
        db_write_cursor.execute(insert_query, values)
        new_id = db_write_cursor.lastrowid
        stress_row = stress_rows[wf_row['id']]
        stress_values = (new_id, stress_row['position'], stress_row['is_primary'])
        db_write_cursor.execute(insert_stress_query, stress_values)

    db_connect.commit()



    print(f"Read {csv_reader_wf.line_num} rows")

"""
    d_query = '''SELECT hw.source, d.main_symbol, d.id, d.is_intransitive, d.is_reflexive, i.inflection_type FROM descriptor AS d \
                 INNER JOIN headword AS hw ON hw.id=d.word_id INNER JOIN inflection AS i ON i.descriptor_id = d.id WHERE d.section = 13;'''
    db_read_cursor.execute(d_query)
    d_rows = db_read_cursor.fetchall()

    i_insert_query = 'INSERT INTO inflection \
                      (descriptor_id, is_primary, inflection_type, accent_type1, accent_type2, short_form_restrictions, \
                      past_part_restrictions, no_short_form, no_past_part, fleeting_vowel, stem_augment, second_genitive, \
                      comment, is_edited) \
                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    db_write_cursor = db_connect.cursor()                      

    for d_row in d_rows:
        descr_id = d_row[2]
        part_pass_past_restricted = not d_row[3] and not d_row[4]   # only applicable to transitives
        inflection_type = 1 if d_row[5] == 6 else 6

        values = (descr_id,    1,          inflection_type,      1,  0,     0,           0, 0, 0, 0, 0, 0, '', 1)
#                  descr    is_primary         infl_type        at1 at2 short_form_restr
        
        db_write_cursor.execute(i_insert_query, values)
#        new_id = db_write_cursor.lastrowid
        print ('{}: main symbol = {}, part_pass_past_restricted = {}'.format(d_row[0], d_row[1], part_pass_past_restricted),
               file=out_file)

    db_connect.commit()
"""

print ('Done.')
