import toml
import sqlite3
import sys

def merge_proper_nouns(db_cursor):

    select_query = """
        SELECT hw.source,      -- 0
        hw.comment, 
        hw.usage, 
        hw.variant, 
        hw.variant_comment, 
        hw.see_ref, 
    --    hw.back_ref,   --0 
    --    hw.source_entry_id, 
        hw.second_part,        -- 6
        pn.is_hypocoristicon,  -- 7
        pn.opposite_gender,
        pn.is_last_name,
        pn.has_tilde,
        pn.g_pl_assumed, 
        pn.has_space_separator,
        pn.extra_word_l,
        pn.extra_word_r,
        pn.comment,
    --    pn.is_edited, --0
        pns.spade_mark,        -- 16
        pns.spade_text,
        pns.is_edited, --0
        pnss.position,         -- 18 
        pnss.is_edited --
        FROM proper_nouns pn 
            JOIN headword hw ON hw.id=pn.word_id 
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
            hw_dict['source'] = pn_row[0]
            hw_dict['plural_of'] = ''
            hw_dict['comment'] = pn_row[1]
            hw_dict['usage'] = pn_row[2]
            hw_dict['variant'] = pn_row[3]
            hw_dict['variant_comment'] = pn_row[4]
            hw_dict['see_ref'] = pn_row[5]
            hw_dict['back_ref'] = ''
    #        hw_dict['source_entry_id'] = pn_row[6]
            hw_dict['spryazh_sm'] = 0
            hw_dict['second_part'] = pn_row[6]
            hw_dict['is_edited'] = 0

            pn_dict['is_hypocoristicon'] = pn_row[7]
            pn_dict['opposite_gender'] = pn_row[8]
            pn_dict['is_last_name'] = pn_row[9]
            pn_dict['has_tilde'] = pn_row[10]
            pn_dict['g_pl_assumed'] = pn_row[11]
            pn_dict['has_space_separator'] = pn_row[12]
            pn_dict['extra_word_l'] = pn_row[13]
            pn_dict['extra_word_r'] = pn_row[14]
            pn_dict['comment'] = pn_row[15]
            pn_dict['is_edited'] = 0

            spade_dict['spade_mark'] = pn_row[16]
            spade_dict['spade_text'] = pn_row[17]

            spade_stress_dict['position'] = pn_row[18]

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
            word_id = db_cursor.lastrowid

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
                word_id,
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

            db_cursor.execute(pn_insert_query, data)
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
                    VALUES ( ?,?,?,?);
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
                    VALUES ( ?,?,?,?);
                """

                data = (
                    pn_id,
                    spade_dict['spade_mark'],
                    spade_dict['spade_text'],
                    0
                )

                db_cursor.execute(spade_insert_query, data)

    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))


if __name__ == "__main__":
    db_connection = sqlite3.connect('../Zal-Data/ZalData/ZalData_ProperNounsOnly.db3')
    db_cursor = db_connection.cursor()

    sql_attach = "ATTACH DATABASE '../Zal-Data/ZalData/ZalData_Master.db3' AS 'M';"
    db_cursor.execute(sql_attach)

    merge_proper_nouns(db_cursor)


