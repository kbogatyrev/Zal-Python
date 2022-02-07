import logging
import re
import sys
import sqlite3
import time
from collections import defaultdict

class Data:
    tact_group_id = -1          # tg.id
    source_with_stress = ''     # tg.source
    first_word_pos = -1         # tg.first_word_position
    words_in_tact_group = -1    # tg.num_of_words
    num_of_syllables = -1       # tg.num_of_syllables
    stressed_syllable = -1      # tg.stressed_syllable
    sentence_number = -1        # lit.line_number
    sentence_source = ''        # lit.source
    text_id = -1                # txt.id

class Node:
#    node_data = Data()
#    children = []

    def __init__(self):
        self.node_data = Data()
        self.children = []

class Handler:

    def __init__(self, db_path):

        self.db_connect = None
        self.db_cursor = None

        self.sentence_query = 'SELECT DISTINCT text_id, line_number FROM lines_in_text;'

#                                              0       1              2                        3               4                        5                  6             7          8      
        self.word_query = 'SELECT DISTINCT tg.id, tg.source, tg.first_word_position, tg.num_of_words, tg.num_of_syllables, tg.stressed_syllable, lit.line_number, lit.text_id, lit.source \
                           FROM tact_group AS tg INNER JOIN lines_in_text AS lit ON tg.line_id = lit.id WHERE lit.text_id = {0} AND lit.line_number = {1} ORDER BY lit.line_number, tg.id ASC;'

#                                              0       1              2                        3               4                        5                  6             7          8      
#        self.words_query = 'SELECT DISTINCT tg.id, tg.source, tg.first_word_position, tg.num_of_words, tg.num_of_syllables, tg.stressed_syllable, lit.line_number, lit.text_id, lit.source \
#                            FROM tact_group AS tg INNER JOIN lines_in_text AS lit ON tg.line_id = lit.id ORDER BY lit.line_number, tg.id ASC;'

        self.word_pos_to_data = {}  # dictionary of lists

        self.ready = False

        try:
            self.db_connect = sqlite3.connect(db_path)
            self.ready = True

        except Exception as e:
            self.ready = False
            print(e)

#---------------------------------------------------------------------------------------------------

    def get_tact_groups(self):
        if not self.ready:
            print('Error: Handler not initialized.')
            return
        try:
            sentence_cursor = self.db_connect.cursor()
            sentence_cursor.execute(self.sentence_query)
            sentence_rows = sentence_cursor.fetchall()

            chapter_to_sentence = defaultdict(list)
            for sentence_row in sentence_rows:
                chapter_to_sentence[sentence_row[0]].append(sentence_row[1])

            tg_cursor = self.db_connect.cursor()
            for chapter in chapter_to_sentence.keys():
                for sentence in chapter_to_sentence[chapter]:
                    query = self.word_query.format(chapter, sentence)
                    tg_cursor.execute(query)
                    tg_rows = tg_cursor.fetchall()
                    root = self.build_tree(tg_rows)
                    verse = []
                    has_rhythm = True
                    print(chapter, sentence)
                    self.traverse(root, verse, has_rhythm)

        except Exception as e:
            print('Exception: {}'.format(e))

#---------------------------------------------------------------------------------------------------

    def build_tree(self, tg_rows):

        # Read tact group data
        current_word_pos = -1
        variants = []
        for row in tg_rows:
            data = Data()
            data.tact_group_id = row[0]
            data.source_with_stress = row[1]
            data.first_word_pos = row[2]
            data.num_of_words = row[3]
            data.num_of_syllables = row[4]
            data.stressed_syllable = row[5]
            data.sentence_number = row[6]
            data.text_id = row[7]
            data.sentence_source = row[8]

            data.pos = self.get_gram_hashes(data)

            if current_word_pos != data.first_word_pos:
                if current_word_pos >= 0:
                    self.word_pos_to_data[current_word_pos] = variants.copy()
                    variants.clear()
                current_word_pos = data.first_word_pos

            variants.append(data)

        # End sentinel
        self.word_pos_to_data[current_word_pos] = variants.copy()
        end_node = Data()
        end_node.source_with_stress = '.'
        end_variants = []
        end_variants.append(end_node)
        self.word_pos_to_data[current_word_pos+1] = end_variants.copy()

        # Build tact group tree
        self.word_pos_list = list(self.word_pos_to_data.keys())
        word_pos = 0
        root = Node()
        self.add_word(root, word_pos)

        return root

#---------------------------------------------------------------------------------------------------

    def add_word(self, parent, word_pos):
        try:
            variants = []
            if word_pos in self.word_pos_to_data:
                if self.word_pos_to_data[word_pos][0].tact_group_id and \
                    self.word_pos_to_data[word_pos][0].source_with_stress == '.':
                    return
                variants = self.word_pos_to_data[word_pos]
            else:
                variants.append(Data())
            for var in variants:
                node = Node()
                node.node_data = var
                parent.children.append(node)
            for child in parent.children:
                self.add_word(child, word_pos+1)
        
        except Exception as e:
            print('Exception: {}'.format(e))

        return

#---------------------------------------------------------------------------------------------------

    def get_gram_hashes(self, data):
        word_query = 'SELECT gram_hash FROM tact_group_to_gram_hash AS gh INNER JOIN tact_group AS tg ON gh.tact_group_id = tg.id WHERE tg.id = {};'.format(data.tact_group_id)
        gram_hash_cursor = self.db_connect.cursor()
        gram_hash_cursor.execute(word_query)
        result_rows = gram_hash_cursor.fetchall()
        gram_hashes = []
        for row in result_rows:
            gram_hashes.append(row[0].split('_')[0])
        return list(set(gram_hashes))

#---------------------------------------------------------------------------------------------------

    def traverse(self, parent, verse, has_rhythm):
        tg = parent.node_data
        if tg.tact_group_id > -1:
           for syll_idx in range(0, tg.num_of_syllables):
                if not has_rhythm:
                    verse.clear()
                prev_syll_idx = len(verse) - 1
                if tg.stressed_syllable == syll_idx:                        
                    unstr_count = 0
                    # Count unstressed syllables preceding last stressed syll.
                    while prev_syll_idx >= 0 and False == verse[prev_syll_idx][0]:
                        unstr_count += 1
                        prev_syll_idx -= 1
                        
                    if len(verse) > 1 and unstr_count % 2 == 0:  # no rhythm, remove this tg
                        at = syll_idx
                        while at > 0:
                            verse.pop()
                            at = at - 1
                        if len(verse) > 3:    # ... and save previous syllables if any
                            self.save_sequence(verse)
                            verse.clear()
                            
                        has_rhythm = False
                                
                    verse.append((True, tg.tact_group_id, syll_idx))
                else:
                    verse.append((False, tg.tact_group_id, syll_idx))
            
        for child in parent.children:
#            print(child.node_data.tact_group_id)
            self.traverse(child, verse[:], has_rhythm)

#---------------------------------------------------------------------------------------------------

    def save_sequence(self, verse):
        for syll_tuple in verse:
            print (syll_tuple)
        print ('------------------')
#---------------------------------------------------------------------------------------------------

if __name__== "__main__":
    db_path = '../../Zal-Data/ZalData/ZalData_oxr_gram.db3'
    output_path = '../../Zal-Data/ZalData/Pasternak_01_16.txt'
    out_file = open(output_path, "w", encoding='utf16')

    h = Handler(db_path)
    h.get_tact_groups()

    k = 0
   