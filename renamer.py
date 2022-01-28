import os


def print_changes():
    refs_count = sum([sum([f[WORD_REFS][r] for r in f[WORD_REFS]]) for f in files_to_edit])
    renames_count = len([f for f in files_to_edit if f[NEEDS_RENAME]])
    print("Scanned %s files. Found %s words to replace and %s files to rename in a total of %s files. Check 'changes_output.txt' for details. "
    %(scanned_files,refs_count,renames_count,len(files_to_edit)))

def write_changes_to_file(words):
    with open("changes_output.txt", "w", encoding="utf-8") as f:
        f.write("Directory: %s\n" % SEARCH_PATH)
        for file in files_to_edit:
            line = file[FILEPATH].replace(SEARCH_PATH, "")
            if file[NEEDS_RENAME]:
                filename = file[FILEPATH].split(os.path.sep)[-1].split(".")[0]
                line += "->(%s)" % words[filename]
            if len(file[WORD_REFS]) > 0:
                total_refs = sum([file[WORD_REFS][ref] for ref in file[WORD_REFS]])
                line += " replacements(%s): [" % total_refs
                for ref in file[WORD_REFS]:
                    line += "%s->%s(%s)" % (ref,words[ref],file[WORD_REFS][ref]) 
                    if ref != list(file[WORD_REFS].keys())[-1]:
                        line += ", "
                    else: line += ']'
            if file != files_to_edit[-1]:
                line += "\n"
            f.write(line)
        
def find_all_references(line, word):
    start = 0
    while True:
        start = line.find(word, start)
        if start == -1: return
        is_char_before_valid = start == 0 or line[start-1] in CHARS_NEIGHBOURS_ALLOWED 
        is_char_after_valid = start + len(word) == len(line) or line[start + len(word)] in CHARS_NEIGHBOURS_ALLOWED

        if is_char_after_valid and is_char_before_valid: # Modify this check if you don't want start/before character restrictions 
            yield start, start + len(word)
        start += len(word) 

def replace_line(original_line, old_word, replacement_word):
    index_moved = 0
    line = original_line
    for i in find_all_references(original_line, old_word):
        char_before = i[0]  + index_moved
        char_after = i[1] + index_moved
        line = line[:char_before] + replacement_word + line[char_after:]
        index_moved += len(replacement_word) - len(old_word)
    return line

def edit_file(file, words):
    old, rep = (0,1)
    newpath = file
    with open(file, "r", encoding="utf-8") as f:
        new_file_content = ""
        for line in f.readlines():
            new_line = line
            new_word_line = new_line
            for word in words.items():
                if word[old] in new_line:
                    new_line = replace_line(new_line, word[old], word[rep])
            new_file_content += new_line 
    
    old_filename = file.split(os.path.sep)[-1] # old.txt
    for word in words.items():
        if word[old] == old_filename.split(".")[0]:
            new_filename = old_filename.replace(word[old], word[rep]) # old.txt -> new.txt
            newpath = file.replace(old_filename, new_filename)# /path/to/new.txt -> /path/to/new.txt
            os.remove(file)
            
    #write new content to new file
    with open(newpath, "w",encoding= "utf-8") as f:
            f.write(new_file_content.strip())

def edit_files(files,words):
    state =[" .  ","  . ","   ."]
    for i,file in enumerate(files):
        print("Editing files %s (%s/%s)" %(state[i % 3],i + 1, len(files)), end = "\r")
        edit_file(file[FILEPATH], words)
    print("DONE.. (%s/%s)                       " %( i + 1, len(files)))

def check_file(filepath, words):
    with open(filepath,"r", encoding= "utf-8") as f:
        rename = False
        refs = {}
        # check if filename needs to be renamed
        for word in words:
            if word == filepath.split(os.path.sep)[-1].split(".")[0]:
                rename = True

        for line in f.readlines():
            for word in words:
                line_refs = list(find_all_references(line, word))
                if len(line_refs) > 0:
                    refs[word] = refs.get(word, 0) + 1
              
    return {FILEPATH:filepath, NEEDS_EDIT:rename or len(refs) > 0, NEEDS_RENAME:rename, WORD_REFS:refs}

def scan_files(s_path, words):
    global scanned_files

    for fname in os.listdir(path = s_path):
        #if it is directory and doesn't match any ignored folder
        if os.path.isdir(s_path + fname) and not any([folder in fname for folder in IGNORE_FOLDERS]):
            scan_files(s_path + fname + os.path.sep, words)
        #if it is file and file extension is in allowed file types
        if os.path.isfile(s_path + fname) and fname.split(".")[1] in FILE_TYPES:
            file = check_file(s_path + fname, words.keys())
            scanned_files += 1
            if file[NEEDS_EDIT]:
                files_to_edit.append(file)
        
def get_sorted_words(words):
    # Get names from file sorted by length reversed in order to prevent conflicts
    # eg. 'my_old_text' will be replaced first if we also have 'old_text' to be replaced
    return dict(sorted(words.items(), key = lambda x: len(x[0]), reverse = True))

def load_words_from_file():
    
    if not os.path.isfile(WORDS_FILE):
        print("\nERROR: WORDS_FILE is not a valid file.")
        exit()
    
    if not os.path.isdir(SEARCH_PATH):
        print("\nERROR: SEARCH_PATH is not a valid directory.")
        exit()
    
    with open(WORDS_FILE,"r",encoding="utf-8") as f:
        raw = [l.strip() for l in f.readlines() if l.strip() != '']    
    if len(raw) == 0 :
            print("\nERROR: No words found in %s.\n" % WORDS_FILE)
            exit() 

    try:
        if KEYS_TO_VALUES:
            words = dict(item.split(KEY_VALUE_SEPERATOR) for item in raw)
        else:
            # swap values to keys if you want keys to be renamed to values
            words = dict((v,k) for k,v in [item.split(KEY_VALUE_SEPERATOR) for item in raw])
    except:
        print("\nERROR: Invalid key/pair values in %s. Current key/value seperator is '%s'\n" % (WORDS_FILE,KEY_VALUE_SEPERATOR))
        exit()
        
    if len(words) != len(raw):
        print("\nERROR: Replace keys are not unique in '%s'." % WORDS_FILE)
        keys = [item.split("=")[0] for item in raw]
        doubles = set(x for x in keys if keys.count(x) > 1)
        print( "Not unique values: %s" % doubles)
        exit()

    if len(words.values()) != len(set(words.values())):
        print("\nERROR: Replace values are not unique in %s." % WORDS_FILE)
        doubles = set(x for x in words.values() if list(words.values()).count(x) > 1)
        print( "Not unique values: %s" % doubles)
        exit()

    return get_sorted_words(words)

def run():
    words = load_words_from_file()
    print("\nScanning ..", end='\r', flush=True)
    scan_files(SEARCH_PATH, words)
    if len(files_to_edit) == 0:
        print("DONE..No need for changes in %s scanned files. You maybe need to switch 'KEYS_TO_VALUES' to '%s'." % (scanned_files, not KEYS_TO_VALUES))
        exit()
    else:
        write_changes_to_file(words)
        print_changes()
        if input("Proceed to edit (y)? Press any other key to cancel. ").lower() == 'y':
            edit_files(files_to_edit, words)
        else:
            print("Edit cancelled.")
            exit()
    
FILEPATH = "filepath"
NEEDS_EDIT = "needs_edit"
NEEDS_RENAME = "needs_rename"
WORD_REFS = "word_refs"
scanned_files = 0 
files_to_edit=[]

### SETTINGS ###

# If true, the keys gets replaced by the values.
KEYS_TO_VALUES = True 

# The parent folder where we start searching.
#SEARCH_PATH = r'../sample_parent_folder'+ os.path.sep
SEARCH_PATH = os.path.abspath(os.getcwd()) + os.path.sep + "sample_parent_folder" +os.path.sep

# The file that contains changes in key/value pairs in each line
WORDS_FILE = "words.txt"

# The seperator of key/value pair in the file, eg. word:replacement
KEY_VALUE_SEPERATOR= ":"

# If a folder name, inside parent directory, matches an entry then this folder will be ignored
IGNORE_FOLDERS = ["inside parent folder"]

# File types we want to edit
FILE_TYPES = ["txt"]

# If a replaceable word has a char from this list before or after it, it will be replaced, else will be ignored.
#CHARS_NEIGHBOURS_ALLOWED = list(" ,./*-+()[]{\}?@!=<>&$#%|;:\"")
CHARS_NEIGHBOURS_ALLOWED = list(" ,.-")

# Starts the script
run()