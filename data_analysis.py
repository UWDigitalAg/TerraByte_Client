# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 20:56:24 2020

@author: M
"""

import json
import os
import pandas as pd
'''
jsons_parsed = []
print(os.getcwd())
for fp in os.listdir("./download/all_jsons"):
    if os.path.isfile("./download/all_jsons/"+fp):
        with open("./download/all_jsons/"+fp, "r") as f:
            jsons_parsed.append(json.load(f))

df = pd.json_normalize(jsons_parsed, sep=".")
print(df)
print(df.describe())
'''
import pprint

pprint.pprint({
    "something": 100,
    "something_else": "long text goes here",
    "a_dict": {"a": 10, "b": "c"}
}, indent=4)
