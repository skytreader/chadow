import os
from chadow import DirectoryIndex

_repr = {}
curr = None

dir_index = DirectoryIndex(is_top_level=True)
subdir_traversal = []

#for root, dirs, files in os.walk("/home/chad/Documents/lib/References/Computer Science/Conceptual", topdown=False):
#for root, dirs, files in os.walk("/home/chad/kode/goodgame-coding-challenge", topdown=True):
#    print("### FILES: ###")
#    for name in files:
#        #dir_index.add_to_index(os.path.join(root, name))
#        print(os.path.join(root, name))
#
#    print("### DIRS: ###")
#    for name in dirs:
#        #dir_index.add_to_index(os.path.join(root, name))
#        print(os.path.join(root, name))
#
#    print("--------NEXT LEVEL--------")

subdir_traversal = ["/home/chad/kode/goodgame-coding-challenge"]
is_top_level = True
parents = {}

while subdir_traversal:
    curdir = subdir_traversal.pop()
    if is_top_level:
        curindex = dir_index
        is_top_level = False
    else:
        curindex = DirectoryIndex(subdir=curdir.split(os.sep)[-1], is_top_level=False)

    #for _file in os.listdir(curdir):
    for root, dirs, files in os.walk(curdir):
        for _file in files:
            curindex.add_to_index(_file)

        for _dir in dirs:
            subdir_traversal.append(os.path.join(root, _dir))
            parents[os.path.join(root, _dir)] = curindex

        # one run only
        break
    
    if parents.get(curdir):
        parents[curdir].add_to_index(curindex)

print(dir_index.to_json())
