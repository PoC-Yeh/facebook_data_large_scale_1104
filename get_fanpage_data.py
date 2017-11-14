import facebook
import requests
import json
import progressbar
from datetime import datetime
from datetime import timedelta


###########fanpage info
def fanpage_info(token_string, fan_page_id):
    token = token_string
    graph = facebook.GraphAPI(access_token = token, version = 2.7)
    id_string = '%s?fields=id,name,fan_count,birthday,likes,category'%(fan_page_id)
    post = graph.get_object(id = id_string)
    return(post)
    
    
def check_key(key_name, dict_name):
    if key_name in dict_name.keys():
        return(dict_name[key_name])
    else:
        return("")

def get_fanpage_info_list(post):
    inside = []
    inside.append(check_key("id", post))
    inside.append(check_key("name", post))
    inside.append(check_key("fan_count", post))
    inside.append(check_key("birthday", post))
    inside.append(check_key("category", post)) 
    return(inside)
    

########comments of posts and likes of posts info
def next_page_data(input_key): 
    all_data_list = []
    
    for i in input_key["data"]:
        all_data_list.append(i)
    
    if "paging" in input_key:
        while True:
            if "next" in input_key["paging"]:
                new_page = requests.get(input_key['paging']['next']).json()
                if "data" in new_page.keys():
                    for n in new_page["data"]:
                        all_data_list.append(n)
                input_key = new_page
            else:
                break
                
    return(all_data_list)
    
    
def update_likes_or_comments(input_key, all_data_list):  #all_data_list = next_page_data(input_key)
    input_key["data"] = all_data_list
    if "paging" in input_key.keys():
        del input_key["paging"]
        
        
def update(p):
    #update likes data of each post
    if "likes" in p.keys():
        p_likes = p["likes"]
        all_likes = next_page_data(p_likes)
        update_likes_or_comments(p_likes, all_likes)
    
        #update comments data of each post
    if "comments" in p.keys():
        p_comments = p["comments"]
        all_comments = next_page_data(p_comments)
        update_likes_or_comments(p_comments, all_comments)


def get_facebookFanPage_comment(token_string, fan_page_id):
    token = token_string
    graph = facebook.GraphAPI(access_token = token, version = 2.7)
    id_string = "%s?fields=posts{comments{id,message,created_time,like_count,reactions{username},from},created_time,message,likes}"%(fan_page_id)
    post = graph.get_object(id = id_string)
    
    #create list containing all posts messages, comments, etc.
    posts_list = []
    for p in post["posts"]["data"]: #page1
        update(p) #update likes and comments data of each post
        posts_list.append(p)
    print("posts : page 1 has been finished!")
    
    if "paging" in post["posts"].keys():
        print("moving on to page 2.")
        post2 = requests.get(post["posts"]['paging']['next']).json() #page2
        for p in post2["data"]:
            update(p)
            posts_list.append(p)
        print("posts : page 2 has been finished!")
        print("posts : if there is page 3, moving on to page 3.")

        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength) #page2~end
        post2_end = post2
        page_count = 3
        while True:
            if "paging" in post2_end:
                new_page = requests.get(post2_end['paging']['next']).json()
                for data in new_page["data"]:
                    update(data)
                    posts_list.append(data)
                bar.update(page_count)
                page_count += 1
                post2_end = new_page
            else:
                break
    return(posts_list)
    
    
def get_facebookFanPage_comment_list(d, page_info_list):
    big_list = []
    
    #print(d["created_time"])
    datetime_object = datetime.strptime(d["created_time"], '%Y-%m-%dT%H:%M:%S%z')
    new_time = datetime_object + timedelta(hours = 8)
    post_created_time = new_time.isoformat(" ")[:-6]
    
    #post_created_time = d["created_time"]
    message_id = d["id"]
    
    message = ""
    if "message" in d.keys():
        message = d["message"]
    
    if "likes" in d.keys():
        likes = d["likes"]["data"]
        post_like_count = len(likes)
        
        for person in likes:
            like_record = [person["id"], person["name"], "LIKE", post_created_time,"like_time_unknown", message_id, message, "", post_like_count]
            like_record.extend(page_info_list)
            big_list.append(like_record)
            
    if "comments" in d.keys():
        comment = d["comments"]["data"]
        post_comment_count = len(comment)
        
        for c in comment:
            fan_name = c["from"]["name"]
            fan_id = c["from"]["id"]
            fan_comment = c["message"]
            fan_comment_time = c["created_time"]
            #fan_like = c["like_count"]
            
            comment_record = [fan_id, fan_name, "COMMENT", post_created_time,fan_comment_time, message_id, message, fan_comment, post_comment_count]
            comment_record.extend(page_info_list)
            big_list.append(comment_record)
    
    if len(big_list) != 0:
        return(big_list)
        
        
def get_data(token_string, fan_page_id):
    final_list = []
    page_info_dict = fanpage_info(token_string, fan_page_id)
    page_info_list = get_fanpage_info_list(page_info_dict)
    
    page_comment_dict_list = get_facebookFanPage_comment(token_string, fan_page_id)
    for comment_dict in page_comment_dict_list:
        page_comment_list = get_facebookFanPage_comment_list(comment_dict, page_info_list)
        final_list.extend(page_comment_list)
    
    return(final_list)
    
    
def implement(token_string, FP_info_list):
    bar_out = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    page_count_out = 1
    thousand_count = 1

    all_data = []
    for fp in FP_info_list:
        try:
            fp_data_list = get_data(token_string, fp[0])
            all_data.extend(fp_data_list)

            bar_out.update(page_count)
            page_count_out += 1

        except:
            token_string = input("fill in the token : ")
            fp_data_list = get_data(token_string, fp[0])
            all_data.extend(fp_data_list)

        if page_count_out % 1000 == 0:
            with open("all_data_{}.txt".format(thousand_count), "wb")as c:
                pickle.dump(all_data, c)
            thousand_count += 1
            all_data = []

    with open("all_data_{}.txt".format(thousand_count), "wb")as c:
        pickle.dump(all_data, c)  
