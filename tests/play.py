

# data structure is {
#           "RSS feed name": "<string>",
#           "URL": "<string>",
#           "keywords": [array]
#           }

list1 = ["ActivityPub", "test1", "test2", "test3", "test4", "test5"]
list2 = ["test2", "test3", "test4"]

def remove_keywords(old_list, remove_list):
    new_list = [item for item in old_list if item not in remove_list]
    print(new_list)
    return new_list

remove_keywords(list1, list2)





