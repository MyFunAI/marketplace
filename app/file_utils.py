from config import *
import json

"""
    Load file from disk
    @param path - path of the file to load
    @return the content of the file (string)
"""
def load_file(path):
    try:
	fid = open(path, mode = 'r', encoding = 'utf-8')
	content = fid.read()
	fid.close()
	return content
    except IOError, e:
	return EMPTY_STRING

"""
    Load json-formatted file from disk
    @param path - path of the file to load
    @return json object of the content of the file
"""
def load_json_file(path):
    content = load_file(path)
    try:
	obj = json.loads(content, 'utf-8')
	return obj
    except ValueError, e:
        return EMPTY_DICT
