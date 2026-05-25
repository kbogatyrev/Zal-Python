import toml
import sqlite3
import sys

def merge_proper_nouns (db_cursor):
    select_query = """
        SELECT hw.id,         -- 0
        hw.source, 
        hw.comment, 
        hw.usage, 
        hw.variant, 
        hw.variant_comment, 
        hw.see_ref, 
        hw.second_part,        -- 7
        pn.is_hypocoristicon,  -- 8
        pn.opposite_gender,
        pn.is_last_name,
        pn.has_tilde,
        pn.g_pl_assumed, 
        pn.has_space_separator,
        pn.extra_word_l,
        pn.extra_word_r,
        pn.comment,
        pns.spade_mark,        -- 17
        pns.spade_text,
        pnss.position,         -- 19 
        pnss.is_edited,        -- 20
        d.id,                  -- 21
        i.id                   -- 22
        FROM proper_nouns pn 
            JOIN headword hw ON hw.id=pn.word_id
            JOIN descriptor d ON hw.id=d.word_id 
            JOIN inflection i ON d.id=i.descriptor_id 
            LEFT JOIN proper_nouns_spade pns ON pns.proper_noun_id=pn.id 
            LEFT JOIN proper_nouns_spade_stress pnss ON pnss.spade_id=pns.id;
       """

    #----------------------------------------------------------------------------------------

    hw_dict = {}
    pn_dict = {}
    spade_dict = {}
    spade_stress_dict = {}
    try:
        db_cursor.execute (select_query)
        pn_rows = db_cursor.fetchall()
        for pn_row in pn_rows:
            old_headword_id = pn_row[0]
            hw_dict['source'] = pn_row[1]
            hw_dict['comment'] = pn_row[2]
            hw_dict['usage'] = pn_row[3]
            hw_dict['variant'] = pn_row[4]
            hw_dict['variant_comment'] = pn_row[5]
            hw_dict['see_ref'] = pn_row[6]
            hw_dict['back_ref'] = ''
            hw_dict['spryazh_sm'] = 0
            hw_dict['second_part'] = pn_row[7]
            hw_dict['is_edited'] = 0

            pn_dict['is_hypocoristicon'] = pn_row[8]
            pn_dict['opposite_gender'] = pn_row[9]
            pn_dict['is_last_name'] = pn_row[10]
            pn_dict['has_tilde'] = pn_row[11]
            pn_dict['g_pl_assumed'] = pn_row[12]
            pn_dict['has_space_separator'] = pn_row[13]
            pn_dict['extra_word_l'] = pn_row[14]
            pn_dict['extra_word_r'] = pn_row[15]
            pn_dict['comment'] = pn_row[16]
            pn_dict['is_edited'] = 0

            spade_dict['spade_mark'] = pn_row[17]
            spade_dict['spade_text'] = pn_row[18]

            spade_stress_dict['position'] = pn_row[19]

            old_descriptor_id = pn_row[21]
            old_inflection_id = pn_row[22]

            print(pn_row)

            hw_insert_query = """
                INSERT INTO M.headword 
                (
                    source,
                    plural_of,
                    comment,
                    usage,
                    variant,
                    variant_comment,
                    see_ref,
                    back_ref,
                    source_entry_id,
                    spryazh_sm,
                    second_part,
                    is_edited
                )
                VALUES ( ?,?,?,?,?,?,?,?,?,?,?,? );
            """

            data = (
                hw_dict['source'],
                '',
                hw_dict['comment'],
                hw_dict['usage'],
                hw_dict['variant'],
                hw_dict['variant_comment'],
                hw_dict['see_ref'],
                hw_dict['back_ref'],
                -1,
                hw_dict['spryazh_sm'],
                hw_dict['second_part'],
                0
            )

            db_cursor.execute (hw_insert_query, data)
            new_headword_id = db_cursor.lastrowid

            merge_stress (db_cursor, old_headword_id, new_headword_id)
            merge_homonyms (db_cursor, old_headword_id, new_headword_id)
            new_descriptor_id = merge_descriptor (db_cursor, old_headword_id, new_headword_id)
            new_inflection_id = merge_inflection (db_cursor, old_descriptor_id, new_descriptor_id)
            merge_common_deviation (db_cursor, old_inflection_id, new_inflection_id)
            merge_difficult_forms (db_cursor, old_inflection_id, new_inflection_id)
            merge_missing_forms (db_cursor, old_inflection_id, new_inflection_id)
            merge_second_locative (db_cursor, old_inflection_id, new_inflection_id)

    #----------------------------------------------------------------------------------------

            pn_insert_query = """
                INSERT INTO M.proper_nouns 
                (
                    word_id,
                    word_id_2,
                    is_hypocoristicon,
                    opposite_gender,
                    is_last_name,
                    has_tilde,
                    g_pl_assumed,
                    has_space_separator,
                    extra_word_l,
                    extra_word_r,
                    comment,
                    is_edited
                )
                VALUES ( ?,?,?,?,?,?,?,?,?,?,?,? );
            """

            data = (
                new_headword_id,
                0,
                pn_dict['is_hypocoristicon'],
                hw_dict['usage'],
                hw_dict['variant'],
                hw_dict['variant_comment'],
                hw_dict['see_ref'],
                hw_dict['back_ref'],
                -1,
                hw_dict['spryazh_sm'],
                hw_dict['second_part'],
                0
            )

            db_cursor.execute (pn_insert_query, data)
            pn_id = db_cursor.lastrowid

    # ----------------------------------------------------------------------------------------

            if (spade_dict['spade_mark']):
                spade_insert_query = """
                    INSERT INTO M.proper_nouns_spade 
                    (
                        proper_noun_id,
                        spade_mark,
                        spade_text,
                        is_edited
                    )
                    VALUES (?,?,?,?);
                """

                data = (
                    pn_id,
                    spade_dict['spade_mark'],
                    spade_dict['spade_text'],
                    0
                )

                db_cursor.execute(spade_insert_query, data)
                spade_id = db_cursor.lastrowid

    #----------------------------------------------------------------------------------------

                spade_stress_insert_query = """
                    INSERT INTO M.proper_nouns_spade_stress 
                    (
                        spade_id,
                        position,
                        is_edited
                    )
                    VALUES (?,?,?);
                """

                data = (
                    spade_id,
                    spade_stress_dict['position'],
                    0
                )

                db_cursor.execute(spade_stress_insert_query, data)

    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_stress (db_cursor, old_headword_id, new_headword_id):

    s_insert_query = f"""
        INSERT INTO M.stress (headword_id, stress_position, is_primary, is_variant, is_edited)
        SELECT ?, stress_position, is_primary, is_variant, 0
        FROM stress s
        WHERE s.headword_id = {old_headword_id};
    """

    try:
        db_cursor.execute(s_insert_query, (new_headword_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_homonyms (db_cursor, old_headword_id, new_headword_id):
    h_insert_query = f"""
        INSERT INTO M.homonyms 
        (
            headword_id, 
            homonym_number, 
            is_variant, 
            is_edited 
        )
        SELECT 
            ?, 
            homonym_number, 
            is_variant, 
            0             
        FROM homonyms h
        WHERE h.headword_id = {old_headword_id};
    """
    try:
        db_cursor.execute (h_insert_query, (new_headword_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_descriptor (db_cursor, old_headword_id, new_headword_id):
    d_insert_query = f"""
        INSERT INTO M.descriptor (            
            word_id, 
            graphic_stem,
            second_part_id,
            is_variant, 
            main_symbol,
            part_of_speech,
            is_plural_of,
            is_intransitive,
            is_reflexive, 
            main_symbol_plural_of, 
            alt_main_symbol, 
            inflection_type, 
            comment, 
            alt_main_symbol_comment, 
            alt_inflection_comment, 
            verb_stem_alternation, 
            part_past_pass_zhd, 
            section, 
            no_comparative, 
            no_long_forms, 
            assumed_forms, 
            yo_alternation, 
            o_alternation, 
            second_genitive, 
            is_impersonal, 
            is_iterative, 
            has_aspect_pair, 
            has_difficult_forms, 
            has_missing_forms, 
            has_irregular_forms, 
            irregular_forms_lead_comment, 
            restricted_contexts, 
            contexts, 
            cognate, 
            trailing_comment, 
            is_edited        
        )
        SELECT 
            ?, 
            graphic_stem, 
            second_part_id, 
            is_variant, 
            main_symbol, 
            part_of_speech, 
            is_plural_of, 
            0,                  -- is_intransitive 
            0,                  -- is_reflexive
            '',                 -- main_symbol_plural_of 
            alt_main_symbol, 
            inflection_type, 
            comment, 
            '',                 -- alt_main_symbol_comment 
            '',                 -- alt_inflection_comment 
            '',                 -- verb_stem_alternation 
            0,                  -- part_past_pass_zhd 
            section, 
            no_comparative, 
            0,                  -- no_long_forms, 
            assumed_forms, 
            yo_alternation, 
            o_alternation, 
            second_genitive, 
            0,                  -- is_impersonal 
            0,                  -- is_iterative 
            0,                  -- has_aspect_pair 
            has_difficult_forms, 
            has_missing_forms, 
            has_irregular_forms, 
            irregular_forms_lead_comment, 
            restricted_contexts, 
            contexts, 
            cognate, 
            trailing_comment, 
            0        
        FROM descriptor d
        WHERE d.word_id = {old_headword_id};
    """

    try:
        db_cursor.execute (d_insert_query, (new_headword_id,))
        return db_cursor.lastrowid

    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_inflection (db_cursor, old_descriptor_id, new_descriptor_id):
    i_insert_query = f"""
        INSERT INTO M.inflection 
        (
            descriptor_id, 
            is_primary, 
            inflection_type, 
            accent_type1, 
            accent_type2, 
            short_form_restrictions, 
            past_part_restrictions,
            no_short_form,
            no_past_part,
            fleeting_vowel,
            stem_extension,
            second_genitive,
            comment,
            is_edited
        )
        SELECT 
            ?, 
            is_primary, 
            inflection_type, 
            accent_type1, 
            accent_type2, 
            short_form_restrictions, 
            past_part_restrictions,
            no_short_form,
            no_past_part,
            fleeting_vowel,
            stem_extension,
            second_genitive,
            comment,
            0
        FROM inflection i
        WHERE i.descriptor_id = {old_descriptor_id};
    """
    try:
        db_cursor.execute (i_insert_query, (new_descriptor_id,))
        return db_cursor.lastrowid
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_common_deviation (db_cursor, old_inflection_id, new_inflection_id):
    i_insert_query = f"""
        INSERT INTO M.common_deviation 
        (
            inflection_id, 
            deviation_type, 
            is_optional, 
            is_edited 
        )
        SELECT 
            ?, 
            deviation_type, 
            is_optional, 
            0             
        FROM common_deviation cd
        WHERE cd.inflection_id = {old_inflection_id};
    """
    try:
        db_cursor.execute (i_insert_query, (new_inflection_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_difficult_forms (db_cursor, old_inflection_id, new_inflection_id):
    df_insert_query = f"""
        INSERT INTO M.difficult_forms 
        (
            inflection_id, 
            gram_hash 
        )
        SELECT
            ?,
            gram_hash 
        FROM difficult_forms df
        WHERE df.inflection_id = {old_inflection_id};
    """
    try:
        db_cursor.execute (df_insert_query, (new_inflection_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_missing_forms (db_cursor, old_inflection_id, new_inflection_id):
    mf_insert_query = f"""
        INSERT INTO M.missing_forms 
        (
            inflection_id, 
            gram_hash 
        )
        SELECT
            ?,
            gram_hash 
        FROM missing_forms mf
        WHERE mf.inflection_id = {old_inflection_id};
    """
    try:
        db_cursor.execute (mf_insert_query, (new_inflection_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_second_locative (db_cursor, old_inflection_id, new_inflection_id):
    sl_insert_query = f"""
        INSERT INTO M.second_locative 
        (
            inflection_id, 
            is_optional,
            preposition,
            is_edited 
        )
        SELECT
            ?, 
            is_optional,
            preposition,
            0 
        FROM second_locative sl
        WHERE sl.inflection_id = {old_inflection_id};
    """
    try:
        db_cursor.execute (sl_insert_query, (new_inflection_id,))
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def update_second_part_id (db_cursor, old_2nd_part_id, new_second_part_id):
    second_part_query = f"""
        UPDATE M.descriptor 
        SET second_part_id={new_second_part_id} 
        WHERE second_part_id = {old_2nd_part_id}; 
    """
    try:
        db_cursor.execute (second_part_query)
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

def merge_compounds(db_cursor):
    select_query = """
        SELECT hw.id,                -- 0
               hw.source, 
               hw.comment, 
               hw.usage, 
               hw.variant, 
               hw.variant_comment, 
               hw.see_ref, 
               hw.second_part,       -- 7 
               d.id,
               i.id
        FROM headword hw JOIN descriptor d ON hw.id=d.word_id JOIN inflection i ON i.descriptor_id=d.id 
        WHERE d.id IN 
            (SELECT DISTINCT 
                old_d.second_part_id
                FROM headword old_hw 
                    JOIN descriptor old_d ON old_hw.id=old_d.word_id  
                    JOIN inflection old_i ON old_i.descriptor_id=old_d.id
                    JOIN proper_nouns old_pn ON old_pn.word_id=old_hw.id
                    JOIN M.headword new_hw ON old_hw.source=new_hw.source
                    JOIN M.descriptor new_d ON (old_d.graphic_stem=new_d.graphic_stem
                        AND new_d.main_symbol=old_d.main_symbol
                        AND new_d.inflection_type=old_d.inflection_type)
                WHERE old_d.second_part_id > 0
                ORDER BY new_hw.source
            );
        """

    hw_insert_query = """
        INSERT INTO M.headword 
        (
            source,
            plural_of,
            comment,
            usage,
            variant,
            variant_comment,
            see_ref,
            back_ref,
            source_entry_id,
            spryazh_sm,
            second_part,
            is_edited
        )
        VALUES ( ?,?,?,?,?,?,?,?,?,?,?,? );
    """

    try:
        hw_dict = {}

        db_cursor.execute(select_query)
        hw_rows = db_cursor.fetchall()
        for hw_row in hw_rows:
            old_headword_id = hw_row[0]
            hw_dict['source'] = hw_row[1]
            hw_dict['plural_of'] = ''
            hw_dict['comment'] = hw_row[2]
            hw_dict['usage'] = hw_row[3]
            hw_dict['variant'] = hw_row[4]
            hw_dict['variant_comment'] = hw_row[5]
            hw_dict['see_ref'] = hw_row[6]
            hw_dict['back_ref'] = ''
            hw_dict['spryazh_sm'] = 0
            hw_dict['second_part'] = hw_row[7]
            hw_dict['is_edited'] = 0
            old_2nd_part_id = hw_row[8]
            old_inflection_id = hw_row[9]

            data = (
                hw_dict['source'],
                '',
                hw_dict['comment'],
                hw_dict['usage'],
                hw_dict['variant'],
                hw_dict['variant_comment'],
                hw_dict['see_ref'],
                hw_dict['back_ref'],
                -1,
                0,
                hw_dict['second_part'],
                0
            )

            db_cursor.execute (hw_insert_query, data)
            new_headword_id = db_cursor.lastrowid
            merge_stress (db_cursor, old_headword_id, new_headword_id)
            merge_homonyms (db_cursor, old_headword_id, new_headword_id)
            new_second_part_id = merge_descriptor (db_cursor, old_headword_id, new_headword_id)
            update_second_part_id (db_cursor, old_2nd_part_id, new_second_part_id)
            new_inflection_id = merge_inflection (db_cursor, old_2nd_part_id, new_second_part_id)
            merge_common_deviation (db_cursor, old_inflection_id, new_inflection_id)
            merge_difficult_forms (db_cursor, old_inflection_id, new_inflection_id)
            merge_missing_forms (db_cursor, old_inflection_id, new_inflection_id)
            merge_second_locative (db_cursor, old_inflection_id, new_inflection_id)

    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))


#def merge_incomplete_parses (db_cursor):
#    ip_insert_query = f"""
#        INSERT INTO M.incomplete_parses
#        SELECT * from incomplete_parses;
#    """
#    try:
#        db_cursor.execute (ip_insert_query)
#    except IOError as io_ex:
#        print('IO Error.', io_ex.args[0])
#    except sqlite3.Error as sqlite_ex:
#        print('sqlite3 error: ', sqlite_ex.args[0])
#    except Exception as e:
#        print('Exception: %s, %s' % (sys.exc_info()[0], e))

if __name__ == "__main__":
    db_connection = sqlite3.connect('../Zal-Data/ZalData/ZalData_ProperNounsOnly.db3')
    db_cursor = db_connection.cursor()

    sql_attach = "ATTACH DATABASE '../Zal-Data/ZalData/ZalData_Master.db3' AS 'M';"
    db_cursor.execute (sql_attach)

#    merge_proper_nouns (db_cursor)

#    db_connection.commit()

    merge_compounds (db_cursor)

    db_connection.commit()

#    merge_incomplete_parses (db_cursor)


