from get_fanpage_data import *
import pickle
import facebook
import requests
import json
import progressbar
from datetime import datetime
from datetime import timedelta

with open("test_list.txt", "rb")as c:
    FP_info_list = pickle.load(c)
    

implement("tokenXXXXXXXXXXXX", FP_info_list)
