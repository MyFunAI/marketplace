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
    except IOError, e:
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
	print 'json obj', obj
	print 'json fields %s' % obj["level1"][0]
	return obj
    except ValueError, e:
	print "load_json_file error", e
        return EMPTY_DICT
