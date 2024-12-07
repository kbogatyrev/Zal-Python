# -*- coding: utf-8 -*-

import sys
import os
import codecs
import sqlite3
import re
import hashlib
from docx import *
from collections import defaultdict
#from EndingsConverter import *

#
#
#

class POS:
    POS_UNDEFINED =             u'Undefined'
    POS_NULL =                  u'None'
    POS_NOUN =                  u'Noun'
    POS_VERB =                  u'Verb'
    POS_ADJ =                   u'Adj'
    POS_PRONOUN =               u'Pron'
    POS_PRONOUN_ADJ =           u'PronAdj'
    POS_PRONOUN_PREDICATIVE =   u'PronPredic'
    POS_NUM =                   u'Num'
    POS_NUM_ADJ =               u'NumAdj'
    POS_ADV =                   u'Adv'
    POS_COMPARATIVE =           u'Comp'      
    POS_PREDICATIVE =           u'Predic'
    POS_PREPOSITION =           u'Prep'
    POS_CONJUNCTION =           u'Conj'
    POS_PARTICLE =              u'Particle'
    POS_INTERJECTION =          u'Interj'
    POS_PARENTH =               u'Parenth'

class POS_ENUM:
    POS_UNDEFINED =             -1
    POS_NULL =                   0
    POS_NOUN =                   1
    POS_VERB =                   2
    POS_ADJ =                    3
    POS_PRONOUN =                4
    POS_PRONOUN_ADJ =            5
    POS_PRONOUN_PREDICATIVE =    6
    POS_NUM =                    7
    POS_NUM_ADJ =                8
    POS_ADV =                    9
    POS_COMPARATIVE =           10
    POS_PREDICATIVE =           11
    POS_PREPOSITION =           12
    POS_CONJUNCTION =           13
    POS_PARTICLE =              14
    POS_INTERJECTION =          15
    POS_PARENTH =               16

class AT:
    AT_NULL =                   u'None'
    AT_A =                      u'A'
    AT_A1 =                     u'A1'
    AT_B =                      u'B'
    AT_B1 =                     u'B1'
    AT_C =                      u'C'
    AT_C1 =                     u'C1'
    AT_C2 =                     u'C2'
    AT_D =                      u'D'
    AT_D1 =                     u'D1'
    AT_E =                      u'E'
    AT_F =                      u'F'
    AT_F1 =                     u'F1'
    AT_F2 =                     u'F2'

class AT_ENUM:
    AT_NULL =                    0
    AT_A =                       1
    AT_A1 =                      2
    AT_B =                       3
    AT_B1 =                      4
    AT_C =                       5
    AT_C1 =                      6
    AT_C2 =                      7
    AT_D =                       8
    AT_D1 =                      9
    AT_E =                      10
    AT_F =                      11
    AT_F1 =                     12
    AT_F2 =                     13

class MULTIPART_TYPE_ENUM:
    LAST_PART_INFLECTED =        0      # usual
    FIRST_PART_INFLECTED =       1      # какой-то
    BOTH_PARTS_INFLECTED =       2      # конёк-горбунок

#
#  Main symbols
#
main_symbols = { u'м' : POS.POS_NOUN, 
                 u'мо' : POS.POS_NOUN, 
                 u'ж' : POS.POS_NOUN, 
                 u'жо' : POS.POS_NOUN, 
                 u'с' : POS.POS_NOUN, 
                 u'со' : POS.POS_NOUN, 
                 u'мо-жо' : POS.POS_NOUN, 
                 u'мн.' : POS.POS_NOUN, 
                 u'мн. неод.' : POS.POS_NOUN, 
                 u'мн. одуш.' : POS.POS_NOUN, 
                 u'мн. от' : POS.POS_NOUN, 
                 u'п' : POS.POS_ADJ, 
                 u'мс' : POS.POS_PRONOUN, 
                 u'мс-п' : POS.POS_PRONOUN_ADJ, 
                 u'мс-предик.' : POS.POS_PRONOUN_PREDICATIVE, 
                 u'числ.' : POS.POS_NUM, 
                 u'числ.-п' : POS.POS_NUM_ADJ, 
                 u'св' : POS.POS_VERB, 
                 u'нсв' : POS.POS_VERB, 
                 u'св-нсв' : POS.POS_VERB, 
                 u'н' : POS.POS_ADV, 
                 u'предл.' : POS.POS_PREPOSITION, 
                 u'союз' : POS.POS_CONJUNCTION, 
                 u'предик.' : POS.POS_PREDICATIVE, 
                 u'вводн.' : POS.POS_PARENTH, 
                 u'сравн.' : POS.POS_COMPARATIVE, 
                 u'част.' : POS.POS_PARTICLE, 
                 u'межд.' : POS.POS_INTERJECTION }

main_symb_to_gender_and_anim = { u'м' : u'M_I',
                                 u'мо' : u'M_A', 
                                 u'ж' : u'F_I', 
                                 u'жо' : u'F_A', 
                                 u'с' : u'N_I', 
                                 u'со' : u'N_A', 
                                 u'мо-жо' : u'F_A' }    # currently treated as F

uninflected_pos = [ POS.POS_ADV, 
                    POS.POS_PREPOSITION, 
                    POS.POS_CONJUNCTION, 
                    POS.POS_PREDICATIVE, 
                    POS.POS_PARENTH, 
                    POS.POS_COMPARATIVE, 
                    POS.POS_PARTICLE, 
                    POS.POS_INTERJECTION ]

#
#  Accent types
#
accent_types = { u'a' : AT.AT_A,
                 u'a\'' : AT.AT_A1, 
                 u'b' : AT.AT_B, 
                 u'b\'' : AT.AT_B1, 
                 u'c' : AT.AT_C, 
                 u'c\'' : AT.AT_C1, 
                 u'c\'\'' : AT.AT_C2, 
                 u'd' : AT.AT_D,
                 u'd\'' : AT.AT_D1, 
                 u'e' : AT.AT_E, 
                 u'f' : AT.AT_F, 
                 u'f\'' : AT.AT_F1,
                 u'f\'\'' : AT.AT_F2 }

#
#  Case values Cyrillic --> Latin
#
case_values = { u'И' : u'N',
                u'В' : u'A',
                u'Р' : u'G',
                u'П' : u'P',
                u'Д' : u'D',
                u'Т' : u'I'  }

pos_to_enum = { POS.POS_UNDEFINED : POS_ENUM.POS_UNDEFINED,
                POS.POS_NULL : POS_ENUM.POS_NULL,
                POS.POS_NOUN : POS_ENUM.POS_NOUN,
                POS.POS_VERB : POS_ENUM.POS_VERB,
                POS.POS_ADJ :  POS_ENUM.POS_ADJ,
                POS.POS_PRONOUN : POS_ENUM.POS_PRONOUN,
                POS.POS_PRONOUN_ADJ : POS_ENUM.POS_PRONOUN_ADJ,
                POS.POS_PRONOUN_PREDICATIVE : POS_ENUM.POS_PRONOUN_PREDICATIVE,
                POS.POS_NUM : POS_ENUM.POS_NUM,
                POS.POS_NUM_ADJ : POS_ENUM.POS_NUM_ADJ,
                POS.POS_ADV : POS_ENUM.POS_ADV,
                POS.POS_COMPARATIVE : POS_ENUM.POS_COMPARATIVE,
                POS.POS_PREDICATIVE : POS_ENUM.POS_PREDICATIVE,
                POS.POS_PREPOSITION : POS_ENUM.POS_PREPOSITION,
                POS.POS_CONJUNCTION : POS_ENUM.POS_CONJUNCTION,
                POS.POS_PARTICLE : POS_ENUM.POS_PARTICLE,
                POS.POS_INTERJECTION : POS_ENUM.POS_INTERJECTION,
                POS.POS_PARENTH : POS_ENUM.POS_PARENTH  }

at_to_enum = { AT.AT_NULL : AT_ENUM.AT_NULL,
               AT.AT_A : AT_ENUM.AT_A,
               AT.AT_A1 : AT_ENUM.AT_A1, 
               AT.AT_B : AT_ENUM.AT_B, 
               AT.AT_B1 : AT_ENUM.AT_B1, 
               AT.AT_C : AT_ENUM.AT_C, 
               AT.AT_C1 : AT_ENUM.AT_C1, 
               AT.AT_C2 : AT_ENUM.AT_C2, 
               AT.AT_D : AT_ENUM.AT_D,
               AT.AT_D1 : AT_ENUM.AT_D1, 
               AT.AT_E : AT_ENUM.AT_E, 
               AT.AT_F : AT_ENUM.AT_F, 
               AT.AT_F1 : AT_ENUM.AT_F1,
               AT.AT_F2 : AT_ENUM.AT_F2  }

no_break_space = u'00a0'

vowels = u'аеёиоуыэюя'

white_space_characters = [u'\t', u' ', u'00a0']

num_aspect_semicolons = 0
num_multiple_aspect_pairs = 0

#
#  Warning: print to errors file and save to DB 
#
def warning (db_cursor, message, paragraph):
    try:
        msg_out = message
        if paragraph:
            msg_out += u': '
            msg_out += paragraph.text
        errors_file.write (msg_out + '\r\n')

        txt = ''
        if paragraph:
            txt = paragraph.text
        params = (message, txt, '0')
#        db_query = u'INSERT INTO conversion_errors VALUES (NULL, ?, ?, ?)'
#        db_cursor.execute(db_query, params)
#        db_connection.commit()
    except IOError as io_ex:
        print ('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print ('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print ('Exception: %s, %s' % (sys.exc_info()[0], e))

def incomplete_parse (db_cursor, unparsed_segment, paragraph):
    try:
        params = (unparsed_segment, paragraph.text)
#        db_query = u'INSERT INTO incomplete_parses VALUES (NULL, ?, ?)'
#        db_cursor.execute(db_query, params)
#        db_connection.commit()
    except IOError as io_ex:
        print ('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print ('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print ('Exception: %s, %s' % (sys.exc_info()[0], e))

#
#  Check if chapter heading, e.g. 'A'
#
def is_chapter_heading(paragraph):
    if (paragraph is None):
        warning (db_cursor, u'Empty paragraph.', paragraph)
        return False

    if len(paragraph.text) != 1:
        return False

    if (None == paragraph.runs[0].font):
        warning (db_cursor, u'Font attribute missing', paragraph)
        return False

    if (None == paragraph.runs[0].font.size):
        warning (db_cursor, u'Font size attribute missing', paragraph)
        return False

    if (paragraph.runs[0].font.size.pt != 27.0):
        warning (db_cursor, u'Unexpected font size', paragraph)
        return False

    return True

#
#  Get run from paragraph offset
#
def run_index_from_offset(paragraph, paragraph_offset):
    length = 0
    index = 0
    for r in paragraph.runs:
        length += len(r.text)
        if paragraph_offset < length:
            return index
        index = index + 1
    
    return -1

#
#  Paragraph offset from run offset
#
def paragraph_offset_from_run_offset(paragraph, run_index, run_offset):
    if run_index >= len(paragraph.runs):
        warning (db_cursor, u'paragraph_offset_from_run_offset(): bad run index', paragraph)
        return -1

    paragraph_offset = 0
    current_run_idx = 0
    while current_run_idx < run_index:
        paragraph_offset += len(paragraph.runs[current_run_idx].text)
        current_run_idx += 1
    
    paragraph_offset += run_offset

    return paragraph_offset

#
#  Run offset from paragraph offset
#
def run_offset_from_paragraph_offset(paragraph, run_index, paragraph_offset):
    if run_index >= len(paragraph.runs):
        warning (db_cursor, u'run_offset_from_paragraph_offset(): bad run index', paragraph)
        return -1

    run_offset = paragraph_offset
    current_run_idx = 0
    while current_run_idx < run_index:
        run_offset -= len(paragraph.runs[current_run_idx].text)
        current_run_idx += 1

    if run_offset > len(paragraph.runs[run_index].text):
        warning (db_cursor, u'run_offset_from_paragraph_offset(): bad run length', paragraph)
        return -1

    return run_offset

#
#  Get offset to next separator relative to the start of paragraph
#
def offset_to_next_separator(paragraph, start_offset):

    if start_offset >= len(paragraph):
        warning (db_cursor, u'offset_to_next_separator(): bad start offset', paragraph)
        return -1

    current_offset = start_offset

    while paragraph.text[current_offset] not in [u'\t', u' ', u'00a0']:
            current_offset = current_offset + 1
            if current_offset >= len(paragraph.text):
                return -1

    return current_offset

#
#  Get offset to next non-separator character relative to the start of paragraph
#
def offset_to_next_text_segment(paragraph, start_offset):

    if start_offset >= len(paragraph.text):
        warning (db_cursor, u'offset_to_next_text_segment(): bad start offset', paragraph)
        return -1

    current_offset = start_offset

    while paragraph.text[current_offset] in [u'\t', u' ']:
        current_offset = current_offset + 1
        if current_offset >= len(paragraph.text):
            return -1

    return current_offset

#
#  Get next text segment, assume starting_offset points to the first non-separator character
#
def get_next_segment(paragraph, start_offset):
    if paragraph.text[start_offset] in [u'\t', u' ']:
        warning (db_cursor, u'Non-separator character expected', paragraph)
        return ''

    current_offset = start_offset

    while paragraph.text[current_offset] not in [u'\t', u' ']:
            current_offset = current_offset + 1
            if current_offset >= len(paragraph.text):
                return paragraph.text[start_offset:]

    return paragraph.text[start_offset:current_offset]

#
#  Check for recent changes (inverted triangle on the left)
#
def check_for_recent_changes(paragraph, locations):
    if len(paragraph.text) < 1:
        return False

    letter = ord(paragraph.text[0])
    if letter != 0xf074:
        return False

    offset = 0
    for r in paragraph.runs:
        if r.underline:
            start = offset
            length = len(r.text)
            locations.append((start, length))

        offset += len(r.text)

    return True

def check_plural_of(paragraph, offset, headword, descriptor):

    match = re.match(r'^(мн\.)\s+(от).*', paragraph.text[offset:])
    if match != None:
        if match.group(1) != None and match.group(2) != None:
            offset += match.end(2)
            descriptor.is_plural_of = True

            run_idx = run_index_from_offset(paragraph, offset-1)
            if run_idx < 0 or run_idx >= len(paragraph.runs):
                warning (db_cursor, u'Bad run index while extracting mn. ot. (ignored).', paragraph)
            elif not paragraph.runs[run_idx].italic:
                warning (db_cursor, u'Second component in mn. ot not italic (ignored).', paragraph)

            offset_to_next = offset_to_next_text_segment(paragraph, offset)
            next = get_next_segment(paragraph, offset_to_next)
            while len(next) > 0 and next[-1] in u',.;/':
                next = next[:-1]
            if not next in main_symbols.keys():
                headword.plural_of = next
                offset = offset_to_next + len(next)

            run_idx = run_index_from_offset(paragraph, offset)
            if run_idx < 0 or run_idx >= len(paragraph.runs):
                warning (db_cursor, u'Bad run index while extracting mn. ot. (ignored).', paragraph)

    return offset

#
#  Check if given offset is inside parentheses
#
def is_in_parentheses(paragraph, offset):
    if offset < 0:
        warning (db_cursor, u'is_in_parentheses(): negative offset.', paragraph)
        return False

    if offset >= len(paragraph.text):
        warning (db_cursor, u'is_in_parentheses(): offset beyond paragraph boundary.', paragraph)
        return False

    if u'(' == paragraph.text[offset] or u')' == paragraph.text[offset]:
        warning (db_cursor, u'is_in_parentheses(): character at offset is parenthesis.', paragraph)
        return False

    if 0 == offset or len(paragraph.text[offset]) - 1 == offset:
        return False

    left_open_parenth_offset = p.text.rfind(u'(', 0, offset-1)
    if -1 == left_open_parenth_offset:
        return False

    if left_open_parenth_offset >= len(p.text):
        warning (db_cursor, u'is_in_parentheses(): opening parenthesis at the end of line.', paragraph)
        return False

    close_parenth_offset = p.text.find(u')', left_open_parenth_offset+1)
    if -1 == close_parenth_offset:
        warning (db_cursor, u'is_in_parentheses(): closing parenthesis not found.', paragraph)
        return False

    if close_parenth_offset > offset:
        return True

    return False

#
# True if all characters in string are italicized
#
def is_italic(paragraph, offset, length):
    run_idx = run_index_from_offset(paragraph, offset)
    if run_idx < 0:
        warning (db_cursor, u'is_italic(): unable to find run index.', paragraph)
        return False

    italicized_text_length = 0
    while paragraph.runs[run_idx].italic:
        italicized_text_length = italicized_text_length + len(paragraph.runs[run_idx].text)
        run_idx += 1
        if run_idx >= len(paragraph.runs):
            return True

    if italicized_text_length < length:
        return False

    return True

def count_vowels(word):
    count = 0
    
    for chr in word:
        if chr in vowels:
            count += 1

    return count

def find_first_vowel_offset(word):    
    offset = 0

    for chr in word:
        if chr in vowels:
            return offset
        else:
            offset += 1

    return -1

def offset_from_syllable_pos(db_cursor, word, pos):
    
    syllable_count = 0
    for chr in word:
        if chr in vowels:
            syllable_count += 1
            if syllable_count == pos:
                return syllable_count

    return -1

'''
def find_example_section_offset (paragraph):

    offset = 0
    for run_idx in range(0, len(paragraph.runs)):
        if paragraph.runs[run_idx].font.name == 'ZapfDingbats BT':
            run_offset = paragraph.runs[run_idx].text.find(u'\uF047')
            if run_offset >= 0:
                offset += run_offset
                return offset
            else:
                return -1
        else:
            offset += len(paragraph.runs[run_idx].text)

    return -1
'''

def check_circled_digit(paragraph, source_text, paragraph_offset, inflection_group):

    paragraph_offset = offset_to_next_text_segment(paragraph, paragraph_offset)
    if paragraph_offset <= 0 or paragraph_offset >= len(source_text):
        return paragraph_offset

    match = re.match(r'^(\[?([\uF0C0\uF0C1\uF0C2\uF0C3\uF0C4\uF0C5\uF0C6\uF0C7\uF0C8])\]?){1,2}.*',
                        source_text[paragraph_offset:])
    if None == match:
        return paragraph_offset

    optional = False
    if u'[' == source_text[paragraph_offset]:
        optional = True
        paragraph_offset += 1

    while source_text[paragraph_offset] in r'\uF0C0\uF0C1\uF0C2\uF0C3\uF0C4\uF0C5\uF0C6\uF0C7\uF0C8':
        cd_number_int = ord(source_text[paragraph_offset])
        cd_number = (cd_number_int & 0xFF) - 0xBF
        if cd_number > 0 and cd_number <= 9:
            inflection_group.common_deviations.append((optional, cd_number))
        else:
            warning (db_cursor, u'Unexpected common deviation.', paragraph)
        paragraph_offset += 1
        if paragraph_offset >= len(source_text):
            if optional:
                warning (db_cursor, u'No closing bracket after circled digit.', paragraph)
            return paragraph_offset

    if optional:
        if u']' == source_text[paragraph_offset]:
            paragraph_offset += 1
        else:
            warning (db_cursor, u'No closing bracket after circled digit.', paragraph)

    return paragraph_offset

def check_cognates (paragraph, source_text, paragraph_offset, descriptor):
    
    # Handles the following references:
    #   (_от_ ...)
    #   (_женск. к_ ...)
    #   (_уменьш. к_ ...)
    #   (_увеличит. к_ ...)
    #   (_ласкат. к_ ...)
    #   (_к_ ...)
    #   (_сущ. к_ ...)
    #   (_ср._ ...)
    #   (_см. также_ ...)

    if paragraph_offset <= 0 or paragraph_offset >= len(source_text):
        return paragraph_offset

#    found = re.search(r'\((к\s+|женск\.\s+к\s+|уменьш\.\s+к|увеличит\.\s+к|ласкат\.\s+к|сущ\.\s+к|ср\.|см\.\s+также|от\s+)',
#                      paragraph.text[paragraph_offset:])

    match = re.match(r'(.*?),?\s*\((к\s+|женск\.\s+к\s+|уменьш\.\s+к|увеличит\.\s+к|ласкат\.\s+к|сущ\.\s+к|ср\.|см\.\s+также|от\s+)\s*([^\)]*)\)(.*)',
                     source_text[paragraph_offset:])
    if None == match:
        return paragraph_offset

    descriptor.cognate_relation = match.group(2)
    descriptor.cognate = match.group(3)

    return paragraph_offset

def check_plus_sign (paragraph, source_text, paragraph_offset, descriptor):

    descriptor.second_inflection_group = None;

    if paragraph_offset <= 0 or paragraph_offset >= len(source_text):
        return paragraph_offset

    match = re.match(r'^(\s*\+\s*)(.*)', source_text[paragraph_offset:])
    if None == match:
        return paragraph_offset

    if not expect_alt_inflection_group:
        warning (db_cursor, u'No comma after main symbol.', paragraph)
#        return paragraph_offset

    paragraph_offset = paragraph_offset + match.start(2)
    ig2 = InflectionGroup(descriptor)
    paragraph_offset = ig2.parse_inflection_group(p, source_text, paragraph_offset)
    ig2.multipart = MULTIPART_TYPE_ENUM.BOTH_PARTS_INFLECTED
    ig2.is_second_part = True
    if ig2 != None:
        descriptor.second_inflection_group = ig2
    descriptor.inflection_group.multipart = 2

    return paragraph_offset

def check_see_ref (paragraph, source_text, paragraph_offset, descriptor):

    match = re.match(r'^(\s*склон. см.\s+|\s*спряж. см.\s+)(.*)', source_text[paragraph_offset:])
    if None == match:
        return paragraph_offset
    
    descriptor.see_ref = match.group(2)

    return paragraph_offset

def check_impersonals_and_iteratives (paragraph, source_text, paragraph_offset, descriptor):

    match = re.match(r'^(.*?),?\s*(безл\.)(.*)', source_text[paragraph_offset:])
    if match != None:
        descriptor.impersonal = True
        paragraph_offset = paragraph_offset + match.end(2)
    match = re.match(r'^(.*?),?\s*(многокр\.)(.*)', source_text[paragraph_offset:])
    if match != None:
        descriptor.iterative = True
        paragraph_offset = paragraph_offset + match.end(2)

    return paragraph_offset

def check_verb_stem_alternations (paragraph, source_text, paragraph_offset, descriptor):

    expect_continuation = False

    match = re.match(r'^,?\s*(?:\(\-([щсcдтбгкнми]+)\-\))(.*)', source_text[paragraph_offset:])
                                # both Cyrillic and latin 'c' may appear in source
    if match != None:
        descriptor.verb_alternation = match.group(1)
        if descriptor.verb_alternation == u'c':      # Latin 
            descriptor.verb_alternation = u'с'       # --> Cyrillic
        paragraph_offset = paragraph_offset + match.start(2)
    else:
        match = re.match(r'^\s*(?:\(([абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+)\-\))(.*)', source_text[paragraph_offset:])
        if match != None:
            if u'св' != descriptor.main_symbol:
                if u'нсв' != descriptor.alt_main_symbol and u'св-нсв' != descriptor.main_symbol:
                    warning (db_cursor, u'This type of stem alternation is expected for verbs only.', paragraph)
                    return paragraph_offset, False
                if descriptor.inflection_group.type != 14:
                    warning (db_cursor, u'This type of verb stem alternation is expected for type 14 only.', paragraph)
                    return paragraph_offset, False;
            descriptor.verb_alternation = match.group(1);
            paragraph_offset = paragraph_offset + match.start(2)
        else:
            match = re.match(r'^(\s*[,;]?\s*прич\. страд\.\s*-жд-)\s*(.*)', source_text[paragraph_offset:])
            if match != None:
                descriptor.past_part_pass_zhd = True
                paragraph_offset = paragraph_offset + match.end(1)

    if paragraph_offset < len(source_text):
        if u',' == source_text[paragraph_offset]:
            expect_continuation = True
        else:
            expect_continuation = False

    return paragraph_offset, expect_continuation

def check_colon (paragraph, source_text, paragraph_offset, descriptor):

    # Looks for: ...:...
    # Except: (...:...) and [...:...]
#    match = re.match (r'\:(?![^\(]*\))\s(.+)$', source_text[paragraph_offset:])
    match = re.match(r'^(.*?)\:(?![^\(]*\))\s(.+)$', source_text)
    if None == match:
        return paragraph_offset

    colon_offset = source_text.find(u':')
    # ignore if preceded by triangle
    if paragraph.text[:colon_offset].rfind(u'\uF057') >= 0:
        return paragraph_offset

    match = re.match(r'^(.*?)\:(?![^\[]*\])\s(.+)$', source_text)
    if None == match:
        return paragraph_offset

    length = match.end(2)

    variant_offset = paragraph.text[colon_offset:].find(u'[//')
    if variant_offset >= 0 and variant_offset < length:
        length = colon_offset + variant_offset

    descriptor.contexts = preprocess_sample(paragraph, colon_offset+1, length).rstrip()
#        descriptor.contexts = descriptor.contexts[:variant_offset]

    # Handles:
    # ... :{...} ...
#    match = re.match (r'^(.*?),?\s*\:\s*\{([^\}]*)\}\s*(.*)$', source_text[paragraph_offset:])
#    if match != None:
#        descriptor.contexts = match.group(2)
#        return paragraph_offset + match.end(2)

    # ... : ... [;|%|#|$ ...]
#    match = re.match (r'^(,\s)?(\[*)?([ПР])2\s*(?:\(([^\)]+)\))?\]?',
#                      source_text[paragraph_offset:])
#    if match != None:
#        descriptor.contexts = match.group(3)
#        return paragraph_offset + match.start(4)

    return paragraph_offset

def preprocess_sample(paragraph, offset, length = -1):

    preprocessed = u''

    max_length = len(paragraph.text);
    if length >= 0:
        max_length = length

    while offset < max_length and paragraph.text[offset].isspace():
        offset += 1

    while  offset < max_length:
        if paragraph.text[offset] in vowels:
            run_idx = run_index_from_offset(paragraph, offset)
            if paragraph.runs[run_idx].font.name == 'Tim_acc':
                preprocessed += u'/'
            elif paragraph.runs[run_idx].font.name == 'Tim_pob':
                preprocessed += u'\\'            
        preprocessed += paragraph.text[offset]
        offset += 1

    return preprocessed

def check_restricted (paragraph, source_text, paragraph_offset, descriptor):

#    paragraph_offset = p.text.rfind(u'(', 0, offset-1)
    if -1 == source_text.find(u'\uF047'):
        return paragraph_offset

    match = re.match(r'^([^\uF047]*?),?\s*\uF047(.*)$', source_text[paragraph_offset:])
    if match != None:
        descriptor.restricted_contexts = preprocess_sample(paragraph, paragraph_offset+match.start(2))
        descriptor.restricted_contexts = descriptor.restricted_contexts.strip()
        if descriptor.restricted_contexts[-1] == ';':
            descriptor.restricted_contexts = descriptor.restricted_contexts[:-1]

#    return paragraph_offset + len(match.group(2))
    return paragraph_offset


#    return paragraph_offset

def check_difficult_and_missing_forms(paragraph, source_text, paragraph_offset, descriptor):
        
    semicolon = False

    if paragraph_offset < 0 or paragraph_offset > len(source_text):
        return paragraph_offset

    offset_to_next = paragraph_offset

    pattern = r"""
    (.*?)[,]\s+
    (
    Р\.\sмн.\sзатрудн\. |                   # --> Noun_Pl_G
    мн\.\sзатрудн\. |                       # --> Noun_Pl_* ??
    косв\.\sзатрудн\. |                     # is this used
    косв\.\sформы\sзатрудн\. |              # --> !*_Sg_N
    кф\sж\sзатрудн\. |                      # --> AdjS_F
    сравн\.\sзатрудн\. |                    # --> AdjComp
    кф\sи\sсравн\.\sзатрудн\. |             # --> AdjS_*, AdjComp
    кф\sм\sзатрудн\. |                      # --> AdjS_M
    Р\.\sзатрудн\. |                        # is this used? should be Noun_*_G
    деепр\.\sзатрудн\. |                    # --> VAdv_Pres     see Vvedenije, p. 20
    наст\.\s1\sед\.\sзатрудн\. |            # --> Pres_Sg_1
    повел\.\sзатрудн\. |                    # --> Impv_*_*
    буд\.\s1\sед\.\sзатрудн\. |             # --> Pres_Sg_1 
    повел\.\sи\sдеепр\.\sзатрудн\. |        # --> Impv_*_*, VAdv_Pres
    прич\.\sстрад\.\sнаст\.\sзатрудн\. |    # --> PPresPL_*_Sg_*, PPresPL_Pl_*, PPresPS_*
    прош\.\sм\sзатрудн\. |                  # --> Past_M
    буд\.\sи\sповел\.\sзатрудн\.            # --> Pres_*_*, Impv_*_*
    )
    (.*)
    """

    dictDifficulties = { r"Р. мн. затрудн." : ["Noun_Pl_G"],
                         r"мн. затрудн." : ["Noun_Pl_*"],
                         r"косв. затрудн." : ["!*_Sg_N"],            # ? doesn't exist?
                         r"косв. формы затрудн." : ["!*_Sg_N"],
                         r"кф ж затрудн." : ["AdjS_F"],
                         r"сравн. затрудн." : ["AdjComp"],
                         r"кф и сравн. затрудн." : ["AdjS_*", "AdjComp"],
                         r"кф м затрудн." : ["AdjS_M"],
                         r"Р. затрудн." : ["Noun_*_G"],               # ? doesn't exist?
                         r"деепр. затрудн." : ["VAdv_Pres"],
                         r"наст. 1 ед. затрудн." : ["Pres_Sg_1"],
                         r"повел. затрудн." : ["Impv_*_*"],
                         r"буд. 1 ед. затрудн." : ["Pres_Sg_1"],
                         r"повел. и деепр. затрудн." : ["Impv_*_*", "VAdv_Pres"],
                         r"прич. страд. наст. затрудн." : ["PresPL_*_Sg_*", "PPresPL_Pl_*", "PPresPS_*"],
                         r"прош. м затрудн." : ["Past_M"],
                         r"буд. и повел. затрудн." : ["Pres_*_*", "Impv_*_*"] }

    zatrudn = u''
    missing = u''

    match = re.match(pattern, source_text[paragraph_offset:], re.VERBOSE)
    if match != None:
#        m1 = match.group(1)
#        if len(m1) > 0:
#            incomplete_parse (db_cursor, m1, paragraph)
#        m3 = match.group(3)
#        if len(m3) > 0:
#            incomplete_parse (db_cursor, m3, paragraph)
        descriptor.has_difficult_forms = True
        d = match.group(2)
        if d not in dictDifficulties.keys():
            warning (db_cursor, u'Difficult form label not in the list.', paragraph)
        else:
            descriptor.difficult_forms.extend(dictDifficulties[d])

        offset_to_next = paragraph_offset + match.end(2) + 1

    else:
        pattern = r"""
        (.*?)[,]\s+
        (
        Р\.\sмн\.\sнет |                                # --> Noun_Pl_*
        пф\sнет |                                       # --> AdjL_*_Sg_*, AdjL_Pl_*
        прош\.\sнет |                                   # --> Past_*
        кф\sи\sсравн\.\sнет |                           # --> AdjS_*, AdjComp
        кф\sм\sнет |                                    # --> AdjS_M
        других\sформ\sнет |                             # --> This_Form_Only
        кроме\sИ\.,\sформ\sнет |                        # --> !Pronoun_*_* (only некто)
        косв\.\sформ\sнет |                             # --> !*_Sg_N                    
        деепр\.\sнет |                                  # --> VAdv_Pres    see Vvedenije, p. 20
        буд\.\sнет |                                    # --> Pres_*_*
        страд\.\sнет |                                  # --> PPastP_*_Sg_*, PPastP_Pl_*, PPastPS_*, PPresP_*_Sg_*, PPresP_Pl_*, PPresPS_*
        повел\.\sнет |                                  # --> Impv_*_*
        в лит\.\sязыке\sнаст\.\sи\sбуд\.\sнет |         # --> Pres_*_*
        прич\.\sстрад\.\sнаст\.\sнет |                  # --> PPresP_*_Sg_*, PPresP_Pl_*,, PPresP_S
        буд\s.\s1\sед\.\sнет |                          # --> Pres_Sg_1
        наст\.\s1\sед\.\sнет |                          # --> Pres_Sg_1
        прош\.\sнет |                                   # --> Past_*
        прич\.\sпрош\.\sнет |                           # --> PPastAL_*_Sg_*, PPastAL_Pl_*, PPastAS_*, PPastP_*_Sg_*, PPastP_Pl_*, PPastPS_*
        буд\.\sв\sлит\.\sязыке\sнет                     # --> Pres_*_*
        )
        (.*)
    """
        dictMissingForms = {r"Р. мн. нет" : ["Noun_Pl_G"],
                            r"пф нет" : ["AdjL_*_Sg_*", "AdjL_Pl_*"],
                            r"кф и сравн. нет" : ["AdjS_*", "AdjComp"],
                            r"кф м нет" : ["AdjS_M"],
                            r"других форм нет" : ["SingleForm"],
                            r"кроме И. форм нет" : ["!*_Sg_N"],  # ? doesn't exist?
                            r"косв. форм нет" : ["!*_Sg_N"],
                            r"прош. нет" : ["Past_*"],
                            r"деепр. нет" : ["VAdv_Pres"],
                            r"буд. нет" : ["Pres_*_*"],
                            r"страд. нет" : ["PPresPL_*_Sg_*", "PPresPL_Pl_*", "PPresPS_*", "PPastPL_*_Sg_*", "PPastPL_Pl_*", "PPastPS_*"],                          #  ???? страд. прич?
                            r"повел. нет" : ["Impv_*_*"],
                            r"в лит. языке наст. и буд. нет" : ["Pres_*_*"],
                            r"прич. страд. наст. нет" : ["PPresPL_*_Sg_*", "PPresPL_Pl_*", "PPresPS_*"],
                            r"буд. 1 ед. нет" : ["Pres_Sg_1"],
                            r"наст. 1 ед. нет" : ["Pres_Sg_1"],
                            r"прош. нет" : ["Past_*"],
                            r"прич. прош. нет": ["PPastAL_*_Sg_*", "PPastAL_Pl_*", "PPastAS_*", "PPastPL_*_Sg_*", "PPastPL_Pl_*", "PPastPS_*"],
                            r"буд. в лит. языке нет" : ["Pres_*_*"] }

        match = re.match(pattern, source_text[paragraph_offset:], re.VERBOSE)
        if match != None:
#            m1 = match.group(1)
#            if len(m1) > 0:
#                incomplete_parse (db_cursor, m1, paragraph)
#            m3 = match.group(3)
#            if len(m3) > 0:
#                incomplete_parse (db_cursor, m3, paragraph)
            descriptor.has_missing_forms = True
            m = match.group(2)
            if m not in dictMissingForms.keys():
                warning(db_cursor, u'Missing form label not in the list.', paragraph)
            else:
                descriptor.missing_forms.extend(dictMissingForms[m])

            if u"пф нет" == m:
                descriptor.no_long_forms = True
            offset_to_next = paragraph_offset + match.end(2) + 1

    return offset_to_next

def check_yo_and_o(paragraph, paragraph_offset, descriptor):
    paragraph_offset = offset_to_next_text_segment(paragraph, paragraph_offset)
    if paragraph_offset < 0 or paragraph_offset > len(paragraph.text):
        warning (db_cursor, u'Bad start offset.', paragraph)
        return paragraph_offset

    if u',' == paragraph.text[paragraph_offset]:
        current_offset = offset_to_next_text_segment(paragraph, paragraph_offset + 1)
        if current_offset < 0 or current_offset > len(paragraph.text):
            warning (db_cursor, u'Bad start offset.', paragraph)
            return current_offset
    
        if u'ё' == paragraph.text[current_offset] and (current_offset == len(paragraph.text) - 1 \
            or (current_offset < len(paragraph.text) - 1 and ' ' == paragraph.text[current_offset + 1])):
            descriptor.yo = True
            paragraph_offset = current_offset + 1

        if u'о' == paragraph.text[current_offset] and (current_offset == len(paragraph.text) - 1 \
            or (current_offset < len(paragraph.text) - 2 and ' ' == paragraph.text[current_offset + 1] and \
                u'р' == paragraph.text[current_offset + 2])):
            descriptor.o = True
            paragraph_offset = current_offset + 1

    return paragraph_offset

def check_loc2_and_gen2(paragraph, paragraph_offset, descriptor):
    paragraph_offset = offset_to_next_text_segment(paragraph, paragraph_offset)
    if paragraph_offset < 0 or paragraph_offset > len(paragraph.text):
        warning (db_cursor, u'Bad start offset.', paragraph)
        return paragraph_offset

    match = re.match(r'^(,\s)?(\[*)?([ПР])2\s*(?:\(([^\)]+)\))?\]?(?:,\s)?(Р2)?', paragraph.text[paragraph_offset:])
    if match:
        if match.group(2) != None and len(match.group(2)) > 0:          # left square bracket
            descriptor.loc2_optional = True
        if match.group(3) != None:
            if u'П' == match.group(3):
                descriptor.loc2 = True
            elif u'Р' == match.group(3):
                descriptor.gen2 = True
            else:
                warning (db_cursor, u'Loc2 or Gen2 parsing error.', paragraph)
                return -1

        if descriptor.loc2_optional and not descriptor.loc2:
            warning (db_cursor, u'Loc2 or Gen2 parsing error.', paragraph)
            return -1

        if match.group(4):
            if not descriptor.loc2:
                warning (db_cursor, u'Loc2 or Gen2 parsing error.', paragraph)
#                return -1
            if u'в' == match.group(4) or u'на' == match.group(4) or u'во' == match.group(4):
                descriptor.loc2_preposition = match.group(4)

        if match.group(5):
            if not descriptor.loc2:
                warning (db_cursor, u'Gen2 but no Loc2.', paragraph)
#                return -1
            descriptor.gen2 = True

        paragraph_offset += len(match.group(0))
            
    return paragraph_offset

#   аб<ак м 3а [//аб<ака]
#   ак<ант м 1а [//_устар._ ак<анф]
def check_square_brackets(paragraph, paragraph_offset, descriptor):
    paragraph_offset = offset_to_next_text_segment(paragraph, paragraph_offset)
    if paragraph_offset < 0 or paragraph_offset > len(paragraph.text):
        warning (db_cursor, u'Bad start offset.', paragraph)
        return paragraph_offset

    found = False
    left_bracket_offset = paragraph.text.find(u'[', paragraph_offset)
    if left_bracket_offset < 0:
        return paragraph_offset

#    if is_in_parentheses(paragraph, left_bracket_offset):
#        ??? not handle? error?

#    if left_bracket_offset > left_bracket_offset:
#        incomplete_parse (db_cursor, paragraph.text[paragraph_offset:left_bracket_offset], paragraph)

    right_bracket_offset = paragraph.text.find(u']', left_bracket_offset + 1)
    if right_bracket_offset < 0:
        warning (db_cursor, u'No closing square bracket.', paragraph)
        return -1

    double_slash = False
    offset = left_bracket_offset + 1
    if paragraph.text[offset:].startswith(r'//'):
        double_slash = True
        offset += 2
        if offset >= len(paragraph.text) or offset >= right_bracket_offset:
            warning (db_cursor, u'No data after double slash.', paragraph)
            return -1

    offset = offset_to_next_text_segment(paragraph, offset)
    if offset < 0 or offset >= len(paragraph.text) or offset >= right_bracket_offset:
        warning (db_cursor, u'Bad offset.', paragraph)
        return offset

    run_idx = run_index_from_offset(paragraph, offset)
    if run_idx < 0 or run_idx > len(paragraph.runs):
        warning (db_cursor, u'Error finding run index.', paragraph)
        return -1

    comment = u''
    while paragraph.runs[run_idx].italic or len(paragraph.runs[run_idx].text) < 1:
        comment += paragraph.runs[run_idx].text
        run_idx += 1
        if run_idx >= len(paragraph.runs):
            warning (db_cursor, u'No text following comment after opening square bracket.', paragraph)
            return offset

    if len(comment) > 0:
        offset += len(comment)
        if offset < len(paragraph.text) and u'.' == paragraph.text[offset]: # sometimes trailing '.' is not marked as italic
            comment += paragraph.text[offset]
            offset += 1
        headword.variant_comment = comment

    offset = offset_to_next_text_segment(paragraph, offset)
    if offset < 0 or offset > len(paragraph.text):
        warning (db_cursor, u'Unable to find offset to variant headword.', paragraph)
        return offset

    has_headword = False
    has_descriptor = False
    headword_offset = -1

    match = re.match(r'^([1-5])(-[1-5])*', paragraph.text[offset:right_bracket_offset])
    if match:
        if match.group(2) != None:
            offset += match.end(2)
        else:
            offset += match.end(1)

    run_idx = run_index_from_offset(paragraph, offset)
    if run_idx < 0 or run_idx >= len(paragraph.runs):
        warning (db_cursor, u'Bad run index (ignored).', paragraph)
    elif paragraph.runs[run_idx].bold:
        offset = offset_to_next_text_segment(paragraph, offset)
        if offset < 0 or offset > len(paragraph.text):
            warning (db_cursor, u'Unable to find offset to variant headword.', paragraph)
            return offset
        else:
            headword_offset = offset
            run_idx = headword.parse_source_data(paragraph, headword_offset, True) # parse as variant headword
            offset = paragraph_offset_from_run_offset(paragraph, run_idx, 0)
            offset = offset_to_next_text_segment(paragraph, offset)
            if offset < 0 or offset > len(paragraph.text):
                warning (db_cursor, u'Unable to find offset to variant headword.', paragraph)
                return offset
            if offset >= right_bracket_offset:
                return offset
            has_headword = True

#   ак<анф м 1а [//ак<ант (_см._)]
    if has_headword and paragraph.text[offset:].startswith(u'(см.)'):
        if len(headword.variant) < 1:
            warning (db_cursor, u'Expected variant headword not found.', paragraph)
        else:
            headword.see_ref = headword.variant     # TODO: this is redundant, bool should suffice
        offset += 5
        offset = offset_to_next_text_segment(paragraph, offset)
        return offset

#   к<апсель м 2а [_проф._ м 2с"1"]
#   б<ондарь мо 2а [//бонд<арь мо 2в] 
#   врожд<ённый п 1*а"1" [//п 1*а/в"2", ё]
    offset = offset_to_next_text_segment(paragraph, offset)
    if offset < 0 or offset > len(paragraph.text):
        warning (db_cursor, u'Unable to find offset to variant headword.', paragraph)
        return offset
    if offset >= right_bracket_offset:
        return offset

    variant_descriptor = Descriptor(paragraph)
    next = get_next_segment(paragraph, offset)
    if len(next) > 0:
        if next in main_symbols:
            semicolon, offset = variant_descriptor.parse_descriptor(headword, paragraph, offset, False, True)
            if semicolon:
                warning (db_cursor, u'Unexpected semicolon inside square brackets.', paragraph)
                return offset
            has_descriptor = True
        if has_headword:
            if headword_offset < 0 or headword_offset > len(paragraph.text) or headword_offset >= right_bracket_offset:
                warning (db_cursor, u'Unable to find offset to variant headword.', paragraph)
                return offset
            variant_headword = Headword()
            variant_headword.parse_source_data(paragraph, headword_offset, False)
            variant_headword.paragraph = paragraph
            variant_headword.lead_comment = comment
            if has_descriptor:
                dictionary[variant_headword].append(variant_descriptor)
            else:
                dictionary[variant_headword].append(descriptor)
        else:
            if has_descriptor:
                dictionary[headword].append(variant_descriptor)
            else:
                dictionary[headword].append(descriptor)

    offset = offset_to_next_text_segment(paragraph, offset)
    if offset < len(paragraph.text) and offset < right_bracket_offset:
        incomplete_parse(db_cursor, paragraph.text[offset:right_bracket_offset], paragraph)

    return right_bracket_offset + 1

def preprocess_aspect_pair_text(paragraph, paragraph_offset, type=0):
    italic = False
    current_offset = paragraph_offset

    koko = paragraph.text[current_offset-1:]
    run_idx = run_index_from_offset(paragraph, current_offset)
    if paragraph.runs[run_idx].italic and koko[0] != '(':
        print(f'*************** {paragraph.text}')

    preprocessed = u''
    while  current_offset < len(paragraph.text) and paragraph.text[current_offset] != u')' and not paragraph.text[current_offset] in white_space_characters:
        run_idx = run_index_from_offset(paragraph, current_offset)
        if paragraph.runs[run_idx].font.name == 'Tim_acc':
            preprocessed += u'/'
        elif paragraph.runs[run_idx].font.name == 'Tim_pob':
            preprocessed += u'\\'            
        preprocessed += paragraph.text[current_offset]
        current_offset += 1

    return preprocessed, italic

def handle_sv_to_nsv(paragraph, paragraph_offset):
    type = 0
    data = u''
    italic = False  # currently unused
    sv_nsv_match = re.match(u'(I{1,3}).*', paragraph.text[paragraph_offset:])
    if sv_nsv_match:
        if sv_nsv_match.group(1) != None:
#            descriptor.has_aspect_pair = True
            type = -1 * len(sv_nsv_match.group(1))
            paragraph_offset += sv_nsv_match.end(1)
            if (u'I') == sv_nsv_match.group(1):
                sv_nsv_vowel_match = re.match(r'(\((\-[ёоа]\-)\)).*', paragraph.text[paragraph_offset:])
                if sv_nsv_vowel_match:      # single vowel
                    data, italic = preprocess_aspect_pair_text(paragraph, paragraph_offset+sv_nsv_vowel_match.start(2))
                    paragraph_offset += sv_nsv_vowel_match.end(1)
                else:                       # word or fragment
                    sv_nsv_word_match = re.match(r'\(([абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+)\).*', paragraph.text[paragraph_offset:])
                    if sv_nsv_word_match:
                        data, italic = preprocess_aspect_pair_text(paragraph, paragraph_offset+sv_nsv_word_match.start(1))
                        paragraph_offset += sv_nsv_word_match.end(1)
            elif (u'II') == sv_nsv_match.group(1) or (u'III') == sv_nsv_match.group(1):
                sv_nsv_word_match = re.match(r'\(([абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+)\).*', paragraph.text[paragraph_offset:])
                if sv_nsv_word_match:
                    data, italic = preprocess_aspect_pair_text(paragraph, paragraph_offset+sv_nsv_word_match.start(1))
                    paragraph_offset += sv_nsv_word_match.end(1)
            else:
                warning(db_cursor, r'Unexpected symbol(s) in SV to NSV type field', paragraph)

    else:
        length = 0
        while paragraph_offset+length < len(paragraph.text) and not (paragraph.text[paragraph_offset+length] in white_space_characters):
            length += 1
        data, italic = preprocess_aspect_pair_text(paragraph,  paragraph_offset)
        paragraph_offset += length

    return paragraph_offset, type, data

def handle_nsv_to_sv(paragraph, paragraph_offset):
    type = 0
    data = u''
    italic = False      # currently not changed
    nsv_sv_match = re.match(r'(\d{1,2}).*', paragraph.text[paragraph_offset:])
    if nsv_sv_match:
        type = int(nsv_sv_match.group(1))
        if type < 1 or type > 16:
            warning (db_cursor, u'handle_nsv_to_sv(): unexpected inflection type number.', paragraph)
            return paragraph_offset, type, data
#        descriptor.has_aspect_pair = True
        paragraph_offset += nsv_sv_match.end(1)
        nsv_sv_vowel_match = re.match(r'(\(\-([ёо])\-\)).*', paragraph.text[paragraph_offset:])
        if nsv_sv_vowel_match:
            vowel = nsv_sv_vowel_match.group(2)
            stressed_o = False
            if u'о' == vowel:
                run_idx = run_index_from_offset(paragraph, paragraph_offset+nsv_sv_vowel_match.start(2))
                if u'Tim_acc' == paragraph.runs[run_idx].font.name:
                    data = u'-/о-'
                else:
                    data = u'-о-'
            else:
                data = u'-' + nsv_sv_vowel_match.group(2) + u'-'
        else:
            nsv_sv_word_match = re.match(r'(\((.+?)\)).*', paragraph.text[paragraph_offset:])
            if nsv_sv_word_match:
                data, italic = preprocess_aspect_pair_text(paragraph, paragraph_offset+nsv_sv_word_match.start(2), type)
                paragraph_offset += nsv_sv_word_match.end(2) + 1
    else:
        whole_word_match = re.match(r'^([абвгдеёжзийклмнопрстуфхцчшщъыьэюя]+)(.*)', paragraph.text[paragraph_offset:])
        if whole_word_match is not None:
            data, italic = preprocess_aspect_pair_text(paragraph, paragraph_offset+whole_word_match.start(1))
            paragraph_offset += whole_word_match.end(1)

    return paragraph_offset, type, data

def check_stored_aspect_pairs(descriptor, ap_type):
    global num_multiple_aspect_pairs

    sql_select = f"""SELECT ap.descriptor_id, d.trailing_comment, ap.type, ap.data, ap.comment FROM aspect_pair ap
	INNER JOIN descriptor d ON d.id=ap.descriptor_id  
	INNER JOIN inflection i ON i.descriptor_id=d.id
	WHERE d.graphic_stem='{descriptor.graphic_stem}'
		AND d.main_symbol='{descriptor.main_symbol}'
		AND d.is_reflexive={descriptor.is_reflexive}
		AND i.inflection_type={descriptor.inflection_group.type}
		AND i.accent_type1={descriptor.inflection_group.accent_type_1}
		AND i.accent_type2={descriptor.inflection_group.accent_type_2}
		AND d.trailing_comment='{descriptor.trailing_comment}';"""

    db_cursor.execute(sql_select)
    rc = True
    rows = db_cursor.fetchall()
    descriptor_id = 0
    if len(rows) != 1:
        rc = False
        num_multiple_aspect_pairs += 1
#        print(f'Number of aspect pair entries: {len(rows)}')
        for row in rows:
            print(f'Skipped:\t{headword.headword_text}: {row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}')
    else:
        row = rows[0]
        descriptor_id = rows[0][0]
        if ap_type == row[0]:
            rc = False
            print(f'Duplicate aspect pair type: {headword.headword_text}: {row[0]}|{row[1]}|{row[2]}|{row[3]}')

    return rc, descriptor_id

def check_stored_aspect_pair_variants(descriptor, ap_type, alt_ap_type, separator, data):
    global num_multiple_aspect_pairs

    sql_select = f"""
    SELECT ap.id, ap.descriptor_id, d.trailing_comment, ap.type, ap.data, ap.is_variant, ap.comment, ap.is_edited 
    FROM aspect_pair ap
	INNER JOIN descriptor d ON d.id=ap.descriptor_id  
	INNER JOIN inflection i ON i.descriptor_id=d.id
	WHERE d.graphic_stem='{descriptor.graphic_stem}'
		AND d.main_symbol='{descriptor.main_symbol}'
		AND d.is_reflexive={descriptor.is_reflexive}
		AND i.inflection_type={descriptor.inflection_group.type}
		AND i.accent_type1={descriptor.inflection_group.accent_type_1}
		AND i.accent_type2={descriptor.inflection_group.accent_type_2}
		AND d.trailing_comment='{descriptor.trailing_comment}';
    """

    data_applies_to_both = False
    if len(separator) > 0:
        if separator == ',':
            data_applies_to_both = True
        else:
            print(f'Error unexpected separator value: {separator}')
            return False, descriptor

    db_cursor.execute(sql_select)
    rc = True
    rows = db_cursor.fetchall()
    descriptor_id = 0
    if len(rows) != 1:
        rc = False
        num_multiple_aspect_pairs += 1
#        print(f'Number of aspect pair entries: {len(rows)}')
        for row in rows:
            print(f'Skipped:\t{headword.headword_text}: {row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}')
        return rc, descriptor_id
    else:
        row = rows[0]
        ap_id = row[0]
        descriptor_id = row[1]
        trailing_comment = row[2]
        gogo = row[3]
        if int(ap_type) != row[3]:
            rc = False
            print(f'Skipped duplicate aspect pair type: {headword.headword_text}: {row[0]}|{row[1]}|{row[2]}|{row[3]}')
            return rc, descriptor_id

    data1 = ''
    if data_applies_to_both:
        data1 = data
    sql_update = f"""  UPDATE aspect_pair 
                       SET type = {ap_type}, data = '{data1}', is_variant = 0 
                       WHERE descriptor_id = {descriptor_id} AND id = {ap_id}; """
    db_cursor.execute(sql_update)

    params = (descriptor_id,
              alt_ap_type,
              data,
              1,
              '',
              0)

    sql_insert = u'INSERT INTO aspect_pair VALUES (NULL, ?, ?, ?, ?, ?, ?)'
    db_cursor.execute(sql_insert, params)

    db_connection.commit()

    return rc, descriptor_id

def insert_alt_nsv_to_sv_pair(paragraph, descriptor_id, type, data, data_no_use, comment):
    is_variant = True
    is_edited = False
    params = (descriptor_id,
              type,
              data,
              is_variant,
              comment,
              is_edited)

    sql_insert = u'INSERT INTO aspect_pair VALUES (NULL, ?, ?, ?, ?, ?, ?)'
    try:
#        print(f'Paragraph: {paragraph.text}')
#        print(f'\tInserting: descriptor ID: {descriptor_id}, type: {type}, data: {data}, comment: {comment}')
        db_cursor.execute(sql_insert, params)
        ap_id = db_cursor.lastrowid
        db_connection.commit()
    except IOError as io_ex:
        print('IO Error.', io_ex.args[0])
    except sqlite3.Error as sqlite_ex:
        print('sqlite3 error: ', sqlite_ex.args[0])
    except Exception as e:
        print('Exception: %s, %s' % (sys.exc_info()[0], e))

    return True

def handle_aspect_semicolon(aspect_sym_idx, paragraph, descriptor):
    global num_aspect_semicolons

    if aspect_sym_idx < len(paragraph.text) and (';' == paragraph.text[aspect_sym_idx]):
        semicolon_match = re.match(r';\s(\D+\s)?(\d{1,2})(?://\s(\d{1,2}))?(,?)(.*)?', paragraph.text[aspect_sym_idx:])
        if semicolon_match:
            comment = semicolon_match.group(1)
            type = semicolon_match.group(2)
            alt_type = semicolon_match.group(3)
            comma = semicolon_match.group(4)
#                    data = semicolon_match.group(5)
            data_no_use = ''
            data_offset = aspect_sym_idx+semicolon_match.span(5)[0]
            italic = False
            data, italic = preprocess_aspect_pair_text(paragraph, data_offset+1)
            if len(data) > 0 and data[0] == '(':
                data = data[1:]
#                    run_idx = run_index_from_offset(paragraph, data_offset+1)   # enclosing parenth is not italicized
#                    if paragraph.runs[run_idx].italic:
#                        data_no_use = data
#                        data = ''
#            print(f'-------- data = {data}, italicized = {italic}')
#                   if len(data) > 0:
#                       data_match = re.match(r'\s*?\((\S+?)\).*', data)
#                       if data_match:
#                           data = data_match.group(1)
#           out_str = f'Semicolon: {headword.headword_text}: comment={comment} | type={type}'
#            if alt_type is not None:
#                print(f'Semicolon:\t{paragraph.text}')
#                out_str += f'//{alt_type} | comma={comma} | data={data}'
#                print(out_str)
#                    print(f'Semicolon: comment={comment} type={type} alt. type={alt_type} data={data}')
            descriptor.graphic_stem = descriptor.make_graphic_stem(headword.headword_text)
            check_trailing_comment(paragraph, descriptor.post_inflection_group_offset, descriptor)

# Italicized forms must be marked:
#                    data2 = paragraph.text[paragraph_offset:]
#                    if len(data2) > 0:
#                        run_idx = run_index_from_offset(paragraph,
#                                                        paragraph_offset + 1)  # enclosing parenth is not italicized
#                        if paragraph.runs[run_idx].italic:
#                            print(f'++++++++++++{data2}')
#
            update, descriptor_id = check_stored_aspect_pairs(descriptor, type)
            if update:
                print(f'Semicolon:\t{paragraph.text}')
                insert_alt_nsv_to_sv_pair(paragraph, descriptor_id, type, data, data_no_use, comment)
                if alt_type is not None:
                    insert_alt_nsv_to_sv_pair(paragraph, descriptor_id, alt_type, data, data_no_use, comment)

            num_aspect_semicolons += 1
#            alternate_match = re.match(r'.*?\s*?//\s*?(\S+?)\s?(\d{1,2})(.*)', paragraph.text[aspect_sym_idx:])
#            if alternate_match:
#                print('Alternate: {}'.format (paragraph.text))
#                descriptor.aspect_alt_pair_comment = alternate_match.group(1)
#                aspect_sym_idx += alternate_match.start(2)
#                aspect_sym_idx, descriptor.aspect_alt_pair_type, descriptor.aspect_alt_pair_data = handle_nsv_to_sv(paragraph, aspect_sym_idx)

def handle_aspect_variant(aspect_sym_idx, paragraph, descriptor):
    global num_aspect_semicolons

    variant_match = re.match(r'(\d{1,2})(?://\s(\d{1,2}))?(,?)(.*)?', paragraph.text[aspect_sym_idx:])
    if variant_match:
        type = variant_match.group(1)
        alt_type = variant_match.group(2)
        separator = variant_match.group(3)
        if alt_type:
            update, descriptor_id = check_stored_aspect_pairs(descriptor, alt_type)
#            if update:
#                update_nsv_to_sv_pair(paragraph, descriptor_id, type, data, data_no_use, comment)
            is_variant = True
            is_edited = False
            data_offset = aspect_sym_idx + variant_match.span(4)[0]
            data, italic = preprocess_aspect_pair_text(paragraph, data_offset+1)
            if len(data) > 0 and data[0] == '(':
                data = data[1:]

            descriptor.graphic_stem = descriptor.make_graphic_stem(headword.headword_text)
            check_trailing_comment(paragraph, descriptor.post_inflection_group_offset, descriptor)

            print(f'Variant:\t{paragraph.text}')
            check_stored_aspect_pair_variants(descriptor, type, alt_type, separator, data)

    return True


def check_aspect_symbol(paragraph, paragraph_offset, descriptor, length = -1):
    global num_aspect_semicolons
    global num_multiple_aspect_pairs

    end = len(paragraph.text)
    if length > 0:
        end = length

    found = False
    aspect_sym_idx = -1
    offset = paragraph.text.rfind(u'р', 0, end)
    while offset >= 0 and not found:
        run_idx = run_index_from_offset(paragraph, offset)
        if u'ZapfDingbat Dop' == paragraph.runs[run_idx].font.name:
            found = True
            aspect_sym_idx = offset
        else:
            offset = offset = paragraph.text.rfind(u'р', 0, offset-1)

    if not found:
        return False, paragraph_offset

    descriptor.has_aspect_pair = True
    aspect_sym_idx += 1
    
    if u'св' == descriptor.main_symbol:
        type = 0
        data = u''
        aspect_sym_idx, descriptor.aspect_pair_type, descriptor.aspect_pair_data = handle_sv_to_nsv (paragraph, aspect_sym_idx)
        alternate_match = re.match(r'\s*?//\s?(\S+?)\s?(I{1,3}).*', paragraph.text[aspect_sym_idx:])
        if alternate_match:
            descriptor.aspect_alt_pair_comment = alternate_match.group(1)
            aspect_sym_idx += alternate_match.start(2)
            aspect_sym_idx, descriptor.aspect_alt_pair_type, descriptor.aspect_alt_pair_data = handle_sv_to_nsv(paragraph, aspect_sym_idx)
    elif u'нсв' == descriptor.main_symbol:
#        offset_to_dash = paragraph.text[aspect_sym_idx:].find('(-')
#        if offset_to_dash > 0:
#            print(f'================ {paragraph.text}')
#        nsv_sv_match = re.match(r'(\d).*', paragraph.text[aspect_sym_idx:])
        nsv_sv_match = re.match(r'(\d).*', paragraph.text[aspect_sym_idx:])
        if nsv_sv_match:
# aspect semicolon:
            new_aspect_sym_idx = aspect_sym_idx+nsv_sv_match.start(1)
            new_aspect_sym_idx, descriptor.aspect_pair_type, descriptor.aspect_pair_data = handle_nsv_to_sv(paragraph, new_aspect_sym_idx)
            handle_aspect_semicolon(new_aspect_sym_idx, paragraph, descriptor)
# end aspect semicolon
            handle_aspect_variant(aspect_sym_idx, paragraph, descriptor)
        else:
            aspect_sym_idx, descriptor.aspect_pair_type, descriptor.aspect_pair_data = handle_nsv_to_sv(paragraph, aspect_sym_idx)
    return True, offset

def check_trailing_comment(paragraph, paragraph_offset, descriptor):
    if paragraph_offset < 0 or paragraph_offset > len(paragraph.text):
        return paragraph_offset

#    while paragraph_offset <  len(paragraph.text) and not paragraph.text[paragraph_offset] in [' ', '\t']:
#        paragraph_offset += 1

    offset_to_next = paragraph_offset

    match = re.match (r'^(\s*?)\((.+?)\)\s*?(.*)$', paragraph.text[paragraph_offset:])
    if match is not None:
        descriptor.trailing_comment = match.group(2)
        m3 = match.group(3)
        if len(m3) > 0:
            if ';' != m3:
                incomplete_parse (db_cursor, m3, paragraph)
        offset_to_next = paragraph_offset + match.end(2) + 1

    return offset_to_next

def extract_stress_marks(source, paragraph):
    
    shift = 0
    stress_dict = {}
    new_text = u''
    
    shift = 0
    for at, char in enumerate(source):
        found = False
        if u'/' == char:
            found = True
            if at < len(source) - 1 and source[at+1] in vowels:                
                stress_dict[at-shift] = True
        if u'\\' == char:
            found = True
            if at < len(source) - 1 and source[at+1] in vowels:                
                stress_dict[at-shift] = False
        if found:
            shift = shift + 1
        else:
            new_text += char

    for yo_pos, char in enumerate(new_text):
        if u'ё' == char:
            if yo_pos in stress_dict:
                if True == stress_dict[yo_pos]:
                    warning (db_cursor, u'Warning: main stress on yo.', paragraph)
            else:
                stress_dict[yo_pos] = True

    if len(new_text) < 1:
        new_text = source

    if len(stress_dict) == 0:
        if count_vowels(new_text) != 1:
            warning (db_cursor, u'Warning: no stress marks and not monosyllabic.', paragraph)
        else:
            stress_pos = find_first_vowel_offset(new_text)
            if stress_pos < 0:
                warning (db_cursor, u'Warning: vowel not found.', paragraph)
            else:
                stress_dict[stress_pos] = True

    return new_text, stress_dict

# Assume stress is marked by preceding '/', return syllable num
def stress_syllable_pos(word):
    count = 0
    for chr in word:
        if chr == u'/' or chr == u'ё':
            return count
        if chr in vowels:
            count += 1
    return -1

def mark_stress_syllable_pos(source, pos):
    word = source.replace(u'/', u'')
    vowel_count = 0
    offset = 0
        
    for chr in word:
        if chr in vowels:
            if vowel_count == pos:
                return word[:offset] + u'/' + word[offset:]
            elif u'ё' == chr:
                word = word[:offset] + u'е' + word[offset:]

            vowel_count += 1
        offset += 1

    return u''

def save_inflection_group_to_db(db_cursor, descriptor_id, descriptor, inflection_group):

    short_form_restrictions = False
    past_part_restrictions = False
    no_short_form =False
    no_past_part = False

    if POS.POS_VERB  == descriptor.part_of_speech:
        past_part_restrictions = inflection_group.x_mark
        no_past_part = inflection_group.boxed_x_mark
    else:
        short_form_restrictions = inflection_group.x_mark
        no_short_form = inflection_group.boxed_x_mark

    params = (descriptor_id,
                True,
                inflection_group.type,
                inflection_group.accent_type_1,
                inflection_group.accent_type_2,
                short_form_restrictions,
                past_part_restrictions,
                no_short_form,
                no_past_part,
                inflection_group.fleeting_vowel,
                inflection_group.stem_augment_type,
                inflection_group.multipart,
                inflection_group.is_second_part,
                False)                          #  is_edited

    db_query = u'INSERT INTO inflection VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
#    db_cursor.execute(db_query, params)
#    ig_id = db_cursor.lastrowid

#    if inflection_group.common_deviations:
#        for cd in inflection_group.common_deviations:
#            params = (ig_id, cd[1], cd[0], False)
#            db_query = u'INSERT INTO common_deviation VALUES (NULL, ?, ?, ?, ?)'
#            db_cursor.execute(db_query, params)

# =================================================================================================

#
#  Headword
#
class Headword:
    def __init__(self):
        self.paragraph = None
        self.source_id = -1
        self.headword_text = ''
        self.stress_dict = {}
        self.homonym_nums = []
        self.lead_comment = ''
        self.trailing_comment = ''
        self.plural_of = ''             # text of the referenced headword
 #       self.plural_of_start_run = -1
        self.variant = ''
        self.variant_stress_dict = {}
        self.variant_homonym_nums = []
        self.variant_comment = ''
        self.see_ref = ''
        self.back_ref = ''
        self.last_row_id = -1
        self.seq_number = -1
        self.is_edited = False
        self.spryazh_sm = False
        return

    def parse_source_data(self, paragraph, offset, is_variant):
        run_idx = run_index_from_offset(paragraph, offset)
        if run_idx < 0:
            return -1

        source = ''
        while not paragraph.runs[run_idx].bold:
            run_idx += 1
            if run_idx >= len(paragraph.runs):
                return -1

        while paragraph.runs[run_idx].bold or len(paragraph.runs[run_idx].text) < 1:
            if paragraph.runs[run_idx].font.name == 'Tim_acc':
                source += u'/'
            elif paragraph.runs[run_idx].font.name == 'Tim_pob':
                source += u'\\'
            
            source += paragraph.runs[run_idx].text.strip()
            run_idx += 1
            if run_idx >= len(paragraph.runs):
                break

            # dash in горно-обогатительный is not bold
            if u'-' == paragraph.runs[run_idx].text:
                source += paragraph.runs[run_idx].text
                run_idx += 1

        while source.startswith(u'\t'):
            source = source[1:]

        #
        #  Extract headword possibly preceded by a list of homonym numbers
        #
        match = re.match(r'^(?:([1-5])?(?:-([1-5]))*)?(\S+)', source)
        if (None == match):
            warning (db_cursor, u'Headword matching failed.', paragraph)
            db_connection.commit()
            return -1

        first_digit = match.group(1)
        last_digit = match.group(2)
        if last_digit != None:
            if first_digit != None:
                current_num = int(first_digit)
                last_num = int(last_digit)
                for num in range(int(first_digit), last_num+1):
                    if is_variant:
                        self.variant_homonym_nums.append(current_num)
                    else:
                        self.homonym_nums.append(current_num)
                    current_num += 1
            else:
                warning (db_cursor, u'Missing 1st homonym number.', paragraph)
        elif first_digit != None:
            if is_variant:
                self.variant_homonym_nums.append(first_digit)
            else:
                self.homonym_nums.append(first_digit)

        if is_variant:
            self.variant = match.group(3)
        else:
            self.headword_text = match.group(3)

        """
        shift = 0
        for at, char in enumerate(self.headword_text):
            found = False
            if u'/' == char:
                found = True
                self.stress_dict[at-shift] = True
            if u'\\' == char:
                found = True
                self.stress_dict[at-shift] = False
            if found:
                new_text = u''
                if at > 0:
                    new_text = self.headword_text[:at-shift]
                new_text += self.headword_text[at+1-shift:]
                self.headword_text = new_text
                shift = shift + 1

        yo_pos = self.headword_text.find(u'ё')
        if yo_pos > -1:
            if yo_pos in self.stress_dict:
                if True == self.headword_text[yo_pos]:
                    warning (db_cursor, u'Warning: main stress + yo.', paragraph)
            else:
                if bool(self.stress_dict):
                    warning (db_cursor, u'Warning: headword with yo has stress mark(s).', paragraph)
                self.stress_dict[yo_pos] = True
        """

        if is_variant:
            self.variant, self.variant_stress_dict = extract_stress_marks(self.variant, paragraph)
        else:
            self.headword_text, self.stress_dict = extract_stress_marks(self.headword_text, paragraph)

        if run_idx >= len(paragraph.runs):      # error??
            return -1

        return run_idx

    #
    #  Extract headword-trailing comments, returns run and absolute position
    #
    def check_headword_trailing_comment(self, paragraph, start_run_idx):
        
        run_idx = start_run_idx

        if run_idx >= len(paragraph.runs):      # error??
            return -1, -1

        offset = paragraph_offset_from_run_offset(paragraph, run_idx, 0)
        if offset < 0 or offset >= len(paragraph.text):
            return -1, -1
        
        offset = offset_to_next_text_segment(paragraph, offset)        
        if offset < 0:
            return run_idx, offset

        if paragraph.text[offset] != u'(':
            return run_idx, offset
        offset += 1

        closing_parenth_pos =  paragraph.text.find(u')', offset+1)
        if closing_parenth_pos < 0:
            warning (db_cursor, u'Unbalanced parenth in headword trailing comment (ignored).', paragraph)
            return run_idx, offset

        self.trailing_comment = paragraph.text[offset:closing_parenth_pos]

        run_idx = run_index_from_offset(paragraph, closing_parenth_pos)

        return run_idx, closing_parenth_pos+1

    #
    # Save headword data if no edited entries exist
    #
    def save_to_db(self, db_cursor):
        try:
        #   We also want to save the raw source text
            hasher = hashlib.md5()
            hasher.update(self.paragraph.text.encode('utf-8'))
            hasher.digest()
            params = (hasher.hexdigest(),
                      self.paragraph.text)
#            db_query = u'INSERT INTO conversion_source_text VALUES (NULL, ?, ?)'
#            db_cursor.execute(db_query, params)
#            self.source_entry_id = db_cursor.lastrowid

            params = (self.headword_text,
                      self.plural_of,
                      self.lead_comment,
                      self.trailing_comment,
                      self.variant,
                      self.variant_comment,
                      self.see_ref,
                      self.back_ref,
                      self.source_entry_id,
                      self.spryazh_sm,
                      False)            # is_edited
            db_query = u'INSERT INTO headword VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
#            db_cursor.execute(db_query, params)
#            self.last_row_id = db_cursor.lastrowid

        except sqlite3.Error as sqlite_ex:
            print ('sqlite3 error: ', sqlite_ex.args[0])
            return False
        except Exception as e:
            print ('Exception: %s, %s' % (sys.exc_info()[0], e))
        return True
    
    def save_stress_pos(self, db_cursor, position, is_primary, is_variant):
        if self.last_row_id < 0:
            warning(db_cursor, u'No headword DB key.', self.paragraph)
            return False
        try:
            params = (self.last_row_id,
                      position,
                      is_primary,
                      is_variant,
                      False)                #  is_edited
#            db_query = u'INSERT INTO stress VALUES (NULL, ?, ?, ?, ?, ?)'
#            db_cursor.execute(db_query, params)
        except IOError as io_ex:
            print ('IO Error.', io_ex.args[0])
            return False
 #       except sqlite3.Error as sqlite_ex:
 #           print ('sqlite3 error: ', sqlite_ex.args[0])
 #           self.last_row_id = db_cursor.lastrowid
 #           return False

        return True        

    def save_homonyms(self, db_cursor):
        if self.last_row_id < 0:
            warning(db_cursor, u'No headword DB key.', self.paragraph)
            return False
        try:
            for num in self.homonym_nums:
                params = (self.last_row_id,
                          num,
                          False,        #  is_variant
                          False)        #  is_edited
                db_query = u'INSERT INTO homonyms VALUES (NULL, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)

            for num in self.variant_homonym_nums:
                params = (self.last_row_id,
                          num,
                          True,         #  is_variant
                          False)        #  is_edited      
                db_query = u'INSERT INTO homonyms VALUES (NULL, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)

        except IOError as io_ex:
            print ('IO Error.', io_ex.args[0])
            return False
        except sqlite3.Error as sqlite_ex:
            print ('sqlite3 error: ', sqlite_ex.args[0])
            self.last_row_id = db_cursor.lastrowid
            return False

        return True


# end of class Headword

#
#  Inflection group
#
class InflectionGroup:
    def __init__(self, descriptor):
        self.has_data = False
        self.multipart = 0  # 0: the last part is inflected (usual)
                            # 1: first part is inflected (какой-то)
                            # 2: both parts are inflected (конёк-горбунок)
        self.is_second_part = False     # after dash part in "+" compounds, e.g., xurda-murda
        self.type = -1
        self.accent_type_1 = 0
        self.accent_type_2 = 0
        self.x_mark = False
        self.boxed_x_mark = False
        self.fleeting_vowel = False
        self.stem_augment_type = -1
        self.comment = ''
        self.common_deviations = []     # list of pairs: { bool, numeric }
        self.descriptor = descriptor

        return

    #
    #  Parse source data
    #
    def parse_inflection_group(self, paragraph, source_text, paragraph_offset):

        self.has_data = False

        if self.descriptor.part_of_speech in uninflected_pos:
            return paragraph_offset

        match = re.match(r'^\s*?([абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.]+)?\s*?(\d{1,2}).*', source_text[paragraph_offset:])
        if None == match:
            if not headword in spryazh_sm:
                warning(db_cursor, u'Unable to find inflection group.', paragraph)
            return paragraph_offset

        if match.group(1) != None:
            try:
                self.comment = match.group(1)
            except:
                warning(db_cursor, u'Unable to parse inflection group comment.', paragraph)

        if match.group(2) != None:
            try:
                self.type = int(match.group(2))
                paragraph_offset = paragraph_offset + match.end(2)
            except:
                warning(db_cursor, u'Unable to parse inflection number.', paragraph)

        self.has_data = True

        if paragraph_offset >= len(source_text):
            return paragraph_offset

        #
        #  Stem augment
        #
        if u'\uF031' == source_text[paragraph_offset]:   # кружочек

            paragraph_offset = paragraph_offset + 1

            if POS.POS_NOUN == self.descriptor.part_of_speech:
                if 1 == self.type:
                    self.stem_augment_type = 1
                if 3 == self.type:
                    if headword.headword_text.endswith(u'онок') or headword.headword_text.endswith(u'ёнок'):
                        self.stem_augment_type = 1
                    elif headword.headword_text.endswith(u'оночек') or headword.headword_text.endswith(u'ёночек'):
                        self.stem_augment_type = 2
                    else:
                        warning(db_cursor, u'Unexpected source for a 3° noun.', paragraph)
                if 8 == self.type:
                    if headword.headword_text.endswith(u'мя'):
                        self.stem_augment_type = 3
                    else:
                        warning(db_cursor, u'Unexpected source for a 8° noun.', paragraph)

            elif POS.POS_VERB == self.descriptor.part_of_speech:
                self.stem_augment_type = 1

        if paragraph_offset >= len(source_text):
            return paragraph_offset

        #
        #  Fleeting vowel
        #
        if u'*' == paragraph.text[paragraph_offset]:
            self.fleeting_vowel = True
            paragraph_offset = paragraph_offset + 1

        if paragraph_offset >= len(source_text):
            return paragraph_offset

        #
        #  Accent type
        #
        ap1 = None
        ap2 = None
        match = re.match(r'^([abcdef]\'{0,2}).*', source_text[paragraph_offset:])
        if match != None:
            if match.group(1) != None:
                ap1 = match.group(1)

                if ap1 in accent_types:
                    self.accent_type_1 = at_to_enum[accent_types[ap1]]
                else:
                    warning (db_cursor, u'Unknown accent type.', paragraph)

                paragraph_offset = paragraph_offset + match.end(1)                
                if paragraph_offset >= len(source_text):
                    return paragraph_offset

                match = re.match(u'^/([abcdef]\'{0,2}).*', source_text[paragraph_offset:])
                if match != None:
                    if match.group(1) != None:
                        ap2 = match.group(1)

                        if ap2 in accent_types:
                            self.accent_type_2 = at_to_enum[accent_types[ap2]]
                        else:
                            warning (db_cursor, u'Unknown 2nd accent type.', paragraph)

                        paragraph_offset = paragraph_offset + match.end(1)
                        if paragraph_offset >= len(source_text):
                            return paragraph_offset

        #
        #  X-mark and boxed x-mark
        #
        if u'\uF025' == source_text[paragraph_offset]:
            self.x_mark = True
            paragraph_offset += 1
            if paragraph_offset >= len(source_text):
                return paragraph_offset
        if u'\uF08D' == source_text[paragraph_offset]:
            self.boxed_x_mark = True
            paragraph_offset += 1
            if paragraph_offset >= len(source_text):
                return paragraph_offset

        paragraph_offset = check_circled_digit(paragraph, source_text, paragraph_offset, self)

        if paragraph_offset < len(paragraph.text) and '>' == paragraph.text[paragraph_offset]:
            paragraph_offset += 1

        return paragraph_offset     #  parse_inflection_group

#  class InflectionGroup

#
#  Descriptor
#
class Descriptor:
    def __init__(self, paragraph):
        self.paragraph = paragraph
        self.paragraph_index = -1
        self.variant = False            # currently unused ?
        self.main_symbol = u''
        self.inflection_symbol = u''     # usually same as above, but cf. б<абий п <мс 6*а>
        self.alt_inflection_symbol = u'' # does it exist?
        self.is_plural_of = False
        self.intransitive = False
        self.is_reflexive = False
        self.inflection_symbol_as_enum = -1
        self.main_symbol_plural_of = u''
        self.alt_main_symbol = u''
        self.part_of_speech = POS.POS_UNDEFINED
        self.comment = u''
        self.cognate = u''           #  (_от_ ...); (_женск. к_ ...)
        self.cognate_relation = u''
        self.alt_main_symbol_comment = u''
        self.alt_inflection_comment = u''
        self.graphic_stem = u''
        self.graphic_stem2 = u''
        self.inflection_group = None
        self.alt_inflection_group = None
        self.second_inflection_group = None     # хурда-мурда, купля-продажа
        self.verb_alternation = u''
        self.past_part_pass_zhd = False
        self.section = -1
        self.no_comparative = False
        self.no_long_forms = False
        self.no_imperative = False
        self.no_adverbial = False
        self.no_part_pres_act = False
        self.no_part_pres_pass = False
        self.no_part_past_act = False
        self.adverbial_difficult = False
        self.assumed_forms = False
        self.yo = False
        self.o = False
        self.gen2 = False
        self.loc2 = False
        self.loc2_optional = False
        self.has_irregular_forms = False
        self.has_difficult_forms = False
        self.has_missing_forms = False               # TODO: currently not assigned
        self.difficult_forms = []   # stored as text without further parsing
        self.missing_forms = []     # stored as text without further parsing
        self.iterative = False          #  многокр.
        self.impersonal = False         #  безл.
        self.loc2_preposition = u''
        self.non_existent_forms = u''
        self.obsolete_forms = u''
        self.colloquial_forms = u''      #  ехай
        self.irregular_forms = []        #  triangle, list of pairs "parameter, value"
        self.alt_irregular_forms = []    #  triangle, optional irregular forms
        self.irregular_forms_lead_comment = u'' 
        self.restricted_contexts = u''      #  diamond
        self.contexts = u''
        self.has_aspect_pair = False
        self.aspect_pair_type = 0        # Roman num --> negative
        self.aspect_pair_data = u''
        self.aspect_pair_is_variant = False
        self.aspect_pair_comment = u''      # We currently assume that is not used in Zal
        self.aspect_alt_pair_type = 0        # Roman num --> negative
        self.aspect_alt_pair_data = u''
        self.aspect_alt_pair_is_variant = False
        self.aspect_alt_pair_comment = u''
#        self.aspect_pair_type = []      #  list of numbers after hatched circle, negative if Roman, 0 if no number
#        self.aspect_pair_comment = []   #  optional comment after aspect pair
#        self.aspect_pairs = []           #  list of tuples: number/comment (if available)
#        self.sharp = -1                 #  number after #, redundant, see "section"
        self.trailing_comment = ''
        self.semicolon_offset = -1
        self.is_secondary = False        #  after semicolon:   выходной	п	1b; м (выходной день)
        self.descriptor_id = -1

        return

    def copy(self):
        copy = Descriptor(self.paragraph)

        copy.paragraph = self.paragraph
        copy.paragraph_index = self.paragraph_index
        copy.variant = self.variant
        copy.main_symbol = self.main_symbol
        copy.inflection_symbol = self.inflection_symbol
        copy.alt_inflection_symbol = self.alt_inflection_symbol
        copy.is_plural_of = self.is_plural_of
        copy.intransitive = self.intransitive
        copy.is_reflexive = self.is_reflexive
        copy.inflection_symbol_as_enum = self.inflection_symbol_as_enum
        copy.main_symbol_plural_of = self.main_symbol_plural_of
        copy.alt_main_symbol = self.alt_main_symbol
        copy.part_of_speech = self.part_of_speech
        copy.comment = self.comment
        copy.cognate = self.cognate
        copy.cognate_relation = self.cognate_relation
        copy.alt_main_symbol_comment = self.alt_main_symbol_comment
        copy.alt_inflection_comment = self.alt_inflection_comment
        copy.graphic_stem = self.graphic_stem
        copy.graphic_stem2 = self.graphic_stem2
        copy.inflection_group = self.inflection_group
        copy.alt_inflection_group = self.alt_inflection_group
        copy.second_inflection_group = self.second_inflection_group
        copy.verb_alternation = self.verb_alternation
        copy.past_part_pass_zhd = self.past_part_pass_zhd
        copy.section = self.section
        copy.no_comparative = self.no_comparative
        copy.no_long_forms = self.no_long_forms
        copy.no_imperative = self.no_imperative
        copy.no_adverbial = self.no_adverbial
        copy.no_part_pres_act = self.no_part_pres_act
        copy.no_part_pres_pass = self.no_part_pres_pass
        copy.no_part_past_act = self.no_part_past_act
        copy.adverbial_difficult = self.adverbial_difficult
        copy.assumed_forms = self.assumed_forms
        copy.yo = self.yo 
        copy.o = self.o
        copy.gen2 = self.gen2
        copy.loc2 = self.loc2
        copy.loc2_optional = self.loc2_optional
        copy.has_irregular_forms = self.has_irregular_forms
        copy.has_difficult_forms = self.has_difficult_forms
        copy.has_missing_forms = self.has_missing_forms
        copy.difficult_forms = self.difficult_forms
        copy.missing_forms = self.missing_forms
        copy.iterative = self.iterative
        copy.impersonal = self.impersonal
        copy.loc2_preposition = self.loc2_preposition
        copy.non_existent_forms = self.non_existent_forms
        copy.difficult_forms = self.difficult_forms
        copy.obsolete_forms = self.obsolete_forms
        copy.colloquial_forms = self.colloquial_forms
        copy.irregular_forms = self.irregular_forms.copy()
        copy.alt_irregular_forms = self.alt_irregular_forms
        copy.restricted_contexts = self.restricted_contexts
        copy.contexts = self.contexts
        copy.has_aspect_pair = self.has_aspect_pair
        copy.has_aspect_pair = False
        copy.aspect_pair_type = 0        # Roman num --> negative
        copy.aspect_pair_data = u''
        copy.aspect_pair_is_variant = False
        copy.aspect_pair_comment = u''
        copy.has_aspect_alt_pair = False
        copy.aspect_alt_pair_type = 0        # Roman num --> negative
        copy.aspect_alt_pair_data = u''
        copy.aspect_alt_pair_is_variant = False
        copy.aspect_alt_pair_comment = u''
#        self.sharp = -1                 #  number after #, redundant, see "section"

        copy.trailing_comment = self.trailing_comment
        copy.semicolon_offset = self.semicolon_offset
        copy.is_secondary = self.is_secondary

        return copy

    def parse_descriptor(self, headword, paragraph, source_offset, inflection_type_mismatch, is_variant):

#        run_idx = start_run_idx
#        if paragraph.runs[run_idx].bold or paragraph.runs[run_idx].italic:                                                         
#            return -1                  # error
#        run_idx = run_index_from_offset(paragraph, source_offset)
#        source = ''
#        source_offset = paragraph_offset_from_run_offset(paragraph, run_idx, 0)
#        while not paragraph.runs[run_idx].bold and not paragraph.runs[run_idx].italic:
#            source += paragraph.runs[run_idx].text
#            run_idx += 1
#            if run_idx >= len(paragraph.runs):
#                break

#        after_semicolon = False
#        if semicolon:
#            after_semicolon = True

        semicolon = False

#        if None == source or '' == source:
#            warning (db_cursor, u'Empty source.', paragraph)
#            return semicolon, source_offset

#        if len(source) < 1:
#            warning (db_cursor, u'Source has negative length.', paragraph)
#            return semicolon, source_offset

        start_offset = offset_to_next_text_segment(paragraph, source_offset)
        if start_offset < 0 or start_offset >= len(paragraph.text):
            warning (db_cursor, u'Main symbol not found.', paragraph)
            return semicolon, -1

        source = paragraph.text
        semicolon, current_offset = self.extract_main_symbol(paragraph, source, start_offset, False)
        if self.semicolon_offset > -1:
            source = source[:self.semicolon_offset]


#        try:
#            if main_symbols[self.inflection_symbol] in (POS.POS_PRONOUN, POS.POS_PRONOUN_ADJ, POS.POS_NUM):
#                out_doc.add_paragraph(paragraph.text)
#        except:
#            print 'skip'

#        while semicolon and current_offset < len(paragraph.text):
            # TODO: write the record
#            semicolon, expect_alt_inflection_group, current_offset = self.extract_main_symbol(paragraph, current_offset, False)

        if current_offset >= len(paragraph.text):
            dictionary[headword].append(self)
            return semicolon, -1

        s, current_offset = self.check_angle_brackets(paragraph, source, current_offset)
        if s:
            source = source[:self.semicolon_offset]
            semicolon = True

# TODO: if semicolon -- return?

        if source.endswith(u','):
            expect_alt_inflection_group = True
            source = source[:-1]
        else:
            expect_alt_inflection_group = False

        """
        if self.has_alt_main_symbol:
            start_offset = offset_to_next_text_segment(paragraph, current_offset+1)
            if start_offset < 0 or start_offset >= len(source):
                return semicolon, -1

            self.alt_main_symbol = get_next_segment(paragraph, start_offset)

            if self.alt_main_symbol not in main_symbols.keys():
                warning (db_cursor, u'Unknown alt. main symbol.', paragraph)
            """

        if paragraph.text[current_offset:].startswith(u'спряж. см. '):
            current_offset += 11
            length = paragraph.text[current_offset:].find(u' ')
            offset_to_next = current_offset
            if length < 0:
                length = len(paragraph.text[current_offset:])
                offset_to_next += length
            else:
                offset_to_next += length+1

            while paragraph.text[current_offset:][length-1] in u',.;/':
                length = length-1
            spryazh_sm[headword] = paragraph.text[current_offset:current_offset+length]

            current_offset = offset_to_next
        else:
            if not is_variant:
                dictionary[headword].append(self)

        if current_offset < 1:
            return semicolon, current_offset
        
        ig = InflectionGroup(self)
        current_offset = ig.parse_inflection_group(paragraph, source, current_offset)
        self.post_inflection_group_offset = current_offset
        if ig != None and ig.has_data:
            self.inflection_group = ig

        section_match = re.match(r'(.*?\, § (\d+))', source[current_offset:])
        if (None != section_match):
            section_num = int(section_match.group(2))
            if not section_num in [7, 8, 9, 10, 11, 12, 13, 14, 15]:
                warning(db_cursor, u'Unexpected section number: must be between 7 and 10.', paragraph)
            else:
                self.section = section_num

            current_offset += len(section_match.group(0))

        if source[current_offset:current_offset+2] == u'//':
            current_offset += 2
            alt_ig = InflectionGroup(self)
            current_offset = alt_ig.parse_inflection_group(paragraph, source, current_offset)
            if alt_ig != None:
                self.alt_inflection_group = alt_ig
    
        if current_offset < 0 or current_offset >= len(source):
            return semicolon, current_offset

        if u'\uF07E' == paragraph.text[current_offset]:   # tilde
            self.no_comparative = True
#               good place to check for §11 (слабенький):
            section_match = re.match(r'(.*?\, § (\d+))', source[current_offset:])
            if (None != section_match):
                section_num = int(section_match.group(2))
                if section_num != 11:
                    warning(db_cursor, u'Unexpected section number: must be 11.', paragraph)
                else:
                    self.section = section_num
                    current_offset += len(section_match.group(0))
            else:
                current_offset = current_offset + 1

            if current_offset >= len(source):
                return semicolon, current_offset

        if u'\u2014' == paragraph.text[current_offset]:   # m-dash a.k.a. minus
            self.assumed_forms = True
            current_offset = current_offset + 1
            if current_offset >= len(source):
                return semicolon, current_offset

        current_offset = check_plus_sign(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset, expect_continuation = check_verb_stem_alternations (paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        # Here we have to repeat common deviations check since sometimes
        # a circled digit may appear after stem alternation         
        current_offset = check_circled_digit(paragraph, source, current_offset, ig)

        if current_offset < 0 or current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_yo_and_o(paragraph, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_loc2_and_gen2(paragraph, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_see_ref(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_impersonals_and_iteratives (paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_cognates(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_colon(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        current_offset = check_restricted(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        #
        #  Another check for X-mark and boxed x-mark (don't want to remove
        #  the old one out of caution
        #
        if not ig.x_mark and 0 <= source.find(u'\uF025', start_offset):
            ig.x_mark = True
            warning(db_cursor, "'x' tag, unusual position", paragraph)

        if not ig.boxed_x_mark and 0 <=  source.find(u'\uF08D', start_offset):
            ig.boxed_x_mark = True
            warning(db_cursor, "Boxed 'x' tag, unusual position", paragraph)

        #
        #  Same for ё and о
        #
        if not self.yo and 0 <= source.find(u', ё', start_offset):
            warning(db_cursor, "Yo tag, unusual position", paragraph)
            self.yo = True
        if not self.o and 0 <=  source.find(u', о', start_offset):
            warning(db_cursor, "O tag, unusual position", paragraph)
            offset = source.find(u', о', start_offset)
            if offset == len(source) - 1 or \
             (offset < len(source) - 2 and ' ' == source[offset + 1] and u'р' == source[offset + 2]):
                self.o = True

        check_aspect_symbol(paragraph, current_offset, self)    # current offset ignored

        self.irregular_forms = IrregularForms(self)
        self.has_irregular_forms = False
        current_offset, self.has_irregular_forms = self.irregular_forms.check_triangle(paragraph, current_offset, self)
        if self.has_irregular_forms:
            semicolon = self.irregular_forms.parse(u'')
        if self.irregular_forms.left_bracket_offset >= 0:
            alt_forms_offset = self.irregular_forms.left_bracket_offset
            alt_forms_offset += len(paragraph.text[self.irregular_forms.left_bracket_offset:]) - len(paragraph.text[self.irregular_forms.left_bracket_offset:].lstrip())
            alt_forms_offset += 1
            if paragraph.text[alt_forms_offset:].startswith(u'//'):
                self.irregular_forms.paragraph_offset = alt_forms_offset + 2
                self.irregular_forms.offset_to_end = self.irregular_forms.paragraph_offset + paragraph.text[self.irregular_forms.paragraph_offset:].find(u']') - 1
                self.irregular_forms.has_alt_forms = True
                self.irregular_forms.parse(u'alt_form_parse')

        current_offset = check_difficult_and_missing_forms(paragraph, source, current_offset, self)
        if current_offset >= len(source):
            return semicolon, current_offset

        if 0 >= self.irregular_forms.left_bracket_offset:   # ignore left brackets after triangle
            current_offset = check_square_brackets(paragraph, current_offset, self)
            if current_offset >= len(source):
                return semicolon, current_offset

        if paragraph.text[current_offset] == u';':
            current_offset += 1
            semicolon = True

        return semicolon, current_offset       # parse_descriptor()

    #
    #  Assemble and identify main symbol
    #
    def extract_main_symbol(self, paragraph, source_text, start_offset, inflection_type_mismatch):

        current_offset = start_offset
        semicolon = False
        extracted_symbol = ''
        extracted_alt_symbol = ''

        if start_offset >= len(source_text):
            warning (db_cursor, u'No text at current offset.', paragraph)
            return False, False, -1

        m_source = re.match(r'[абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-]+([\t ;:])[абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-]*', source_text[start_offset:])
        if None == m_source:
            source = source_text[start_offset:]
            chars_to_extract = len(source_text) + 1
            offset_to_next = chars_to_extract
        else:
            chars_to_extract = start_offset + m_source.end(1)
            offset_to_next = chars_to_extract

            separator = m_source.group(1)
            if u';' == separator:
                self.semicolon_offset = start_offset + m_source.start(1)
                semicolon = True
            else: 
                semicolon = False

            if u':' == separator: 
                colon = True
            else:
                colon = False

            if u' ' == separator or u'\t' == separator:
                for tag in [u'мн. от', u'мн. неод.', u'мн. одуш.', u'мн.']:
                    if source_text[start_offset:].startswith(tag):
                        chars_to_extract = offset_to_next = start_offset + len(tag) + 1
                        break
                if (source_text[start_offset:].startswith(u'св') or
                   source_text[start_offset:].startswith(u'нсв') or
                   source_text[start_offset:].startswith(u'св-нсв')):
                        continuation_offset = offset_to_next_text_segment(paragraph, offset_to_next)
                        if continuation_offset < len(source_text):
                            if source_text[continuation_offset:].startswith(u'нп'):
                                self.intransitive = True
                                offset_to_next += 3

        extracted = source_text[start_offset:chars_to_extract-1]

        self.has_alt_main_symbol = False

        m_next = re.match(r'[абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-]+([/,;])[абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-]*',
                          source_text[start_offset:offset_to_next])
        if m_next != None:
            offset_to_next = start_offset + m_next.end(1)
            next = source_text[start_offset:offset_to_next]
            source = source_text[offset_to_next:]
            
            extracted = source_text[start_offset:offset_to_next-1]
            
            separator = m_next.group(1)

            if u'/' == separator:
                if source.startswith(u'/ '):    # ж// жо, 1st forward slash already counted
                    alt_offset = offset_to_next + 2
                    m_alt = re.match(r'[абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-]+([,;])([^абвгдеёжзийклмнопрстуфхцчшщъыьэюя\.\-])',
                                     source_text[alt_offset:])
                    if None == m_alt:
                        extracted_alt_symbol = source_text[alt_offset:]
                        offset_to_next = len(source_text)
                    else:
                        extracted_alt_symbol = source_text[alt_offset:alt_offset+m_alt.start(1)]
                        offset_to_next = alt_offset + m_alt.start(1)

                self.has_alt_main_symbol = True

            if len(source_text[offset_to_next:]) > 0:
                next_char = source_text[offset_to_next:offset_to_next+1]
                if u',' == next_char:
                    expect_alt_inflection_group = True
                    offset_to_next += 1

        extracted = extracted.replace(u'\t', u' ')
        extracted = extracted.strip(''.join(tuple(white_space_characters)))

#        extracted_alt_symbol = extracted
        if len(extracted) >= 3 and u'§' == extracted[0]:
            if u'§ 1' == extracted[0:3]:
                self.section = 1
                offset_to_next = start_offset + 3
            elif u'§ 2' == extracted[0:3]:
                self.section = 2
                offset_to_next = start_offset + 3
            else:
                warning(db_cursor, u'Unexpected section number.', paragraph)
            return semicolon, offset_to_next
        else:
            self.inflection_symbol = extracted
            self.alt_inflection_symbol = extracted_alt_symbol

        if not inflection_type_mismatch:
            self.main_symbol = extracted
            self.alt_main_symbol = extracted_alt_symbol

        if u'' == extracted:
            warning (db_cursor, u'Unable to extract main symbol.', paragraph)
        else:
            if not (extracted in main_symbols.keys()):
                warning (db_cursor, u'Unable to extract main symbol.', paragraph)
                return False, -1
            else:
                if extracted in main_symbols.keys():
                    if not inflection_type_mismatch:
                        self.part_of_speech = main_symbols[extracted]
                else:
                    warning (db_cursor, u'Unidentified main symbol.', paragraph)
                    return False, -1

        return semicolon, offset_to_next

    #  extract_main_symbol

    #
    #  Extract inflection type if different from main symbol, e.g., б'абий п <мс 6*а>
    #
    def check_angle_brackets(self, paragraph, source_text, start_offset):
        
        start_offset = offset_to_next_text_segment(paragraph, start_offset)
        if start_offset < 0 or start_offset >= len(paragraph.text):
            return False, start_offset

        match = re.match(u'(<(.+?)>).*', source_text[start_offset:])
        if None == match:
            return False, start_offset

        alt_main_symb_offset = start_offset + match.start(2)

        semicolon, offset_to_next = self.extract_main_symbol(paragraph, source_text, alt_main_symb_offset, True)

        section_match = re.match(r'(<(.+?)>)\, § (\d+)', source_text[start_offset:])
        if (None != section_match):
            section_num = int(section_match.group(3))
            if not section_num in [3, 4, 5, 6, 11, 12]:
                warning(db_cursor, u'Unexpected section number: must be between 3 and 6.', paragraph)
            else:
                self.section = section_num
#                offset_to_next = start_offset + len(section_match.group(0))

        return semicolon, offset_to_next

    def make_graphic_stem(self, headword_source, second_part = False):
                                                    #           ^--- (xurda)-murda
        if len(headword_source) < 1:
            warning (db_cursor, u'Illegal source form.', paragraphs[self.paragraph_index])
            db_connection.commit()
            return u''

#        if second_part and not self.second_inflection_group:
#            warning(db_cursor, u'Missing 2nd inflection group in a compound.', paragraphs[self.paragraph_index])
#            return
#                            ^--- should be allowed for uninflected?

        graphic_stem = u''
        inflection_group = None
        if second_part:
            inflection_group = self.second_inflection_group
        else:
            inflection_group = self.inflection_group

        if None != inflection_group:
#            if self.main_symbol in (u'м', u'мо', u'ж', u'жо', u'мо-жо', u'с', u'со', u'мс-п'):
            if self.inflection_symbol in (u'м', u'мо', u'ж', u'жо', u'мо-жо', u'с', u'со', u'мс-п', u'мс'):
                if 0 == inflection_group.type:
                    graphic_stem = headword_source
                    return graphic_stem

                if headword_source[-1] in (u'а', u'е', u'ё', u'и', u'о', u'у', u'ы', u'э', u'ю', u'я', u'й', u'ь'):
                    if len(headword_source) < 1:
                        warning (db_cursor, u'Illegal source form.', paragraphs[self.paragraph_index])
                        db_connection.commit()
                        return u''

                    graphic_stem = headword_source[:-1]
                else:
                    graphic_stem = headword_source

                return graphic_stem
        
        if u'мс' == self.main_symbol:
        # In this case, all forms should be considered irregular
            graphic_stem = headword_source
            return  graphic_stem

#        if self.main_symbol in (u'мн.', u'мн. неод.', u'мн. одуш.', u'мн. от'):
        if self.inflection_symbol in (u'мн.', u'мн. неод.', u'мн. одуш.', u'мн. от'):
            graphic_stem = headword_source[:-1]
            return graphic_stem

#        if u'п' == self.alt_inflection_symbol:
        if u'п' == self.inflection_symbol:
            if None == inflection_group or 0 == inflection_group.type:
                graphic_stem = headword_source
                return graphic_stem

            if self.no_long_forms:
                graphic_stem = headword_source
                return graphic_stem

            chars_to_remove = 0
            if headword_source.endswith(u'ся'):
                chars_to_remove = 4
            else:           
                chars_to_remove = 2

            if len(headword_source) < chars_to_remove:
                warning (db_cursor, u'Source form too short.', paragraphs[self.paragraph_index])
                db_connection.commit()                
                return u''

            graphic_stem = headword_source[:-chars_to_remove]
            return graphic_stem
        
        if self.main_symbol in (u'св', u'нсв', u'св-нсв'):
            if headword_source.endswith(u'ти') or headword_source.endswith(u'ть') or headword_source.endswith (u'чь'):
                graphic_stem = headword_source[:-2]
            elif headword_source.endswith(u'тись') or headword_source.endswith(u'ться') or headword_source.endswith (u'чься'):
                graphic_stem = headword_source[:-4]
                self.is_reflexive = True
            else:
                warning (db_cursor, u'Warning: verb not recognized.', paragraphs[self.paragraph_index])
                db_connection.commit()
                # Assume verbal wordforms with no infinitive form, like "поезжай"
                graphic_stem = headword_source
            
            return graphic_stem

        graphic_stem = headword_source
        # warning (db_cursor, u'Unable to create graphic stem.', paragraphs[self.paragraph_index])
        # db_connection.commit()
        # Assume verbal wordforms with no infinitive form, like "поезжай"
        return graphic_stem

    # make_graphic_stem()

    def save_to_db(self, db_cursor, headword_id):

        difficult_forms = u''
        missing_forms = u''

        try:
            params = (headword_id,                      # 1
                      self.graphic_stem,                # 2
                      self.graphic_stem2,               # 3
                      self.variant,                     # 4
                      self.main_symbol,                 # 5
                      pos_to_enum[self.part_of_speech], # 6
                      self.is_plural_of,                # 7
                      self.intransitive,                # 8
                      self.is_reflexive,                # 9
                      self.main_symbol_plural_of,       # 10
                      self.alt_main_symbol,             # 11
                      self.inflection_symbol,           # 12
                      self.comment,                     # 13
                      self.alt_main_symbol_comment,     # 14
                      self.alt_inflection_comment,      # 15
                      self.verb_alternation,            # 16
                      self.past_part_pass_zhd,          # 17
                      self.section,                     # 18
                      self.no_comparative,              # 19
                      self.no_long_forms,               # 20
                      self.assumed_forms,               # 21
                      self.yo,                          # 22
                      self.o,                           # 23
                      self.gen2,                        # 24
                      self.impersonal,                  # 25
                      self.iterative,                   # 26
                      self.has_aspect_pair,             # 27
                      self.has_difficult_forms,         # 28
                      self.has_missing_forms,           # 29
                      self.has_irregular_forms,         # 30
                      self.irregular_forms_lead_comment,# 31
                      self.restricted_contexts,         # 32
                      self.contexts,                    # 33
                      self.cognate,                     # 34
                      self.trailing_comment,            # 35
                      False)                            # 36  is_edited

            db_query = u'INSERT INTO descriptor VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
#                                                             1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36
#            db_cursor.execute(db_query, params)

            descriptor_id = db_cursor.lastrowid

            if self.loc2:
                params = (descriptor_id,
                          self.loc2_optional,
                          self.loc2_preposition,
                          False)

                db_query = u'INSERT INTO second_locative VALUES (NULL, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)

            if self.gen2:
                params = (descriptor_id, False)

                db_query = u'INSERT INTO second_genitive VALUES (NULL, ?, ?)'
#                db_cursor.execute(db_query, params)

            if self.has_aspect_pair:
                params = (descriptor_id, self.aspect_pair_type, self.aspect_pair_data, False, self.aspect_pair_comment, False)
                db_query = u'INSERT INTO aspect_pair VALUES (NULL, ?, ?, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)

                if self.aspect_alt_pair_type != 0:
                    params = (descriptor_id, self.aspect_alt_pair_type, self.aspect_alt_pair_data, True, self.aspect_alt_pair_comment, False)
#                    db_cursor.execute(db_query, params)

            if self.has_difficult_forms:
                for item in self.difficult_forms:
                    params = (descriptor_id, item)
                    db_query = u'INSERT INTO difficult_forms VALUES (NULL, ?, ?)'
#                    db_cursor.execute(db_query, params)

            if self.has_missing_forms:
                for item in self.missing_forms:
                    params = (descriptor_id, item)
                    db_query = u'INSERT INTO missing_forms VALUES (NULL, ?, ?)'
#                    db_cursor.execute(db_query, params)

#            if self.has_irregular_forms:
#                self.irregular_forms.save_to_db(db_cursor, descriptor_id)
            
#            if self.inflection_group != None and self.inflection_group.has_data:
#                save_inflection_group_to_db(db_cursor, descriptor_id, self, self.inflection_group)

#            if self.alt_inflection_group != None and self.alt_inflection_group.has_data:
#                save_inflection_group_to_db(db_cursor, descriptor_id, self, self.alt_inflection_group)

#            if self.second_inflection_group != None:
#                save_inflection_group_to_db(db_cursor, descriptor_id, self, self.second_inflection_group)

            self.descriptor_id = descriptor_id

        except IOError as io_ex:
            print ('IO Error.', io_ex.args[0])
        except sqlite3.Error as sqlite_ex:
            print ('sqlite3 error: ', sqlite_ex.args[0])
            self.last_row_id = db_cursor.lastrowid
        except Exception as e:
            print ('Exception: %s, %s' % (sys.exc_info()[0], e))


# class Descriptor

class IrregularForm:
   
    def __init__(self):
        self.form = None
        self.stress_dict = {}
        self.lead_comment = None
        self.trailing_comment = None

    def copy(self):
        copy = IrregularForm()

        copy.form = self.form
        copy.stress_dict = self.stress_dict
        copy.lead_comment = self.lead_comment
        copy.trailing_comment = self.trailing_comment

        return copy

class IrregularStress:
    def __init__(self):
        self.form = None
        self.stress_dict = {}

    def copy(self):
        copy = IrregularStress(self)

        copy.form = self.copy
        copy.stress_dict = self.stress_dict

        return copy

class IrregularForms:
    
    def __init__(self, descriptor):
        self.descriptor = descriptor
        self.paragraph_offset = -1
        self.length = -1
        self.source = None
        self.forms = {}             # gramm feature set --> form
        self.alt_forms = {}
        self.lead_comment = None
        self.trailing_comment = None;
        self.initial_form = None
        self.stem = None
        self.has_alt_forms = False
        self.noun_paradigm = False
        self.semicolon = False

    def copy(self):
        copy = IrregularForms(self.descriptor)

        copy.paragraph_offset = self.paragraph_offset
        copy.length = self.length
        copy.source = self.source
        for key, form in self.forms.viewitems():
            copy.forms[key] = form
        for key, alt_form in self.alt_forms.viewitems():
           copy.alt_forms[key] = alt_form
        copy.lead_comment = self.lead_comment
        copy.trailing_comment = self.trailing_comment
        copy.initial_form = self.initial_form
        copy.stem = self.stem
        copy.has_alt_forms = self.has_alt_forms
        copy.noun_paradigm = self.noun_paradigm
        copy.semicolon = self.semicolon

        return copy

    def assign(self, key, form):
        if not self.has_alt_forms:
            self.forms[key] = form
        else:
            self.alt_forms[key] = form

    def assign_form(self, key, form_text):
        if not self.has_alt_forms:
            self.forms[key].form = form_text
        else:
            self.alt_forms[key].form = form_text

    def get(self, key):
        if not self.has_alt_forms:
            return self.forms[key]
        else:
            return self.alt_forms[key]

    def get_keys(self):
        if not self.has_alt_forms:
            return self.forms.keys()
        else:
            return self.alt_forms.keys()

    #
    # §      = section mark
    # \uF057 = triangle
    # $ = aspect pair mark
    # \uF047 = restricted forms mark
    #
    def check_triangle(self, paragraph, paragraph_offset, descriptor):

        self.left_bracket_offset = -1
        end_offset = paragraph_offset
        self.source = ''
        self.paragraph = paragraph
        self.offset_to_end = -1

        if not u'\uF057' in paragraph.text[paragraph_offset:]:
            return end_offset, False

        triangle_offset = paragraph.text.find(u'\uF057', paragraph_offset)
#        if triangle_offset < paragraph_offset:
#            warning (db_cursor, u'Wrong triangle offset.', paragraph)

        self.paragraph_offset = triangle_offset + 1

        start_pos = self.paragraph_offset
        semicolon_offset = paragraph.text.find(u';', start_pos)
        while semicolon_offset >= 0:
            close_parenth_offset = p.text.find(u')', semicolon_offset + 1) # closest ")" to the right of ";"
            open_parenth_offset = p.text.rfind(u'(', 0, semicolon_offset)  # closest "(" to the left of ";"
            if close_parenth_offset >= 0 and open_parenth_offset >= 0:
                if open_parenth_offset < close_parenth_offset:
                    start_pos = close_parenth_offset + 1
                    semicolon_offset = paragraph.text.find(u';', start_pos)
                    continue        # parenthetical segment, ignore
            if semicolon_offset + 2 >= len(paragraph.text):
                semicolon_offset = paragraph.text.find(u';', semicolon_offset + 1)
                continue
            next_seg = get_next_segment(paragraph, semicolon_offset + 2)  # skip space
            if not next_seg in main_symbols:
                semicolon_offset = paragraph.text.find(u';', semicolon_offset + 1)
                continue
            else:
                run_idx = run_index_from_offset(paragraph, semicolon_offset + 2)
                if run_idx < 0 or run_idx >= len(paragraph.runs):
                    warning (db_cursor, u'Bad run index while extracting mn. ot. (ignored).', paragraph)
                elif not paragraph.runs[run_idx].italic:
                    break
                else:
                    semicolon_offset = paragraph.text.find(u';', semicolon_offset + 1)

        if semicolon_offset >= 0:
            descriptor.semicolon_offset = semicolon_offset - 1;

        aspect_symbol_found, end_offset = check_aspect_symbol(paragraph, self.paragraph_offset, descriptor, semicolon_offset)
        if aspect_symbol_found:
            self.offset_to_end = end_offset - 1
        else:
            if descriptor.semicolon_offset > paragraph_offset:
                self.offset_to_end = semicolon_offset
            else:
                self.offset_to_end = len(paragraph.text) - 1

        #
        #    Triangle section may be in parantheses
        #
        parenth_match = re.match(r'^.+?\([^\)\(]?(\uF057.+?)\).*?', paragraph.text)
        if parenth_match != None:
#            self.source = parenth_match.group(1)
            self.paragraph_offset = parenth_match.start(1) + 1
            self.offset_to_end = parenth_match.end(1) - 1
        else:    
            #
            #    ... or may be followed by aspect pair mark, section mark, or restricted forms mark
            #
            found = re.search(r'[§$\uF047]', paragraph.text[triangle_offset+1:])
            if None != found:
                end_offset = triangle_offset + found.end(0) - 1
                self.offset_to_end = min(self.offset_to_end, end_offset)

        self.left_bracket_offset = paragraph.text.find(u'[', triangle_offset+1, self.offset_to_end);
        while self.left_bracket_offset >= 0:
            if not is_in_parentheses(paragraph, self.left_bracket_offset):
                self.offset_to_end = self.left_bracket_offset - 1
                break            
            self.left_bracket_offset = paragraph.text.find(u'[', self.left_bracket_offset+1, self.offset_to_end);            

        return self.offset_to_end, True

    #  check_triangle()

    #
    #  Extract triangle section, mark italicized words
    #
    def preprocess(self):

        if self.paragraph_offset < 0 or self.offset_to_end < self.paragraph_offset:
            warning (db_cursor, u'preprocess(): offsets not set, unable to extract triangle section.', self.paragraph)
            return False

        current_offset = self.paragraph_offset
        current_offset = offset_to_next_text_segment(self.paragraph, current_offset)

        self.source = u''

        segments = []
        
        current_run_index = run_index_from_offset(self.paragraph, current_offset)
        last_run_index = run_index_from_offset(self.paragraph, self.offset_to_end)

        if current_run_index < 0 or current_run_index > last_run_index:
            warning(db_cursor, u'Unable to preprocess triangle section: incorrect run index.', self.paragraph)
            return False

        first_run_index = current_run_index

        try:
            processed_text = u''
            current_run = self.paragraph.runs[current_run_index]

            while current_run_index <= last_run_index:

                while current_run_index <= last_run_index and current_run.italic:
                    processed_text += current_run.text
                    if current_run_index == first_run_index:
                        initial_run_offset = run_offset_from_paragraph_offset(self.paragraph, first_run_index, current_offset)
                        processed_text = processed_text[initial_run_offset:]
                    current_run_index += 1
                    if current_run_index <= last_run_index:
                        current_run = self.paragraph.runs[current_run_index]

                if len(processed_text) > 0:
                    segments.append( (True, processed_text) )
                    processed_text = u''

                while current_run_index <= last_run_index and not current_run.italic:
                    if current_run.font.name == 'Tim_acc':
                        processed_text += u'/'
                    elif current_run.font.name == 'Tim_pob':
                        processed_text += u'\\'        
                    processed_text += current_run.text
                    if current_run_index == first_run_index:
                        initial_run_offset = run_offset_from_paragraph_offset(self.paragraph, first_run_index, current_offset)
                        processed_text = processed_text[initial_run_offset:]
                    current_run_index += 1
                    if current_run_index <= last_run_index:
                        current_run = self.paragraph.runs[current_run_index]

                if len(processed_text) > 0:
                    segments.append( (False, processed_text) )
                    processed_text = u''

            remove_from_end = 0
            if current_run_index-1 == last_run_index:
                remove_from_end = len(current_run.text) - run_offset_from_paragraph_offset(self.paragraph, current_run_index-1, self.offset_to_end) - 1

            for segment in segments:
                i_at = segments.index(segment)
                if i_at > 0:
                    cur_seg = segments[i_at]
                    prev_seg = segments[i_at-1]

                    if cur_seg[1].startswith(u'.'):
                        prev_seg_text = (prev_seg[1]) + u'.'
                        cur_seg_text = (cur_seg[1])[1:]
                        segments[i_at-1] = (prev_seg[0], prev_seg_text)
                        if len(cur_seg_text) < 1:
                            segments.remove(cur_seg)
                        else:
                            segments[i_at] = (cur_seg[0], cur_seg_text)

            for s in segments:
                i_at = segments.index(s)
                if i_at > 0:
                    if s[1].isspace():
                        segments[i_at] = (segments[i_at-1][0], segments[i_at][1])

            self.source = u''
            for s in segments:
                if s[0]:
                    non_space_match = re.match(r'^(\s*)(.+?)(\s*)$', s[1])
                    if (non_space_match != None) and not non_space_match.group(2).isspace():
                        self.source += non_space_match.group(1) + u'_' + non_space_match.group(2) + u'_' + non_space_match.group(3)
                        self.source = self.source.replace(u'__', u'_')
                    else:
                        self.source += s[1]
                else:
                    self.source += s[1]

            if remove_from_end != 0:
                self.source = self.source[:-remove_from_end];

            self.source = re.sub(r'(\S+)\s*//\s*(\S+)', r'\1 // \2', self.source)
            self.source = re.sub(r'(_\s*_)', r' ', self.source)

            diamond_offset = self.source.find(u'\uF047')
            if diamond_offset < 0:
                length = len(self.source)
            else:
                length = diamond_offset

            semicolon = False
            semicolon_offset =  self.source.rfind(u';', 0, length)
            if semicolon_offset >= 0:
                left_open_parenth_offset = self.source.rfind(u'(', 0, semicolon_offset-1)
                if -1 == left_open_parenth_offset:
                    semicolon = True
                else:
                    close_parenth_offset = self.source.find(u')', left_open_parenth_offset+1)
                    if -1 == close_parenth_offset:
                        semicolon = True
                        warning (db_cursor, u'is_in_parentheses(): closing parenthesis not found.', self.paragraph)
#                    else:
#                        semicolon = False

            if semicolon:
                rhs = self.source[semicolon_offset+1:].strip()
                if len(rhs) > 0:
                    rhs_split = rhs.split()
                    next = u''
                    if len(rhs_split) > 0:
                        next = rhs_split[0]
                    else:
                        next = rhs
                    if (next != None and len(next) > 0):
                        if next in main_symbols.keys():
                            self.source = self.source[:semicolon_offset]
                        else:
                            semicolon = False

            self.semicolon = semicolon

        except:
            warning(db_cursor, u'Unable to preprocess triangle section, exception {0}.'.format(sys.exc_info()[0]), self.paragraph)
            return False

        return True

#       preprocess()

    #
    #  One or more forms, e.g.: Д. мн. церкв|ам //  -ям, Т. мн. -ами //  -ями, П. мн. -ах //  -ях
    #
    def extract_individual_forms(self, inflection_symbol, source):

        try:

            self.initial_form = None

            gram_marker = None
            number = None
            match_string = None

            if POS.POS_VERB == inflection_symbol:
                if (source.replace(u'_', u'').startswith(u'1') or
                    source.replace(u'_', u'').startswith(u'2')  or
                    source.replace(u'_', u'').startswith(u'3')): 
            # буд. 1 ед. забегу, 3 мн. -ут
                    match_string = r'.*?(\d)\s+(ед|мн)\.,?\s*(.+)'

            if POS.POS_NOUN == inflection_symbol:
            # Д., П. ед. лити|и, Т. ед. ей
            # Т. ед. ей, Р. мн. судий
                match_string = r'.*?_(И|В|Р|Д|Т|П)\.,?_?\s+(ед|мн)\.,?\s*(.+)'

            match = re.match(match_string, source)
            
            while len(source) > 0 and match != None:
                gram_marker = match.group(1).strip(u'_.,; ')

                number = match.group(2)
                if u'ед' == match.group(2):
                    number = u'Sg'
                elif u'мн' == match.group(2):
                    number = u'Pl'
                else:                   # expect мн. <xxx>, see кружева
                    if self.descriptor.main_symbol == u'мн.':
                        number = u'Pl'

                key = None

                if POS.POS_NOUN == inflection_symbol:
                    if not gram_marker in case_values:
                        warning(db_cursor, u'Unknown case value {0}.'.format(case), paragraph)
                        break
                    key = u'Noun_' + number + u'_' + case_values[gram_marker]

                if POS.POS_VERB == inflection_symbol:
                    if gram_marker != u'1' and gram_marker != u'2' and gram_marker != u'3':
                        warning(db_cursor, u'Unknown person value {0}.'.format(gram_marker), paragraph)
                        break
                    key = u'Pres_' + number + u'_' +  gram_marker

#                    next = split_on_whitespace[current_segment]
#                    source = source[len(next):].strip()
                """
                next = next.replace(u'_', u'')
                if case != None:
                    if next.startswith(u'мн.'):
                        number = u'Pl'
                        current_segment += 1
                        if current_segment >= len(split_on_whitespace):
                            continue
                    elif next.startswith(u'ед.'):
                        number = u'Sg'
                        current_segment += 1
                        if current_segment >= len(split_on_whitespace):
                            continue
                    else:
#                       else:  expect мн. <xxx>, see кружева
                        if self.descriptor.main_symbol == u'мн.':
                            number = u'Pl'
                """
                    
                source = source[match.end(2):].strip(u'_.,; ')

                self.lead_comment, source = self.extract_comment(source)
                if self.lead_comment != None:
                    self.descriptor.irregular_forms_lead_comment = self.lead_comment
                split_on_whitespace = source.split()
                if None == split_on_whitespace[0]:
                    warning(db_cursor, u'Unable to extract individual forms.', paragraph)
                    break

                current_segment = 0
                current_segment, form_dict = self.extract_form(source, split_on_whitespace, current_segment)
                form = form_dict[u'form']
                if None == form:
                    warning(db_cursor, u'Unable to parse irregular forms: form not found.', self.paragraph)
                    return

                if None == self.initial_form:
                    self.initial_form = form

                f = IrregularForm()
                f.form = self.normalize_form(form)
                f.lead_comment = form_dict[u'lead_comment']
                f.trailing_comment = form_dict[u'trailing_comment']
                self.forms[key] = f

                alt_form = form_dict[u'alt_form']
                if alt_form != None:
                    af = IrregularForm()
                    af.form = self.normalize_form(alt_form)
                    af.lead_comment = form_dict[u'alt_lead_comment']
#                        af.trailing_comment = form_dict[u'alt_trailing_comment']
                    self.alt_forms[key] = af

                if current_segment != None:
                    source = u' '.join(split_on_whitespace[current_segment:]).strip()
                else:
                    source = u''

                if source.startswith(u','):
                    source = source[1:].strip()

                match = re.match(match_string, source)
                    
#                self.source = source

            #
            # TODO: add missing forms for mn. or ed.
            #

        except KeyError as unknown_key_ex:
            warning(db_cursor, u'Unable to parse irregular forms.', self.paragraph)
        except:
            warning(db_cursor, u'Unable to parse irregular forms.', self.paragraph)

        return

#   extract_individual_forms()

    #
    #  Comments: (_затрудн._) etc
    #
    def extract_comment(self, source):
#        extract_comment_regex = r'^((?:_\(|\(_).+(?:\)_|_|)).*'
#        extract_comment_regex = r'^(?:_\(|\(_)([^_\)]+)(\)_|_\)).*'
        extract_comment_regex = r'(?:_\(|\(_|_)(_?[^_\)]+)(\)_|_\)|_).*'

        comment_match = re.match(extract_comment_regex, source)
        comment = None
        if comment_match != None:
            comment = comment_match.group(1)
            source = source[comment_match.end(2):]
            comment = comment.strip(u'()_')
            comment = comment.replace(u'_', u'')

        return comment, source


    #
    # Extracts a single irregular form with possible leading and trailing comments
    # return what's left of the source string
    #
    def extract_form(self, source, word_sequence, current_word):

        next = word_sequence[current_word].strip()
        source = source[len(word_sequence[current_word]):].strip()

        results = {}
        results[u'form'] = None
        results[u'alt_form'] = None
        results[u'lead_comment'] = None
        results[u'trailing_comment'] = None
        results[u'alt_lead_comment'] = None
#        results[u'alt_trailing_comment'] = None    # doesn't exist?

# lead comment:
        lead_comment, ignore = self.extract_comment(u' '.join(word_sequence[current_word:]).strip())

        if lead_comment != None:
            results[u'lead_comment'] = lead_comment
            current_word += 1            
            if current_word >= len(word_sequence):
                return None, results
     
        next = word_sequence[current_word].strip(u' ,')
        next = next.replace(u'_', u'')
#        source = source[len(word_sequence[current_word]):].strip()

# form:
        results[u'form'] = next

        current_word += 1

        if current_word >= len(word_sequence):
            return None, results

        next = word_sequence[current_word].strip()
#        source = source[len(word_sequence[current_word]):].strip()

# trailing comment:
        trailing_comment, ignore = self.extract_comment(next)
        if trailing_comment != None:
            results[u'trailing_comment'] = trailing_comment
            current_word += 1
            if current_word >= len(word_sequence):
                return None, results

        next = word_sequence[current_word].strip()
        source = source[len(word_sequence[current_word]):].strip()

# alt form group:
        if next.startswith(u'//'):

            current_word += 1
            if current_word >= len(word_sequence):
                warning (db_cursor, u'Alt. form not found', self.paragraph)
                return None, None

            next = word_sequence[current_word].strip()
            source = source[len(word_sequence[current_word]):].strip()

            alt_lead_comment, ignore = self.extract_comment(next)
            if alt_lead_comment != None:
                results['alt_lead_comment'] = alt_lead_comment
                current_word += 1               
                if current_word >= len(word_sequence):
                    warning (db_cursor, u'Alt. form not found', self.paragraph)
                    return None, None
                
            next = word_sequence[current_word].strip()
            source = source[len(word_sequence[current_word]):].strip()
# form:
            alt_form = None
            alt_form_match = re.match(r'([^\s,]+)', next)
            if alt_form_match != None:
                results[u'alt_form'] = alt_form_match.group(1).replace(u'_', u'')
                current_word += 1
                if current_word >= len(word_sequence):
                    return None, results

        return current_word, results

#       extract_form()

    def extract_comparative(self):
        self.source = self.source[8:]
        split_on_whitespace = self.source.split()
        if len(split_on_whitespace) < 1:
            warning(db_cursor, u'Unable to extract comparative form.', paragraph)
            return

        current_segment, form_dict = self.extract_form(self.source, split_on_whitespace, 0)
        if None != current_segment:
            self.source = self.source[len(u''.join(split_on_whitespace[:current_segment])):].strip()
        else:
            self.source = u''

        if form_dict != None:
            if form_dict[u'form'] != None:
                f = IrregularForm()
                f.form = form_dict[u'form']
                f.lead_comment = form_dict[u'lead_comment']
                f.trailing_comment = form_dict[u'trailing_comment']
                self.forms[u'AdjComp'] = f

            if form_dict[u'alt_form'] != None:
                af = IrregularForm()
                af.lead_comment = form_dict[u'lead_comment']
                af.form = form_dict[u'alt_form']
                af.trailing_comment = form_dict[u'trailing_comment']
                self.alt_forms[u'AdjComp'] = af

        return

#   extract_comparative()

    #
    #  кф м; кф см.; кф + paradigm
    #
    def extract_short_forms(self):
    #                        gender_match = re.match(u'(?:_)?.+?(?:_)?\s?(м_|м).*', self.source)
        gender_match = re.match(r'(?:_)?.+?(?:_)?\s?(м_).*', self.source)
        if gender_match:
            self.source = self.source[gender_match.end(1):]
            split_on_whitespace = self.source.split()
            if len(split_on_whitespace) < 1:
                warning(db_cursor, u'Unable to extract masculine short form.', paragraph)
                return

            current_segment, form_dict = self.extract_form(self.source, split_on_whitespace, 0)
            if None != current_segment:
                self.source = self.source[len(u''.join(split_on_whitespace[:current_segment])):].strip()
            if form_dict != None:
                if form_dict[u'form'] != None:
                    f = IrregularForm()
                    f.form = form_dict[u'form']
                    f.lead_comment = form_dict[u'lead_comment']
                    f.trailing_comment = form_dict[u'trailing_comment']
                    self.forms['AdjS_M'] = f

            if form_dict[u'alt_form'] != None:
                af = IrregularForm()
                af.lead_comment = form_dict[u'lead_comment']
                af.form = form_dict[u'alt_form']
                af.trailing_comment = form_dict[u'trailing_comment']
                self.alt_forms[u'AdjS_M'] = af

            if None == current_segment:
                self.source = u''

        else:
            split_on_space = self.source.split(u' ', 1)
            if len(split_on_space) < 2:
                warning(db_cursor, u'Unable to find short forms.', paragraph)
                return

            self.source = split_on_space[1]
            self.expand_short_adj_paradigm()

        return

#   extract_short_form()

    def extract_imperatives(self, source):

        split_on_whitespace = source.split()
        if len(split_on_whitespace) < 2:
            warning(db_cursor, u'Unable to extract imperative.', paragraph)
            return

        if split_on_whitespace[0].replace(u'_', u'') != u'повел.':
            warning(db_cursor, u'Unable to extract imperative.', paragraph)
            return

        split_on_whitespace = split_on_whitespace[1:]

        if u'нет' == split_on_whitespace[0].replace(u'_', u''):
            self.descriptor.no_imperative = True
            return

        current_segment, form_dict = self.extract_form(source, split_on_whitespace, 0)

#        if None != current_segment:
#            self.source = self.source[len(u''.join(split_on_whitespace[:current_segment])):].strip()

        if form_dict != None:
            if form_dict[u'form'] != None:
                f = IrregularForm()
                f.form = self.normalize_form(form_dict[u'form'])
                f.lead_comment = form_dict[u'lead_comment']
                f.trailing_comment = form_dict[u'trailing_comment']
                self.forms[u'Impv_Sg_2'] = f

        if form_dict[u'alt_form'] != None:
            af = IrregularForm()
            af.lead_comment = form_dict[u'lead_comment']
            af.form = self.normalize_form(form_dict[u'alt_form'])
            af.trailing_comment = form_dict[u'trailing_comment']
            self.alt_forms[u'Impv_Sg_2'] = af

#        if None == current_segment:
#            self.source = u''

        return

    def extract_adverbial(self, source):

        split_on_whitespace = source.split()
        if len(split_on_whitespace) < 2:
            warning(db_cursor, u'Unable to extract adverbial.', paragraph)
            return

        if split_on_whitespace[0].replace(u'_', u'') != u'деепр.':
            warning(db_cursor, u'Unable to extract adverbial.', paragraph)
            return

        is_past = False

        split_on_whitespace = split_on_whitespace[1:]

        if split_on_whitespace[0].replace(u'_', u'') == u'прош.':
            past = True
            split_on_whitespace = split_on_whitespace[1:]

        if u'нет' == split_on_whitespace[0].replace(u'_', u''):
            self.descriptor.no_adverbial = True
            return

        if u'затрудн.' == split_on_whitespace[0].replace(u'_', u''):
            self.descriptor.adverbial_difficult = True
            return

        current_segment, form_dict = self.extract_form(source, split_on_whitespace, 0)

#        if None != current_segment:
#            self.source = self.source[len(u''.join(split_on_whitespace[:current_segment])):].strip()

        if form_dict != None:
            if form_dict[u'form'] != None:
                f = IrregularForm()
                f.form = self.normalize_form(form_dict[u'form'])
                f.lead_comment = form_dict[u'lead_comment']
                f.trailing_comment = form_dict[u'trailing_comment']
                if is_past:
                    self.forms[u'VAdv_Past'] = f
                else:
                    self.forms[u'VAdv_Pres'] = f

        if form_dict[u'alt_form'] != None:
            af = IrregularForm()
            af.lead_comment = form_dict[u'lead_comment']
            af.form = form_dict[u'alt_form']
            af.trailing_comment = form_dict[u'trailing_comment']
            if is_past:
                self.forms[u'VAdv_Past'] = af
            else:
                self.forms[u'VAdv_Pres'] = af

#        if None == current_segment:
#            self.source = u''

        return

#   extract_adverbials()

    #
    #  церкв|ам, -ах --> церквам, церквах
    #
    def normalize_form(self, form):
        split_on_ending_separator = form.split(u'|')
        if len(split_on_ending_separator) > 1:
            self.stem = split_on_ending_separator[0]
            return self.stem + split_on_ending_separator[1]
        elif form.startswith(u'-'):
            stem = None
            ending = form[1:]

            if None == self.stem:
                if None == self.initial_form:
                    warning(db_cursor, u'Unable to parse irregular forms: stem or initial form not found.', self.paragraph)
                    return u''

                if self.initial_form[-1:] in (vowels + u'йь'):
#                    return self.initial_form[:-1] + form[1:]
                    stem = self.initial_form[:-1]
                else:
                    stem = self.initial_form
#                    return stem + form[1:]
            else:
                stem = self.stem

            if ending.find(u'/') > -1 or ending.find(u'ё') > -1:    # з/адал + -/а => задал/а
                stem = stem.replace(u'/', u'')

            return stem + ending

        else:
            return form

    #
    #  Abbreviated paradigm
    #
    def expand_noun_paradigm(self):
#  мн. 
#  мн. куры, кур, курам [// курицы, куриц, курицам] 
#  мн. сосед|и, -ей, -ям

#given: NGD
#need to construct: ALI

#in pl D --> I [м]и
#      D --> L м --> х
      
#      if anim: G = A, otherwise N = A
#        offset_to_next = 0
#        split = re.split(u'[,\s]+', self.source[offset_to_next:])
        split = re.split(r'[,\s\)]+', self.source)
        if None == split:
            warning (db_cursor, u'Error expanding irregular form list: unable to split.', self.paragraph)
            return False

        try:

            iAt = 0

            next = split[iAt].replace(u'_', '')
            if next != u'мн.' and next != u'ед.':
                warning (db_cursor, u'Error expanding irregular form list: expect ''mn.'' or ''ed.''.', self.paragraph)
    #            return False
            else:
                iAt += 1

            next = split[iAt]
        
            lead_comment, ignore = self.extract_comment(next)
            if lead_comment != None:
                self.lead_comment = lead_comment
                split = split[iAt:]

    #        if len(split) != 4:
    #            warning (db_cursor, u'Error expanding irregular form list: expect exactly three forms.', self.paragraph)
    #            return False
        
            next = split[iAt].replace(u'_', '')
            split_on_ending_separator = next.split(u'|')

            n_pl = IrregularForm()
            if len(split_on_ending_separator) > 1:
                n_pl.form = split_on_ending_separator[0] + split_on_ending_separator[1]
            else:
                n_pl.form = next

            self.assign(u'Noun_Pl_' + u'N', n_pl)  

            iAt += 1

            g_pl = IrregularForm()                
            g_pl.form = split[iAt].replace(u'_', '')
            self.assign(u'Noun_Pl_' + u'G',  g_pl)

            iAt += 1

            d_pl = IrregularForm()
            d_pl.form = split[iAt].replace(u'_', '')
            self.assign(u'Noun_Pl_' + u'D', d_pl)

            for f in self.get_keys():

                if f[5:7] == u'Pl':
                   if f[-1:] == u'G' or f[-1:] == u'D':

                    if self.get(f).form.startswith(u'-'):
                        ending = self.get(f).form
                        ending = ending[1:]
                        stem = None
                        if len(split_on_ending_separator) > 1:
                            stem = split_on_ending_separator[0]
                        else:
                            stem = self.get(u'Noun_Pl_' + u'N').form
                            stem = stem[:-1] 

                        if ending.find(u'/') > -1:    # з/адал + -/а => задал/а
                            stem = stem.replace(u'/', u'')

                        self.assign_form(f, stem+ending)

            if len(split) > 4:
                self.source = u' '.join(split[4:])
            else:
                self.source = u''

            is_animate = False
            if self.descriptor.main_symbol in (u'мо', u'жо', u'мо-жо', u'со', u'мс-п', u'мн. одуш.'):
                is_animate = True

            a_pl = IrregularForm()                
            if is_animate:
                a_pl.form = g_pl.form
            else:
                a_pl.form = n_pl.form
            self.assign(u'Noun_Pl_' + u'A', a_pl)
            
            i_pl = IrregularForm()                
            i_pl.form = d_pl.form + u'и'
            self.assign(u'Noun_Pl_' + u'I', i_pl)

            l_pl = IrregularForm()                
            l_pl.form = d_pl.form[:-1] + u'х'
            self.assign(u'Noun_Pl_' + u'P', l_pl)

        except:
            warning (db_cursor, u'Error expanding irregular noun paradigm.', self.paragraph)
            return False

        return

#    expand_noun_paradigm()

    def expand_short_adj_paradigm(self):
      
        offset_to_next = 0
        split = re.split(r'[,;\s]+', self.source[offset_to_next:])
        if None == split:
            warning (db_cursor, u'Error expanding irregular form list: unable to split.', self.paragraph)
            return False

        lead_comment, ignore = self.extract_comment(split[0])
        if lead_comment != None:
            self.lead_comment = lead_comment
            split = split[1:]
        
        next = split[0].replace(u'_', '')
        split_on_ending_separator = next.split(u'|')

        try:
            m = IrregularForm()
            if len(split_on_ending_separator) > 1:
                m.form = split_on_ending_separator[0] + split_on_ending_separator[1]
            else:
                m.form = next

#            self.forms[u'AdjS_M'] = m
            self.assign(u'AdjS_M', m)

            f = IrregularForm()                
            f.form = split[1].replace(u'_', '')
#            self.forms[u'AdjS_F'] = f
            self.assign(u'AdjS_F', f)

            n = IrregularForm()
            n.form = split[2].replace(u'_', '')
#            self.forms[u'AdjS_N'] = n
            self.assign(u'AdjS_N', n)

            pl = IrregularForm()
            pl.form = split[3].replace(u'_', '')
#            self.forms[u'AdjS_Pl'] = pl
            self.assign(u'AdjS_Pl', pl)

            
            for f in [u'AdjS_F', u'AdjS_N', u'AdjS_Pl']:
                if self.get(f).form.startswith(u'-'):
#                if self.forms[f].form.startswith(u'-'):
#                    ending = self.forms[f].form
                    ending = self.get(f).form
                    ending = ending[1:]
                    stem = None
                    if len(split_on_ending_separator) > 1:
                        stem = split_on_ending_separator[0]
                    else:
#                        stem = self.forms[u'AdjS_M'].form
                        stem = self.get(u'AdjS_M').form

                    if ending.find(u'/') > -1:    # з/адал + -/а => задал/а
                        stem = stem.replace(u'/', u'')

#                    self.forms[f].form = stem + ending
                    self.assign_form(f, stem + ending)

            if len(split) > 4:
                self.source = u' '.join(split[4:])
            else:
                self.source = u''

        except:
            warning (db_cursor, u'Error expanding irregular short form list.', self.paragraph)
            return False

        return

    # expand_short_adj_paradigm()

    def expand_present_tense(self, source):

        offset_to_next = 0
        split = re.split(r'[,;\s]+', source[offset_to_next:])
        if None == split:
            warning (db_cursor, u'Error expanding irregular form list: unable to split.', self.paragraph)
            return False

        lead_comment, ignore = self.extract_comment(split[0])
        if lead_comment != None:
            self.lead_comment = lead_comment
            split = split[1:]

        all_forms = []
        current_form = []   # current form + possible alt form
        expect_alt_form = False

        for i_at in range (0, len(split)):
            current_segment = split[i_at].strip(''.join(white_space_characters) + u')][')

            if len(current_segment) < 1:
                warning (db_cursor, u'Error expanding irregular present tense forms: unrecognized separator.', self.paragraph)
                continue

            if current_segment.startswith(r'//'):
                expect_alt_form = True
                continue

            if expect_alt_form:
                if len(current_form) != 1:
                    warning (db_cursor, u'Error expanding irregular present tense forms: non-alt form expected.', self.paragraph)
                    return False
            elif len(current_form) > 0:
                all_forms.append(current_form)
                current_form = []

            current_form.append(current_segment)
            expect_alt_form = False

        if expect_alt_form:
            warning (db_cursor, u'Error expanding irregular present tense forms: alt form expected.', self.paragraph)
            return False

        if len(current_form) > 0:
            all_forms.append(current_form)

        if len(all_forms) < 0:
            warning (db_cursor, u'Error expanding irregular present tense forms: no forms found.', self.paragraph)
            return False

        if len(all_forms) != 2 and len(all_forms) != 3 and len(all_forms) != 6:
            warning (db_cursor, u'Error expanding irregular present tense forms: unexpected number of forms in abbreviated paradigm.', 
                     self.paragraph)
            return False

        is_reflexive = False
        if all_forms[0][0].endswith(u'сь'):
            is_reflexive = True

        sg1 = all_forms[0][0]
        sg1_ending = u''
        if is_reflexive:
            sg1_ending = all_forms[0][0][-3]
        else:
            sg1_ending = all_forms[0][0][-1]

        if len(sg1) > len(sg1_ending):
            if u'/' == sg1[-1*(len(sg1_ending)+1)]:
                sg1_ending = u'/' + sg1_ending

        sg3 = all_forms[1][0]
        sg3_ending = u''
        if is_reflexive:
            sg3_ending = all_forms[1][0][-4:]
        else:
            sg3_ending = all_forms[1][0][-2:]

        if len(sg3) > len(sg3_ending):
            if u'/' == sg3[-1*(len(sg3_ending)+1)]:
                sg3_ending = u'/' + sg3_ending

        alt_sg3 = u''
        if len(all_forms[1]) > 1:
            alt_sg3 = all_forms[1][1]

        sg3_stress_pos = stress_syllable_pos(sg3)
        if sg3_stress_pos < 0:
            warning (db_cursor, u'Unable to find irregular stress pos for 1 Pers. Pl.', self.paragraph)

        alt_sg3_stress_pos = -1
        if alt_sg3 != u'':
            alt_sg3_stress_pos = stress_syllable_pos(alt_sg3)
            if alt_sg3_stress_pos < 0:
                warning (db_cursor, u'Unable to find irregular stress pos for 1 Pers. Pl., alt. form', self.paragraph)
        
#
# P. 89
#        
        iAt = 0
        for number in range (1, 3):
            for person in range(1, 4):

                form_available = True
                generated_form = u''
                alt_generated_form = u''

                if 1 == person and 2 == number:
                    if len(all_forms) < 6:
                        form_available = False                        
                        if is_reflexive:
                            generated_form = sg3[:-3] + u'мся'
                            if len(alt_sg3) > 0:
                                alt_generated_form = alt_sg3[:-3] + u'мся'
                        else:
                            generated_form = sg3[:-1] + u'м'
                            if len(alt_sg3) > 0:
                                alt_generated_form = alt_sg3[:-1] + u'м'

                if 2 == person:
                    if len(all_forms) < 6:
                        form_available = False
                        if 1 == number:
                            if is_reflexive:
                                generated_form = sg3[:-3] + u'шься'
                                if len(alt_sg3) > 0:
                                    alt_generated_form = alt_sg3[:-3] + u'шься'
                            else:
                                generated_form = sg3[:-1] + u'шь'
                                if len(alt_sg3) > 0:
                                    alt_generated_form = alt_sg3[:-1] + u'шь'
                        elif 2 == number:
                            if is_reflexive:
                                generated_form = sg3[:-3] + u'тесь'
                                if len(alt_sg3) > 0:
                                    alt_generated_form = alt_sg3[:-2] + u'тесь'
                            else:
                                generated_form = sg3[:-1] + u'те'
                                if len(alt_sg3) > 0:
                                    alt_generated_form = alt_sg3[:-1] + u'те'

                if 3 == person and 2 == number:
                    if len(all_forms) < 3:
                        form_available = False

                        if sg3.endswith(u'ёт') or sg3.endswith(u'ётся') or sg3.endswith(u'ет') or sg3.endswith(u'ется'):
                            if is_reflexive:
                                generated_form = sg3[:-4] + sg1_ending + u'тся'
                            else:
                                generated_form = sg3[:-2] + sg1_ending + u'т'

                        if len(alt_sg3) > 0:
                            if alt_sg3.endswith(u'ёт') or alt_sg3.endswith(u'ётся') or alt_sg3.endswith(u'ет') or alt_sg3.endswith(u'ется'):
                                if is_reflexive:
                                    alt_generated_form = sg3[:-4] + sg1_ending + u'тся'
                                else:
                                    alt_generated_form = sg3[:-2] + sg1_ending + u'т'                           

                        if sg3.endswith(u'ит') or sg3.endswith(u'ится'):
                            if is_reflexive:
                                stem = sg3[:-4]
                            else:
                                stem = sg3[:-2]
                            if len(stem) > 0:
                                if stem[:-1] in u'цчшщ':
                                    generated_form = sg3[:-4] + u'ат'
                                else:
                                    generated_form = sg3[:-4] + u'ят'
                            else:
                                warning (db_cursor, u'Irregular stem not found.', self.paragraph)

                            if is_reflexive:
                                generated_form += u'ся'
                            
                        if len(alt_sg3) > 0:
                            if sg3.endswith(u'ит') or sg3.endswith(u'ится'):
                                if is_reflexive:
                                    stem = alt_sg3[:-4]
                                else:
                                    stem = alt_sg3[:-2]
                                if len(stem) > 0:
                                    if stem[:-1] in u'цчшщ':
                                        alt_generated_form = alt_sg3[:-4] + u'ат'
                                    else:
                                        alt_generated_form = alt_sg3[:-4] + u'ят'
                                else:
                                    warning (db_cursor, u'Alt-irregular stem not found.', self.paragraph)

                            if is_reflexive:
                                alt_generated_form += u'ся'

                    if len(generated_form) > 0:
                        generated_form = mark_stress_syllable_pos(generated_form, sg3_stress_pos)

                    if len(alt_generated_form) > 0:
                        alt_generated_form = mark_stress_syllable_pos(alt_generated_form, alt_sg3_stress_pos)

                form = u''
                if form_available:
                    form = self.normalize_form (all_forms[iAt][0])
                else:
                    form = self.normalize_form (generated_form)

                irf = IrregularForm()
                irf.form = form
                if 0 == iAt:
                    self.initial_form = irf.form

                if 1 == number:
                    key = u'Pres_Sg_{}'.format(person)
                else:
                    key = u'Pres_Pl_{}'.format(person)

                self.forms[key] = irf

                if len(alt_generated_form) > 0 or ((len(all_forms) > iAt) and len(all_forms[iAt]) > 1):
                    alt_irf = IrregularForm()
                    if form_available:
                        form = self.normalize_form (all_forms[iAt][1])
                    else:
                        form = self.normalize_form (alt_generated_form)
                    alt_irf.form = form
                    self.alt_forms[key] = alt_irf

                if form_available:
                    iAt += 1
#                if iAt > len(all_forms):
#                    break;

        return True

#    expand_present_tense

    def expand_past_tense(self, source):

        split = re.split(r'[,\s]+', source)
        if None == split:
            warning (db_cursor, u'Error expanding irregular form list: unable to split.', self.paragraph)
            return False

        lead_comment, ignore = self.extract_comment(split[0])
        if lead_comment != None:
            if len(split) < 2:
                warning (db_cursor, u'Error expanding irregular past tense forms: expect past tense form(s) after a comment.', self.paragraph)
                return
            self.lead_comment = lead_comment
            split = split[1:]
        
        all_forms = []
        current_form = []   # current form + possible alt form
        expect_alt_form = False
        only_masc = False
        self.initial_form = None

        if u'м' == split[0].strip(u'_'):
            if len(split) < 2:
                warning (db_cursor, u'Error expanding irregular past tense forms: expect past tense form after "м".', self.paragraph)
                return
            only_masc = True
            split = split[1:]

        for i_at in range (0, len(split)):
            current_segment = split[i_at].strip(''.join(white_space_characters) + u')][')

            if len(current_segment) < 1:
                warning (db_cursor, u'Error expanding irregular past tense forms: unrecognized separator.', self.paragraph)
                continue

            if current_segment.startswith(r'//'):
                expect_alt_form = True
                continue

            if expect_alt_form:
                if len(current_form) != 1:
                    warning (db_cursor, u'Error expanding irregular past tense forms: non-alt form expected.', self.paragraph)
                    return False
            elif len(current_form) > 0:
                all_forms.append(current_form)
                current_form = []

            current_form.append(current_segment)
            expect_alt_form = False

        if expect_alt_form:
            warning (db_cursor, u'Error expanding irregular past tense forms: alt form expected.', self.paragraph)
            return False

        if len(current_form) > 0:
            all_forms.append(current_form)

        if len(all_forms) < 1:
            warning (db_cursor, u'Error expanding irregular past tense forms: no forms found.', self.paragraph)
            return False

#        if len(all_forms) != 2 and len(all_forms) != 3:
#            warning (db_cursor, u'Error expanding irregular present tense forms: unexpected number of forms in abbreviated paradigm.', 
#                     self.paragraph)
#            return False

#
#   1st form: m exept for безл. when it is n
#   Last form: part act past if contains -ий (ся)"
#   Other forms: f, n, pl 
#
        last = all_forms[-1]

        if last[0].endswith(r'ий') or last[0].endswith(r'ийся'):
            past_part_act = IrregularForm()
            self.initial_form = self.normalize_form (all_forms[0][0])
            past_part_act.form = self.normalize_form (last[0])
#            self.forms[u'PPastA_M_Sg_N'] = past_part_act
            self.assign(u'PPastA_M_Sg_N', past_part_act)
            if len(last) > 1:
                past_part_act.form = self.normalize_form (last[1])
#                self.alt_forms[u'PPastA_M_Sg_N'] = past_part_act
                self.assign(u'PPastA_M_Sg_N', past_part_act)
            all_forms.pop()

        if len(all_forms) < 1:
            warning (db_cursor, u'Error expanding irregular past tense forms: no forms found.', self.paragraph)
            return False

        self.stem = None
        for key in [u'Past_M', u'Past_F', u'Past_N', u'Past_Pl']:
            f = IrregularForm()
# безл?
            f.form = self.normalize_form (all_forms[0][0])
            if 'Past_M' == key:
                self.initial_form = f.form
            self.forms[key] = f

            if len(all_forms[0]) > 1:
                af = IrregularForm()
                af.form = self.normalize_form (all_forms[0][1])
                self.alt_forms[key] = af

            all_forms.pop(0)

            if len(all_forms) < 1:
                break

        if u'Past_F' in self.forms:
            if not u'Past_N'in self.forms:
                fn = IrregularForm()
                fn = self.forms[u'Past_F'].copy()
                back_step = -1
                finale = u''
                if fn.form.endswith(u'сь') or fn.form.endswith(u'ся'):
                    back_step = -3
                    finale = fn.form[-2:]
                fn.form = fn.form[:back_step] + u'о'
                if back_step == -3:
                    fn.form = fn.form + finale
                self.forms[u'Past_N'] = fn
            if not u'Past_Pl'in self.forms:
                fpl = IrregularForm()
                fpl = self.forms[u'Past_F'].copy()
                back_step = -1
                finale = u''
                if fpl.form.endswith(u'сь') or fpl.form.endswith(u'ся'):
                    back_step = -3
                    finale = fpl.form[-2:]
                fpl.form = fpl.form[:back_step] + u'и'
                if back_step == -3:
                    fpl.form = fpl.form + finale
                self.forms[u'Past_Pl'] = fpl

        return True

#    expand_past_tense

    def expand_participles(self, source):
        split = re.split(r'[,\s]+', source)
        if None == split:
            warning (db_cursor, u'Error expanding irregular form list: unable to split.', self.paragraph)
            return False

        lead_comment, ignore = self.extract_comment(split[0])
        if lead_comment != None:
            if len(split) < 2:
                warning (db_cursor, u'Error expanding irregular participial forms: expect participial form(s) after a comment.', self.paragraph)
                return
            self.lead_comment = lead_comment
            split = split[1:]

        if split[0].replace(u'_', u'').startswith (u'прош.'):
            if split[1].replace(u'_', u'').startswith (u'нет'):
                self.descriptor.no_part_past_act = True
            else:
                p = IrregularForm()
                p.form = self.normalize_form(split[1])
#                self.forms[u'PPastA_M_Sg_N'] = p
                self.assign(u'PPastA_M_Sg_N', p)
            return

        if split[0].replace(u'_', u'').startswith (u'наст.'):
            if split[1].replace(u'_', u'').startswith (u'нет'):
                self.descriptor.no_part_pres_act = True
            else:
                p = IrregularForm()
                p.form = split[1]
#                self.forms[u'PPresA_M_Sg_N'] = p            
                self.assign(u'PPresA_M_Sg_N', p)            
            return

        if split[0].replace(u'_', u'').startswith (u'страд.'):
            if len(split) < 2:
                return

            if split[1].replace(u'_', u'').startswith (u'наст.'):
                if split[2].replace(u'_', u'').startswith (u'нет'):
                    self.descriptor.no_part_pres_pass = True
                else:
                    p = IrregularForm()
                    p.form = self.normalize_form(split[2])
#                    self.forms[u'PPresPL_M_Sg_N'] = p
                    self.assign(u'PPresPL_M_Sg_N', p)
                return
            else:
                p = IrregularForm()
                p.form = self.normalize_form(split[1])
                self.assign(u'PPastPL_M_Sg_N', p)
                iAt = 2
                if len(split) > 2:
                    if u'//' == split[2]:
                        if len(split) < 4:
                            warning (db_cursor, u'Error expanding irregular part. past passive alternative form: expect participial form(s) after a doubleslash.', self.paragraph)
                            return
                        alt = IrregularForm()
                        alt.form = split[3]
                        self.alt_forms[u'PPastPL_M_Sg_N'] = alt
                        iAt = 3
                
                match = re.match(r'\(_кф_\s+?(\S+?)(\s+?//\s+?\S+?)?\s+?(\S+?)(\s+?//\s+?\S+?)?\s+?(\S+?)(\s+?//\s+?\S+?)?\s+?(\S+?)(\s+?//\s+?\S+?)?\)', u' '.join(split[2:]).strip())
                if match != None:
                    position = 1
                    for key in [u'PPastPS_M', u'PPastPS_F', u'PPastPS_N', u'PPastPS_Pl']:
                        kf = IrregularForm()
                        kf.form = self.normalize_form (match.group(position))
                        if 1 == position:
                            self.stem = kf.form            #
                            self.initial_form = kf.form    #  which of the two?
                        self.forms[key] = kf

                        alt = match.group(position+1)
                        if alt != None and alt.strip().startswith(u'//'):
                            alt_kf = IrregularForm()
                            alt_kf.form = self.normalize_form (alt.strip(u' /'))
                            self.alt_forms[key] = alt_kf

                        position += 2

#    expand_participles

    def parse(self, mode):

        alt_forms_parse = False
        if (u'alt_form_parse' == mode):
            alt_forms_parse = True

        self.preprocess()

        self.source = self.source.strip()
        split_on_colon = self.source.split(u':')
        if len(split_on_colon) > 1:
            lhs = split_on_colon[0]
            self.source = split_on_colon[1].strip()

# TODO: handle lhs

        try:
            if POS.POS_VERB == main_symbols[self.descriptor.inflection_symbol]:

                have_more = True
                while have_more:
                    length = self.source.find(u';')                
                    current = u''
                    if length > 0:
                        current = self.source[:length]
                        have_more = True
#                        if len(self.source) > length + 1:
#                            self.source = self.source[length+1:]
#                        else:
#                            warning(db_cursor, u'Error parsing verb forms.', paragraph)
#                            have_more = False
                    else:
                        current = self.source
                        have_more = False

                    present_tense = False
                    if (current.replace(u'_', u'').startswith(u'наст. (буд.)')):
                        split_on_first_space = current.split(u' ', 2)
                        if len(split_on_first_space) < 2:
                            warning(db_cursor, u'Unable to find present tense forms.', self.paragraph)
                            return
                        current = split_on_first_space[2]                    
                        present_tense = True
                    elif (current.replace(u'_', u'').startswith(u'наст.') or
                        current.replace(u'_', u'').startswith(u'буд.')):
                        split_on_first_space = current.split(u' ', 1)
                        if len(split_on_first_space) < 2:
                            warning(db_cursor, u'Unable to find present tense forms.', self.paragraph)
                            return
                        current = split_on_first_space[1]
                        present_tense = True

                    if present_tense:
                        if (current.replace(u'_', u'').startswith(u'1') or
                           current.replace(u'_', u'').startswith(u'2')  or
                           current.replace(u'_', u'').startswith(u'3')): 
                            self.extract_individual_forms(POS.POS_VERB, current)
                        else:
                            result = self.expand_present_tense(current)

                    if (current.replace(u'_', u'').startswith(u'повел.')):
                       self.extract_imperatives(current)

                    if (current.replace(u'_', u'').startswith(u'деепр.')):
                       self.extract_adverbial(current)

                    if (current.replace(u'_', u'').startswith(u'прош.')):
                        split_on_first_space = current.split(u' ', 1)
                        if len(split_on_first_space) < 2:
                            warning(db_cursor, u'Unable to find past tense forms.', self.paragraph)
                            return
                        current = split_on_first_space[1]
                        result = self.expand_past_tense(current)

                    if current.replace(u'_', u'').startswith(u'прич.'):
                        split_on_first_space = current.split(u' ', 1)
                        if len(split_on_first_space) < 2:
                            warning(db_cursor, u'Unable to find participial forms.', self.paragraph)
                            return
                        current = split_on_first_space[1]
                        self.expand_participles(current)

                    if length > 0 and length < len(self.source):
                        self.source = self.source[length:]
                        have_more = True
                    else:
                        self.source = u''
                        have_more = False

                    if self.source.startswith(u',') or self.source.startswith(u';'):
                        self.source = self.source[1:].strip()

            if POS.POS_NOUN == main_symbols[self.descriptor.inflection_symbol]:
            # Д., П. ед. лити|и, Т. ед. ей
            # Т. ед. ей, Р. мн. судий
                number = ''
                cases = []

                if self.source.replace(u'_', u'').startswith(u'В. ед.=И. ед.'):
                    cases.append(u'N Sg')
                    cases.append(u'A Sg')
                    number = 'Sg'

                expand = re.match(r'^_мн(?:_)?\.(?:_)?\s.*', self.source)
                if expand != None:
                    self.noun_paradigm = True;

                if self.noun_paradigm:
                    self.expand_noun_paradigm()
                else:
                    self.extract_individual_forms(POS.POS_NOUN, self.source)

            if POS.POS_ADJ == main_symbols[self.descriptor.inflection_symbol]:
                
                has_more = True
                while len(self.source) > 0:
                    
                    if self.source.replace(u'_', u'').startswith(u'сравн.'):
                        self.extract_comparative()
                    
                    elif self.source.replace(u'_', u'').startswith(u'кф'):
                        self.extract_short_forms()

                    else:
                        break
                    
                    if self.source.startswith(u','):
                        self.source = self.source[1:].strip()

            if not alt_forms_parse:
                for key in self.forms:
                    stress = IrregularStress()
                    form_text = self.forms[key].form
    #                form_text = self.get(key).form
                    if None == form_text:
                        warning (db_cursor, u'self.get(key) returned None for key ' + key, self.paragraph)
                        continue

    #                self.forms[key].form, self.forms[key].stress_dict = extract_stress_marks(form_text, self.descriptor.paragraph)
                    form, stress_dict = extract_stress_marks(form_text, self.descriptor.paragraph)
    #                if not self.has_alt_forms:
                    self.forms[key].form = form
                    self.forms[key].stress_dict = stress_dict
    #                else:
    #                    self.alt_forms[key].form = form
    #                    self.alt_forms[key].stress_dict = stress_dict
#            else:
            for key in self.alt_forms:
                alt_stress = IrregularStress()
                alt_form_text = self.alt_forms[key].form
#                form_text = self.get(key).form
                if None == alt_form_text:
                    warning (db_cursor, u'self.get(key) returned None for key ' + key, self.paragraph)
                    continue

#                self.forms[key].form, self.forms[key].stress_dict = extract_stress_marks(form_text, self.descriptor.paragraph)
                alt_form, alt_stress_dict = extract_stress_marks(alt_form_text, self.descriptor.paragraph)
                self.alt_forms[key].form = alt_form
                self.alt_forms[key].stress_dict = alt_stress_dict

        except KeyError as unknown_key_ex:
            warning(db_cursor, u'Unknown inflection symbol.', self.paragraph)
            return False

        return self.semicolon

#       parse()

    def save_to_db(self, db_cursor, descriptor_id):

        for key in self.forms:            
            try:
                params = (descriptor_id,
                          key,
                          self.forms[key].form,
                          False,
                          self.forms[key].lead_comment,
                          self.forms[key].trailing_comment,
                          False)                                # is_edited
                db_query = u'INSERT INTO irregular_forms VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)
                irregular_form_id = db_cursor.lastrowid

                for stress_pos in self.forms[key].stress_dict:
                    params = (irregular_form_id,
                              stress_pos,
                              self.forms[key].stress_dict[stress_pos],
                              False)                            # is_edited
                    db_query = u'INSERT INTO irregular_stress VALUES (NULL, ?, ?, ?, ?)'
#                    db_cursor.execute(db_query, params)

            except Exception as e:
                print ('Exception: %s, %s' % (sys.exc_info()[0], e))

        for key in self.alt_forms:
            
            try:
                params = (descriptor_id,
                          key,
                          self.alt_forms[key].form,
                          True,
                          self.forms[key].lead_comment,
                          self.forms[key].trailing_comment,
                          False)
                db_query = u'INSERT INTO irregular_forms VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)'
#                db_cursor.execute(db_query, params)
                irregular_form_id = db_cursor.lastrowid

                for stress_pos in self.alt_forms[key].stress_dict:
                    params = (irregular_form_id,
                              stress_pos,
                              self.alt_forms[key].stress_dict[stress_pos],
                              False)
                    db_query = u'INSERT INTO irregular_stress VALUES (NULL, ?, ?, ?, ?)'
#                    db_cursor.execute(db_query, params)

            except Exception as e:
                print ('Exception: %s, %s' % (sys.exc_info()[0], e))

#       save_to_db

#  class IrregularForm

#
#  parse_entry()
#
def parse_entry(paragraph, paragraph_index, headword, headless):

    if len(p.text) < 1:
        return False

    if is_chapter_heading(paragraph):
        return False

    if u';' == paragraph.text[0]:
        return False

    recent_changes_list = []
    has_recent_change_info = check_for_recent_changes(paragraph, recent_changes_list)

    offset = 0
    match = re.match(r'^[\uf074\t]*(.*?)', paragraph.text)
    if match != None:
        if match.group(1) != None:
            offset = match.start(1)

#    if has_recent_change_info:
#        del segments[0]

#        replace_aspect_symbol(p)

    headword.paragraph = paragraph

    if not headless:
        run_idx = headword.parse_source_data(paragraph, offset, False)  # not variant
        if run_idx >= len(paragraph.runs):
            return False                   # error??

        run_idx, offset = headword.check_headword_trailing_comment(paragraph, run_idx)
        if run_idx >= len(paragraph.runs):
            return False                   # error??

        if run_idx < 0 or offset < 0:
            warning(db_cursor, u'Bad run number or text offset.', paragraph)
            return False

#        run_idx, text_offset = headword.check_plural_of(paragraph, offset)
#        if run_idx >= len(paragraph.runs):
#            return False                   # error??
    else:
        run_idx = run_index_from_offset(paragraph, offset)
        if run_idx < 0:
            warning(db_cursor, u'Bad run number.', paragraph)
            return False

#    if p.text.endswith(u';'):
#        p.semicolon_offset = len(p.text) - 1
#        semicolon = True
#    else:
#        semicolon = False

    descriptor = Descriptor(paragraph)
#    dictionary[headword].append(descriptor)

    descriptor.paragraph_index = paragraph_index

#    current_offset = paragraph_offset_from_run_offset(paragraph, run_idx, 0)

    offset = check_plural_of(paragraph, offset, headword, descriptor)
    semicolon, current_offset = descriptor.parse_descriptor(headword, paragraph, offset, False, False)
                                                            #  ^-- no inflection type mismatch
    current_offset = check_trailing_comment(paragraph, current_offset, descriptor)
    if current_offset < 0 or current_offset >= len(paragraph.text):
        return True
    if u';' == paragraph.text[current_offset]:
        current_offset += 1
        if current_offset >= len(paragraph.text):
            return True
        semicolon = True

    """
    if current_offset < len(paragraph.text):
        current_offset = offset_to_next_text_segment(paragraph, current_offset)
        if current_offset >= 0 and current_offset < len(paragraph.text):
    """    

    while semicolon:
        semicolon = False
        run_idx = run_index_from_offset(paragraph, current_offset)

        main_descriptor = dictionary[headword][0]

        descriptor = Descriptor(paragraph)
        descriptor.is_secondary = True
#        dictionary[headword].append(descriptor)
        semicolon, current_offset = descriptor.parse_descriptor(headword, paragraph, current_offset, False, False)
        current_offset = check_trailing_comment(paragraph, current_offset, descriptor)

        if not descriptor.main_symbol in main_symbols.keys():
            continue

        if (None == descriptor.inflection_group or \
                (descriptor.inflection_group != None and not descriptor.inflection_group.has_data)) and \
          main_symbols[descriptor.main_symbol] == POS.POS_NOUN and \
                main_descriptor.inflection_group != None and \
          main_descriptor.inflection_group.type != 0 and \
          u'п' == main_descriptor.main_symbol:
            if headword in dictionary:
                main_descriptor = dictionary[headword][0]
                descriptor.inflection_symbol = main_descriptor.main_symbol
                descriptor.alt_inflection_symbol = main_descriptor.alt_inflection_symbol
                descriptor.inflection_group = main_descriptor.inflection_group
            else:
                warning(db_cursor, u'Unable to find previous descriptor.', paragraph)

        if current_offset < 0 or current_offset >= len(paragraph.text):
            break
        if u';' == paragraph.text[current_offset]:
            current_offset += 1
            if current_offset >= len(paragraph.text):
                break
            semicolon = True

    if current_offset >= len(paragraph.text):
        return True

    while run_idx < len(p.runs) and paragraph.runs[run_idx].italic:
        run_idx += 1
            
    if run_idx >= len(paragraph.runs):
        return True

    '''
    semicolon_run_offset = p.runs[run_idx].text.find(u';')
    while semicolon_run_offset != -1:            
        semicolon_offset = paragraph_offset_from_run_offset(p, run_idx, semicolon_run_offset)
        if -1 == semicolon_offset:
            continue
        if 0 == semicolon_offset:
            warning (db_cursor, u'Suspicious parenth at offset 0.', paragraph)
            continue

        if (is_in_parentheses(p, semicolon_offset)):
            continue
    '''       

#        find_example_section_offset(p)

    return True      #  parse_entry()

#
#  Main
#
if __name__=="__main__":
    db_connection = sqlite3.connect ('../Zal-Data/ZalData/ZalData_Aspect.db3')
    db_cursor = db_connection.cursor()

    errors_file = codecs.open('../Zal-Data/ZalData/conversion_errors_aspect.txt', encoding='utf-16', mode='w')
    zal = Document('../Zal-Data/verbs.docx')

#    out_doc = Document()

#    out_file = codecs.open('test_data.txt', encoding='utf-16', mode='w') 

    dictionary = defaultdict(list)

    text_to_headword_obj = {}

    paragraphs = zal.paragraphs

    spryazh_sm = {}

    current_paragraph_num = -1
    expect_alt_inflection_group = False

    semicolon = False
    outer_semicolon = False

    for current_paragraph_num in range (len(paragraphs)):

        p = paragraphs[current_paragraph_num]
        current_paragraph_num = current_paragraph_num + 1

#        if current_paragraph_num % 100 == 0:
#            print (current_paragraph_num)
# TEST!!!
#            if current_paragraph_num >= 100:
#                break
# TEST!!!

        if not outer_semicolon:
            headword = Headword()
        elif None == headword:
            warning (db_cursor, u'No headword instance.', p)

        ret = parse_entry(p, current_paragraph_num, headword, outer_semicolon)
        if not ret:
            continue

        text_to_headword_obj[headword.headword_text] = headword
        headword.seq_number = current_paragraph_num
        headword.seq_number = current_paragraph_num

        if p.text.rstrip().endswith(';'):
            outer_semicolon = True
        else:
            outer_semicolon = False

    db_connection.commit()
    db_cursor.close()
    db_connection.close()

    print ('Aspect semicolon variants: {}'.format(num_aspect_semicolons))
    print ('Multiple semicolon variants: {}'.format(num_multiple_aspect_pairs))

    os._exit(0)
