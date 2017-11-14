from bs4 import BeautifulSoup
import requests
import re
import time
import progressbar
import pickle

##############################get category list
url = "http://likeboy.tw/category.php?isCategory=1"
get_text = requests.get(url).text
soup = BeautifulSoup(get_text, "html.parser")


def get_category(href):
    return href and re.compile("category").search(href)

li_list = soup.find_all(href = get_category)
href_list = [["http://likeboy.tw/" + li.get("href"), li.get("href").replace("category.php?category_name=", "")] for li in li_list[3:-1]]

#herf_list --> all category href list on likeboy.tw
#for i in href_list:
#    print(i)


##############################function of getting fanpage list
def find_FP(href):
    return href and re.compile("pages_detail").search(href)
    

def get_FP_info(soup, category):
    FP_list = soup.find_all(href = find_FP)
    FP_href_list = [FP.get("href") for FP in FP_list]

    FP_info = []
    for i in FP_href_list:
        slim = i.replace("pages_detail.php?pages_id=", "").replace("&type=detail", "")
        slim_split = slim.split("&pages_name=")
        slim_split.append(category)
        FP_info.append(slim_split)
    
    return(FP_info)
    

def next_page(soup):
    #botton of next page
    next_page = soup.find("a", style = "cursor: auto;")
    try:
        next_page_url = "http://likeboy.tw/" + next_page.get("href")
    except:
        next_page_url = ""
    return(next_page_url)
    
    
def get_all_category_FP_info(url, category):
    big_list = []
    while True:
        get_text = requests.get(url).text
        soup = BeautifulSoup(get_text, "html.parser")

        food_1 = get_FP_info(soup, category)
        big_list.extend(food_1)

        next_page_url_return = next_page(soup)
        if len(next_page_url_return) != 0:
            url = next_page_url_return
        else:
            break
        time.sleep(2)
    return(big_list)
    
    
#########################get fan page list
#href_list[0]
#['http://likeboy.tw/category.php?category_name=主修科目', '主修科目']

final_list = []
bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
page_count = 1

for href in href_list:
    inside = get_all_category_FP_info(href[0], href[1])
    final_list.extend(inside)
    bar.update(page_count)
    page_count += 1
    time.sleep(5)
    
    
with open("test_list.txt", "wb")as c:
    pickle.dump(final_list, c)
