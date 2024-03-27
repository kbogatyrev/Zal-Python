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

# -- Add second_genitive column
# -- Create empty records for missing inflection entries (e.g. uninflected words)
# -- Copy second_genitive values from the descriptor table
def fix_inflection_table(cursor, logger, output):

    cursor.execute('''CREATE TABLE "inflection_NEW" (id INTEGER PRIMARY KEY ASC, descriptor_id INTEGER, is_primary BOOLEAN DEFAULT (0),
                      inflection_type INTEGER, accent_type1 INTEGER, accent_type2 INTEGER, short_form_restrictions BOOLEAN DEAFULT (0),
                      past_part_restrictions BOOLEAN DEAFULT (0), no_short_form BOOLEAN DEAFULT (0), no_past_part BOOLEAN DEAFULT (0),
                      fleeting_vowel BOOLEAN DEFAULT (0), stem_augment BOOLEAN DEFAULT (0), second_genitive BOOLEAN DEAFAULT(0),
                      comment TEXT, is_edited BOOLEAN DEFAULT(0))''')

    cursor.execute('''INSERT INTO inflection_NEW (id, descriptor_id, is_primary, inflection_type, accent_type1, accent_type2,
                      short_form_restrictions, past_part_restrictions, no_short_form, no_past_part, fleeting_vowel, 
                      stem_augment, second_genitive, comment, is_edited) 
                      SELECT i.id, i.descriptor_id, i.is_primary, i.inflection_type, i.accent_type1, i.accent_type2,
                      i.short_form_restrictions, i.past_part_restrictions, i.no_short_form, i.no_past_part, i.fleeting_vowel, 
                      i.stem_augment, d.second_genitive, NULL, i.is_edited FROM inflection AS i INNER JOIN descriptor AS d
                      ON d.id=i.descriptor_id;''')

    try:
        d_id_to_hw = {}
        cursor.execute('''SELECT d.id, d.second_genitive, hw.source FROM headword AS hw INNER JOIN descriptor AS d on d.word_id=hw.id;''')
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
                cursor.execute(f'''INSERT INTO inflection_NEW 
                                   VALUES (NULL, {d_id}, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, ?, 1);''',(None,))
        d_ids_no_infl.sort()
        print(f'Descriptors with missing inflection entries: {count}.', file=output)
        for idx in range(len(d_ids_no_infl)):
            d_id = d_ids_no_infl[idx]
            print(f'{d_id}: {d_id_to_hw[d_id]}', file=output)

    except Exception as e:
        logger.error(f'Exception while retrieving inflection entry: {e}.')
        sys.exit()

    cursor.execute('DROP TABLE "inflection"')
    cursor.execute('ALTER TABLE inflection_NEW RENAME TO inflection;')

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
    cursor.execute('''CREATE TABLE "descriptor_NEW" (id INTEGER PRIMARY KEY ASC, word_id INTEGER, graphic_stem TEXT, second_part_id INTEGER, 
                      is_variant BOOLEAN DEFAULT (0), main_symbol TEXT, part_of_speech INTEGER, is_plural_of BOOLEAN DEFAULT (0), 
                      is_intransitive BOOLEAN DEFAULT (0), is_reflexive BOOLEAN DEFAULT(0), main_symbol_plural_of TEXT, alt_main_symbol TEXT, 
                      inflection_type TEXT, comment TEXT, alt_main_symbol_comment TEXT, alt_inflection_comment TEXT, verb_stem_alternation TEXT, 
                      part_past_pass_zhd BOOLEAN DEFAULT (0), section INTEGER, no_comparative BOOLEAN DEFAULT (0), no_long_forms BOOLEAN DEFAULT (0), 
                      assumed_forms BOOLEAN DEFAULT (0), yo_alternation BOOLEAN DEFAULT (0), o_alternation BOOLEAN DEFAULT (0), 
                      is_impersonal BOOLEAN DEFAULT (0), is_iterative BOOLEAN DEFAULT (0), has_aspect_pair BOOLEAN DEFAULT (0), 
                      has_difficult_forms BOOLEAN DEFAULT (0), has_missing_forms BOOLEAN DEFAULT (0), has_irregular_forms BOOLEAN DEFAULT (0), 
                      irregular_forms_lead_comment TEXT, restricted_contexts TEXT, contexts TEXT, cognate TEXT, trailing_comment TEXT, 
                      is_edited BOOLEAN DEFAULT(0), FOREIGN KEY (word_id) REFERENCES "headword" (id))''')

'''
def rename_new_tables(cursor, logger):
    try:
        cursor.execute('DROP TABLE "descriptor"')
        cursor.execute('ALTER TABLE descriptor_NEW RENAME TO descriptor;')
    except Exception as e:
        logger.error(f'Failed to modify table: exception {e}')
'''

def update_irregular_forms(cursor, logger, output):
    exceptions = 0

    cursor.execute('''CREATE TABLE irregular_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, gram_hash TEXT, wordform TEXT, 
                      is_alternative BOOLEAN DEFAULT (0), lead_comment TEXT, trailing_comment TEXT, is_edited BOOLEAN DEFAULT(0));''')
    cursor.execute('''CREATE TABLE irregular_stress_NEW (id INTEGER PRIMARY KEY ASC, form_id INTEGER, position INTEGER, 
                      is_primary BOOLEAN, is_edited BOOLEAN DEFAULT(0), FOREIGN KEY(form_id) REFERENCES irregular_forms(id));''')
    cursor.execute('''CREATE TABLE irregular_forms_spryazh_sm_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, gram_hash TEXT, 
                      wordform TEXT, is_alternative BOOLEAN DEFAULT (0), lead_comment TEXT, trailing_comment TEXT, is_edited BOOLEAN DEFAULT(0));''')
    cursor.execute('''CREATE TABLE irregular_stress_spryazh_sm_NEW (id INTEGER PRIMARY KEY ASC, form_id INTEGER, position INTEGER, 
                      is_primary BOOLEAN, is_edited BOOLEAN DEFAULT(0), FOREIGN KEY(form_id) REFERENCES irregular_forms(id));''')

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

    cursor.execute('DROP TABLE irregular_forms;')
    cursor.execute('ALTER TABLE irregular_forms_NEW RENAME TO irregular_forms;')
    cursor.execute('DROP TABLE irregular_forms_spryazh_sm;')
    cursor.execute('ALTER TABLE irregular_forms_spryazh_sm_NEW RENAME TO irregular_forms_spryazh_sm;')
    cursor.execute('DROP TABLE irregular_stress;')
    cursor.execute('ALTER TABLE irregular_stress_NEW RENAME TO irregular_stress;')
    cursor.execute('DROP TABLE irregular_stress_spryazh_sm;')
    cursor.execute('ALTER TABLE irregular_stress_spryazh_sm_NEW RENAME TO irregular_stress_spryazh_sm;')

    print(f'Total irregular forms: {len(irreg_form_rows)}', file=output)
    print (f'{exceptions} exceptions', file=output)

    return True

def update_missing_and_difficult_forms(cursor, logger, output):
    exceptions = 0

    cursor.execute('''CREATE TABLE missing_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, content TEXT);''')
    cursor.execute('''CREATE TABLE difficult_forms_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, content TEXT);''')

    for forms_table in ['missing_forms', 'difficult_forms']:
        cursor.execute(f'''SELECT i.id, f.content FROM inflection AS i INNER JOIN {forms_table} 
                          AS f ON f.descriptor_id = i.descriptor_id;''')
        form_rows = cursor.fetchall()
        for form in form_rows:
            try:
                cursor.execute(f'''INSERT INTO {forms_table}_new 
                                   VALUES (NULL, {form[0]}, \'{form[1]}\');''')
#                                                 infl id     gr hash
            except Exception as e:
                exceptions += 1
                logger.error(f'Failed to update {forms_table}: inflection id={form[0]}, exception {format(e)}')
                continue

    print(f'Total irregular forms: {len(form_rows)}', file=output)

    cursor.execute('DROP TABLE missing_forms;')
    cursor.execute('ALTER TABLE missing_forms_NEW RENAME TO missing_forms;')
    cursor.execute('DROP TABLE difficult_forms;')
    cursor.execute('ALTER TABLE difficult_forms_NEW RENAME TO difficult_forms;')

    print (f'Done with {exceptions} exceptions', file=output)

    return True

def update_second_locative(cursor, logger, output):
    exceptions = 0

    cursor.execute('''CREATE TABLE second_locative_NEW (id INTEGER PRIMARY KEY ASC, inflection_id INTEGER, is_optional BOOLEAN DEFAULT(0), 
                      preposition TEXT, is_edited BOOLEAN(0));''')

    cursor.execute(f'''SELECT i.id, sl.is_optional, sl.preposition FROM inflection AS i INNER JOIN second_locative 
                       AS sl ON sl.descriptor_id = i.descriptor_id;''')
    rows = cursor.fetchall()
    for row in rows:
        try:
            cursor.execute(f'''INSERT INTO second_locative_NEW 
                               VALUES (NULL, {row[0]}, {row[1]}, \'{row[2]}\', 1);''')
            #                                 infl id   is_opt    preposition  is_edited
        except Exception as e:
            exceptions += 1
            logger.error(f'Failed to update second_locative table: inflection id={row[0]}, exception {format(e)}')
            continue

    cursor.execute('DROP TABLE second_locative;')
    cursor.execute('ALTER TABLE second_locative_NEW RENAME TO second_locative;')

    print(f'Total second locative entries: {len(rows)}', file=output)
    print(f'Done with {exceptions} exceptions', file=output)

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
