import toml
import sqlite3
from pymultimap.multimap import MultiMap

if __name__ == "__main__":

    dedupe_query = """
        SELECT hw.source, hw.id,d.id, i.id 
        FROM headword hw 
        INNER JOIN descriptor d ON hw.id=d.word_id left 
        OUTER JOIN inflection i ON i.descriptor_id=d.id 
        WHERE hw.source like '%острова)'
    """

    mm_hw_to_data = MultiMap (sorted=True)
    db_connection = sqlite3.connect('../Zal-Data/ZalData/ZalData_ProperNounsOnly.db3')
    db_cursor = db_connection.cursor()

    try:
        db_cursor.execute (dedupe_query)
        dedupe_rows = db_cursor.fetchall()
        for dedupe_row in dedupe_rows:
            mm_hw_to_data[dedupe_row[0]] = [dedupe_row[1], dedupe_row[2], dedupe_row[3]]
            if dedupe_row[3] is not None:
               print (dedupe_row[0])
        print (mm_hw_to_data)

    except Exception as e:
        print(e)

    try:
        for key, val in mm_hw_to_data.items():
            if len(val) < 2:
                print(f'********** No duplicate row for {key}')
                continue
            if val[1][2] is not None:
                db_cursor.execute(f"DELETE FROM inflection WHERE id = {val[1][2]}")
            db_cursor.execute(f"DELETE FROM descriptor WHERE id = {val[1][1]}")
            db_cursor.execute(f"DELETE FROM headword WHERE id = {val[1][0]}")

        db_connection.commit()

    except Exception as e:
        print(e)

    db_cursor = db_connection.cursor()

    select_query = """
        SELECT d.id, d.graphic_stem    
        FROM headword hw 
        INNER JOIN descriptor d ON hw.id=d.word_id 
        WHERE hw.source like '%острова)'
    """

    db_cursor.execute(select_query)
    select_rows = db_cursor.fetchall()
    gr_st_cursor = db_connection.cursor()
    for select_row in select_rows:
        d_id = select_row[0]
        gr_stem = select_row[1]
        stem_type = -1
        offset = gr_stem.find('ие (острова)')
        if offset > 0:
            stem_type = 1
        else:
            offset = gr_stem.find('овы (острова)')
            if offset > 0:
                stem_type = 2
        if offset > 0:
            gr_stem = gr_stem[:offset]
        else:
            print('************** ERROR unable to find substring in {0}'.format(gr_stem))
            continue
        update_query = f"""
            UPDATE descriptor 
            SET graphic_stem = '{gr_stem}', main_symbol = 'мн. неод.', part_of_speech = 1
            WHERE id = {d_id}
        """
        gr_st_cursor.execute(update_query)

        insert_query = f"""
            INSERT 
                INTO inflection (descriptor_id, is_primary, inflection_type, accent_type1, accent_type2)
                VALUES ({d_id}, 1, 3, 1, 0)
        """
        gr_st_cursor.execute(insert_query)

        gg = True

    db_connection.commit()





    k = 0
