from config import *
import codecs
import json
import os
  
"""
    Load file from disk
    @param path - path of the file to load
    @return the content of the file (string)
"""
def load_file(path):
    try:
	print 'load_file', path
	print "current dir", os.getcwd()
	fid = codecs.open(path, encoding = 'utf-8')
	content = fid.read()
	fid.close()
	print 'file content %s' % content
	return content
    except ValueError, e:
	print "load_file error", e
	return EMPTY_STRING

"""
    Load json-formatted file from disk
    @param path - path of the file to load
    @return json object of the content of the file
"""
def load_json_file(path):
    print 'load_json_file', path
    print "current dir", os.getcwd()
    content = load_file(path)
    try:
	obj = json.loads(content, encoding = 'utf-8')
	return obj
    except ValueError, e:
	print "load_json_file error", e
        return EMPTY_DICT

"""
    Print the categories loaded from file
"""
def print_categories(categories):
    for key, value in categories.iteritems():
	first_level_index = key / CATEGORY_ID_MULTIPLIER
	second_level_index = key % CATEGORY_ID_MULTIPLIER
	print "%d (%d, %d) = %s, %s" % (key, first_level_index, second_level_index, value[0], value[1])

