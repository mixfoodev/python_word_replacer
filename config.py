import os

### SETTINGS ###

# If true, the keys gets replaced by the values.
KEYS_TO_VALUES = True 

# The parent folder where we start searching. Replace it with your directory.
# eg SEARCH_PATH = r'path/to/your/folder'+ os.path.sep
SEARCH_PATH = os.path.abspath(os.getcwd()) + os.path.sep + "sample_parent_folder" +os.path.sep

# The file that contains the changes as key/value pairs in each line.
WORDS_FILE = "words.txt"

# The seperator of key/value pair in the file, eg. word:replacement.
KEY_VALUE_SEPERATOR= ":"

# Folders inside parent directory that you want to be ignored.
IGNORE_FOLDERS = ["some_folder"]

# File types you want to edit.
FILE_TYPES = ["txt"]

# If a replaceable word has a char from this list before or after it, it will be replaced else will be ignored.
#eg list(" ,./*-+()[]{\}?@!=<>&$#%|;:\"")
CHARS_NEIGHBOURS_ALLOWED = list(" ,.\n")