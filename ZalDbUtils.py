import logging
import sys
import sqlite3
import codecs

def find_multiple_inflections(cursor, output, logger):
    try:
        descriptor_ids = []
        d_ids = []
        cursor.execute('''SELECT id FROM descriptor;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            descriptor_id = result[0]
            d_ids.append(descriptor_id)

        count = 0
        words = {}
        for id in d_ids:
            cursor.execute(f'''SELECT COUNT(*) FROM inflection WHERE descriptor_id = {id}''')
#            num_infl_rows = cursor.fetchall()
            for num_infl in cursor:
                if num_infl[0] > 1:
                    count += 1
                    cursor.execute(f'''SELECT d.id, hw.source FROM headword AS hw INNER JOIN descriptor AS d ON d.word_id = hw.id WHERE d.id = {id}''')
                    sources = cursor.fetchall()
                    for source in sources:
                        print(f'{source[0]}, {source[1]}', file=output)
                        words[source[0]] = source[1]
#                        words.sort()
        print(f'Total: {count}', file=output)
        for key, value in words:
            print(key, value)
    except Exception as e:
        logger.error(f'Exception trying to retrieve inflection entry: {e}.')
        sys.exit()

def find_multiple_inflections_details(cursor, output, logger):
    try:
        descriptor_ids = []
        d_ids = []
        cursor.execute('''SELECT id FROM descriptor;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            descriptor_id = result[0]
            d_ids.append(descriptor_id)

        count = 0
        words = {}
        for id in d_ids:
            cursor.execute(f'''SELECT COUNT(*) FROM inflection WHERE descriptor_id = {id}''')
#            num_infl_rows = cursor.fetchall()
            for num_infl in cursor:
                if num_infl[0] > 1:
                    count += 1
                    cursor.execute(f'''SELECT d.id, hw.source FROM headword AS hw INNER JOIN descriptor AS d ON d.word_id = hw.id WHERE d.id = {id}''')
                    sources = cursor.fetchall()
                    for source in sources:
                        print(f'{source[0]}, {source[1]}', file=output)
                        words[source[0]] = source[1]
#                        words.sort()
        print(f'Total: {count}', file=output)
        for key, value in words:
            print(key, value)
    except Exception as e:
        logger.error(f'Exception trying to retrieve inflection entry: {e}.')
        sys.exit()

def find_missing_inflections(cursor, logger, output):
    try:
        d_id_to_hw = {}
        cursor.execute('''SELECT d.id, hw.source FROM headword AS hw INNER JOIN descriptor AS d on d.word_id=hw.id;''')
        result_rows = cursor.fetchall()
        for row in result_rows:
            d_id_to_hw[row[0]] = row[1]
#            print(descriptor_id)

#        unique_descriptor_ids = set(descriptor_ids)

        count = 0;
        d_ids_no_infl = []
        for d_id in d_id_to_hw:
            cursor.execute((f'SELECT * FROM inflection WHERE descriptor_id = {d_id}'))
            result_rows = cursor.fetchall()
            if len(result_rows) < 1:
                count += 1
                d_ids_no_infl.append(int(d_id))
#                print(f'Descriptor {d_id} has no matching inflection entry.')
#                print(d_id)
        d_ids_no_infl.sort()
        print(f'Descriptors with missing inflection entries: {count}.', file=output)
        for idx in range(len(d_ids_no_infl)):
            d_id = d_ids_no_infl[idx]
            print(f'{d_id}: {d_id_to_hw[d_id]}', file=output)

    except Exception as e:
        logger.error(f'Exception while retrieving inflection entry: {e}.')
        sys.exit()

    return True

def find_missing_inflections_irregular_forms(cursor, logger, output):
    try:
        descriptor_ids = []
        cursor.execute('''SELECT id, descriptor_id FROM irregular_forms;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            form_id = result[0]
            descriptor_id = result[1]
            descriptor_ids.append(int(descriptor_id))
#            print(descriptor_id)

        unique_descriptor_ids = set(descriptor_ids)

        count = 0;
        ids_with_no_infl = []
        for d_id in unique_descriptor_ids:
            cursor.execute((f'SELECT * FROM inflection WHERE descriptor_id = {d_id}'))
            result_rows = cursor.fetchall()
            if len(result_rows) < 1:
                count += 1
                ids_with_no_infl.append(int(d_id))
#                print(f'Descriptor {d_id} has no matching inflection entry.')
#                print(d_id)
        ids_with_no_infl.sort()
        print(f'Descriptors with missing inflection entries: {count}.', file=output)
        for idx in range(len(ids_with_no_infl)):
            print(ids_with_no_infl[idx])

    except Exception as e:
        logger.error(f'Exception while retrieving inflection entry: {e}.')
        sys.exit()

    return True

def check_multiple_irreg_inflections(cursor, logger, output):
    try:
# TODO: use toml
        with open(r'C:\git-repos\zal\Zal-Data\ZalData\mult_inf.txt', encoding='UTF-8') as m:
            for line in m.readlines():
                descriptor = line.split()[0]
                cursor.execute((f'''SELECT * FROM irregular_forms WHERE descriptor_id = {descriptor}'''))
                result_rows = cursor.fetchall()
                if len(result_rows) > 0:
                    print(descriptor)

    except Exception as e:
        logger.error(f'Exception while retrieving inflection entry: {e}.')
        sys.exit()

    return True

def create_new_tables(cursor):
    cursor.execute('''CREATE TABLE irregular_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, gram_hash TEXT, wordform TEXT, 
                      is_alternative BOOLEAN DEFAULT (0), lead_comment TEXT, trailing_comment TEXT, is_edited BOOLEAN DEFAULT(0));''')
    cursor.execute('''CREATE TABLE irregular_stress_NEW (id INTEGER PRIMARY KEY ASC, form_id INTEGER, position INTEGER, 
                      is_primary BOOLEAN, is_edited BOOLEAN DEFAULT(0), FOREIGN KEY(form_id) REFERENCES irregular_forms(id));''')
    cursor.execute('''CREATE TABLE irregular_forms_spryazh_sm_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, gram_hash TEXT, 
                      wordform TEXT, is_alternative BOOLEAN DEFAULT (0), lead_comment TEXT, trailing_comment TEXT, is_edited BOOLEAN DEFAULT(0));''')
    cursor.execute('''CREATE TABLE irregular_stress_spryazh_sm_NEW (id INTEGER PRIMARY KEY ASC, form_id INTEGER, position INTEGER, 
                      is_primary BOOLEAN, is_edited BOOLEAN DEFAULT(0), FOREIGN KEY(form_id) REFERENCES irregular_forms(id));''')
    cursor.execute('''CREATE TABLE missing_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, content TEXT);''')
    cursor.execute('''CREATE TABLE difficult_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, content TEXT);''')
    cursor.execute('''CREATE TABLE second_genitive_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, is_edited BOOLEAN DEFAULT(0));''')
    cursor.execute('''CREATE TABLE second_locative_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, is_ptional BOOLEAN DEFAULT(0), 
                      preposition TEXT, is_edited BOOLEAN(0));''')

def update_irregular_forms(cursor, logger, output):
    exceptions = 0

    for irreg_forms_table in ['irregular_forms', 'irregular_forms_spryazh_sm']:
        irreg_stress_table = 'irregular_stress' if 'irregular_forms' == irreg_forms_table else 'irregular_stress_spryazh_sm'
        cursor.execute(f'''SELECT irreg.id, infl.id, irreg.gram_hash, irreg.wordform, irreg.is_alternative, irreg.lead_comment,
                          irreg.trailing_comment, irreg.is_edited FROM inflection AS infl INNER JOIN {irreg_forms_table}
                          AS irreg ON irreg.descriptor_id = infl.descriptor_id;''')
        irreg_form_rows = cursor.fetchall()
        for form in irreg_form_rows:
            try:
                cursor.execute(f'''INSERT INTO {irreg_forms_table}_new 
                                   VALUES (NULL, {form[1]}, \'{form[2]}\', \'{form[3]}\', {form[4]}, \'{form[5]}\', \'{form[6]}\', {form[7]});''')
#                                                 infl id     gr hash        wordform     is alt       lead comm     trail comm     is edited
            except Exception as e:
                exceptions += 1
                logger.error(f'Failed to update irregular form {form[3]}: id={form[0]}, exception {format(e)}')
                continue
            try:
                irreg_form_id = cursor.lastrowid
                cursor.execute(f'SELECT id, position, is_primary, is_edited FROM {irreg_stress_table} WHERE form_id={form[0]};')
                stress_rows = cursor.fetchall()
                for stress in stress_rows:
                    cursor.execute(f'''INSERT INTO {irreg_stress_table}_new 
                                       VALUES (NULL, {irreg_form_id}, {stress[1]}, {stress[2]}, {stress[3]});''');
            except Exception as e:
                exceptions += 1
                logger.error(f'Failed to update irregular stress for {form[3]}: id {stress[0]}: exception {format(e)}')

    print(f'Total irregular forms: {len(irreg_form_rows)}', file=output)
    print (f'{exceptions} exceptions', file=output)

    return True

def rename_new_tables(cursor, logger):
    try:
        cursor.execute('DROP TABLE irregular_forms;')
        cursor.execute('ALTER TABLE irregular_forms_NEW RENAME TO irregular_forms;')
        cursor.execute('DROP TABLE irregular_forms_spryazh_sm;')
        cursor.execute('ALTER TABLE irregular_forms_spryazh_sm_NEW RENAME TO irregular_forms_spryazh_sm;')
        cursor.execute('DROP TABLE missing_forms;')
        cursor.execute('ALTER TABLE missing_forms_NEW RENAME TO missing_forms;')
        cursor.execute('DROP TABLE difficult_forms;')
        cursor.execute('ALTER TABLE difficult_forms_NEW RENAME TO difficult_forms;')
        cursor.execute('DROP TABLE second_genitive;')
        cursor.execute('ALTER TABLE second_genitive_NEW RENAME TO second_genitive;')
        cursor.execute('DROP TABLE second_locative;')
        cursor.execute('ALTER TABLE second_locative_NEW RENAME TO second_locative;')
    except Exception as e:
        logger.error(f'Failed to modify table: exception {e}')

#ALTER TABLE second_genitive RENAME COLUMN descriptor_id TO inflection_id;
def update_second_genitive(cursor, logger):
    try:
        cursor.execute('''SELECT i.id FROM second_genitive AS if INNER JOIN inflection AS i 
                          ON if.descriptor_id = i.descriptor_id;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            cursor.execute(f'''UPDATE second_genitive SET descriptor_id={result[0]};''')

        # descriptor_id -> inflection_id
        cursor.execute('''ALTER TABLE second_genitive RENAME COLUMN descriptor_id TO inflection_id;''')

    except Exception as e:
        logger.error(f'Failed to retrieve inflection entry, exception: {e}.')
        sys.exit()

    return True

def update_missing_forms(cursor, logger):
    try:
        cursor.execute('''SELECT mfo.*, i.id FROM missing_forms_old AS mfo INNER JOIN inflection AS i 
                          ON mfo.descriptor_id = i.descriptor_id;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            content = result[2]
            inflection_id = result[3]
            cursor.execute('''INSERT INTO missing_forms (inflection_id, content) 
                              VALUES (?, ?);''',
                              (inflection_id, content))

    #            print('.', end='')

    except Exception as e:
        logger.error(f'Failed to update missing forms table, exception: {e}.')
        sys.exit()

    return True

def update_difficult_forms(cursor, logger):
    try:
        cursor.execute('''SELECT dfo.*, i.id FROM difficult_forms_old AS dfo INNER JOIN inflection AS i 
                             ON dfo.descriptor_id = i.descriptor_id;''')
        result_rows = cursor.fetchall()
        for result in result_rows:
            content = result[2]
            inflection_id = result[3]

            cursor.execute('''INSERT INTO difficult_forms (inflection_id, content) 
                              VALUES (?, ?);''',
                           (inflection_id, content))
    except Exception as e:
        logger.error(f'Failed to update difficult forms table, exception: {e}.')
        sys.exit()

    return True
