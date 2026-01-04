import toml
import sqlite3
from pymultimap.multimap import MultiMap

def handle_entry(headword):
    main_symbol = ''
    inflection_type = ''
    inflection_num = -1
    gr_stem = ''

    gram_hashes = []

    match headword:
        case headword if headword.find('(острова)') > 0:
            main_symbol = 'п'
            offset = headword.find('ие (острова)')
            if offset > 0:
                inflection_type = 'п'
                inflection_num = 3
            else:
                offset = headword.find('овы (острова)')
                if offset > 0:
                    inflection_type = 'мс'
                    inflection_num = 1
                    offset += 2
                else:
                    print('************** ERROR unable to find substring in {}'.format(headword))
            if offset > 0:
                gr_stem = headword[:offset]
                gram_hashes.extend(['AdjL_*_Sg_*', 'AdjL_*_Sg_*_*', 'AdjL_Pl_A_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ая (сопка)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ая (сопка)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_N_Sg_*', 'AdjL_N_Sg_*_*', 'AdjL_Pl_A_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ий (залив)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ий (залив)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ов (залив)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find(' (залив)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ий (пролив)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ий (пролив)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ов (пролив)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find(' (пролив)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('кий (океан)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ий (океан)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('хий (океан)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ий (океан)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('во (поле)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find('о (поле)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim',  'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ое (море)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            if headword.find('кое') > 0:
                inflection_num = 3
            else:
                inflection_num = 1
            gr_stem = headword[:headword.find('ое (море)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim',  'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('во (море)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find('о (море)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim',  'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ое (озеро)') > 0:
            main_symbol = 'п'
            inflection_type = 'п'
            inflection_num = 3
            gr_stem = headword[:headword.find('ое (озеро)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim',  'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('во (озеро)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find('о (озеро)')]
            gram_hashes.extend(['AdjL_M_Sg_*', 'AdjL_M_Sg_*_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim',  'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

        case headword if headword.find('ев (курган)') > 0:
            main_symbol = 'п'
            inflection_type = 'мс'
            inflection_num = 1
            gr_stem = headword[:headword.find(' (курган)')]
            gram_hashes.extend(['AdjL_N_Sg_*', 'AdjL_F_Sg_*', 'AdjL_*_Sg_*_Anim', 'AdjL_Pl_*_Anim', 'AdjS_*', 'AdjComp'])

    return  gr_stem, main_symbol, inflection_type, inflection_num, gram_hashes

if __name__ == "__main__":

    dedupe_query = """
        SELECT hw.source, hw.id, d.id, i.id 
        FROM headword hw 
        INNER JOIN descriptor d ON hw.id=d.word_id left 
        OUTER JOIN inflection i ON i.descriptor_id=d.id 
        WHERE hw.source like '%острова)' 
            OR hw.source like '%сопка)' 
            OR hw.source like '%залив)' 
            OR hw.source like '%пролив)'
            OR hw.source like '%поле)'
            OR hw.source like '%море)'
            OR hw.source like '%курган)'
            OR hw.source like '%океан)'
            OR hw.source like '%озеро)'
            OR hw.source like '%башня)'  
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
        print('------------------------------------------------------------------')
        for key, values in mm_hw_to_data.items():
            print(key, values)
        print('------------------------------------------------------------------')
#        print (mm_hw_to_data)

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
        SELECT d.id, d.graphic_stem, i.id 
        FROM headword hw 
        INNER JOIN descriptor d ON hw.id=d.word_id 
        LEFT OUTER JOIN inflection i ON i.descriptor_id = d.id 
        WHERE hw.source like '%острова)'
            OR hw.source like '%сопка)' 
            OR hw.source like '%залив)' 
            OR hw.source like '%пролив)'
            OR hw.source like '%поле)'
            OR hw.source like '%море)'
            OR hw.source like '%курган)'
            OR hw.source like '%океан)'
            OR hw.source like '%озеро)'
            OR hw.source like '%башня)'  
    """

    db_cursor.execute(select_query)
    select_rows = db_cursor.fetchall()
    gr_st_cursor = db_connection.cursor()
    for select_row in select_rows:
        d_id = select_row[0]
        gr_stem, main_symbol, inflection_type, inflection_num, gram_hashes = handle_entry(select_row[1])
        update_query = f"""
            UPDATE descriptor 
            SET graphic_stem = '{gr_stem}', main_symbol = '{main_symbol}', part_of_speech = 3, inflection_type = '{inflection_type}'
            WHERE id = {d_id}
        """
        gr_st_cursor.execute(update_query)

        inflection_id = select_row[2]
        if inflection_id == None:
                insert_query = f"""
                INSERT 
                    INTO inflection (descriptor_id, is_primary, inflection_type, accent_type1, accent_type2)
                    VALUES ({d_id}, 1, {inflection_num}, 1, 0)
            """
                gr_st_cursor.execute(insert_query)
                inflection_id = gr_st_cursor.lastrowid

        for gram_hash in gram_hashes:
            missing_forms_query = f"""
                INSERT 
                    INTO missing_forms (inflection_id, gram_hash)
                    VALUES ({inflection_id}, '{gram_hash}') 
            """
            gr_st_cursor.execute(missing_forms_query)

            descriptor_query = f"""
                UPDATE descriptor
                SET has_missing_forms = 1
                WHERE id = {d_id}
            """
            gr_st_cursor.execute(descriptor_query)

        gg = True

    db_connection.commit()

    k = 0
