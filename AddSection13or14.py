import toml
import logging
import sqlite3


if __name__== "__main__":
    with open('AddSection13or14.toml', mode='r') as f:
        config = toml.load(f)

    db_path = config['paths']['db_path_windows']
    output_path = config['paths']['output_path_windows']

    out_file = open(output_path, mode='w', encoding='utf-8')
    
    db_connect = sqlite3.connect(db_path)
    db_read_cursor = db_connect.cursor()

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

    print ('Done.')
