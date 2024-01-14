import toml
from ctypes import *
import logging
import re
import time
import gc

#
# Helper class
#
if __name__== "__main__":

    gc.enable()
    gc.set_debug(gc.DEBUG_LEAK)

    with open('analyzer.toml', mode='r') as f:
        config = toml.load(f)
    
    lib_path = config['paths']['lib_path_windows']
    db_path = config['paths']['db_path_windows']
    text_path = config['paths']['text_path_windows']


#    lib_path = r'C:\git-repos\Zal\Zal-Core\out\build\x64-debug\ZalPythonItf.dll'
#    db_path = r'C:\git-repos\Zal\Zal-Data\ZalData\ZalData_Master_Tsvetaeva.db3'
#    text_path = r'C:\git-repos\Zal\Zal-Data\ZalData\Tsvetaeva_UTF-16_BOM.txt'
#    text_path = r'C:\git-repos\Zal\Zal-Data\ZalData\test.txt'

    zal_lib = cdll.LoadLibrary(lib_path)
    if zal_lib is None:
        logging.error('Unable to load Zal library.')
        exit(0)

    ret = zal_lib.Init(db_path)
    if not ret:
       logging.error('Unable to initialize Zal library.')
       exit(0)

    author = None
    book = None
    part = None
    chapter = None
    date = None
    title = None
    page = None

    texts = []
    text = ''

#    last_line = ''

    metadata = ''

    try:
        with open (text_path, encoding='utf-16', mode='r') as reader:
            lf_count = 0
            beginning_line_num = 0
            for line_num, line in enumerate(reader):
                line = line.rstrip()
                if not line:
                    lf_count += 1
                    continue
                logging.info(line_num)
                match = re.match(r'^\<(\w+?)\s+(.+?)\/(\w+)>', line)
                if match != None:
                    # Parse the text just read:
                    if len(text) > 0:
                        metadata = 'author = {0} | book = {1} | part = {2} | chapter = {3} | date = {4} | title = {5}'.format(
                            author, book, part, chapter, date, title)
                        logging.info(book)
                        isProse = False
                    start_tag = match.group(1)
                    value = match.group(2)
                    end_tag = match.group(3)

                    if start_tag != end_tag:
                        logging.error('Tag mismatch: %s', line)
                        continue

                    tag_name = start_tag

                    if 'author' == tag_name:
                        author = value
                    elif 'book' == tag_name:
                        book = value
                    elif 'part' == tag_name:
                        part = value
                    elif 'chapter' == tag_name:
                        chapter = value
                    elif 'date' == tag_name:
                        date = value
                    elif 'title' == tag_name:
                        title = value
                    elif 'page' == tag_name:
                        page = value
                    else:
                        logging.error ('Unable to parse tag: {0} in: {1}'.format(tag_name, line))
                else:
                    if lf_count > 1:
                        if text:
                            try:
                                isProse = False
                                last_text_id = zal_lib.llParseText(book, metadata, text, beginning_line_num, isProse)
                                del(text)
                                text = ''
                                gc.collect()
                                beginning_line_num = line_num
                            except:
                                import traceback
                                traceback.print_exc()
                            #        raw_input("Program crashed; press Enter to exit")
                                logging.error ('Exception: %s', e)
                        else:
                            lf_count = 0
                    else:
                        if text:
                            text += '\r\n'
                        text += line

#                last_line = line

    except Exception as e:
        import traceback
        traceback.print_exc()
#        raw_input("Program crashed; press Enter to exit")
        logging.error ('Exception: %s', e)
