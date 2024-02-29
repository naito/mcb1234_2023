#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint

def get_args():
    parser = argparse.ArgumentParser(
        description='csvファイル内容で、SOL上のクイズの設定を更新する'
    )
    parser.add_argument('csv_file',
        help='dump_Quizzes.pyで生成されたcsvファイルを編集したもの。'
    )

    return parser.parse_args()

args = get_args()


csv_ls = []
with open(args.csv_file, newline='') as cf:
    csv_ls = [l for l in csv.reader(cf)]

# CSVの１行目は属性名
attr_ls = csv_ls.pop(0)
n_attr = len(attr_ls)

for qz_info in csv_ls:
    c = get_course(canvas, int(qz_info[attr_ls.index('course_id')]))
    print(c)
    qz_obj = c.get_quiz(int(qz_info[attr_ls.index('id')]))

    update_dict = dict_from_object(qz_obj, quiz_attr_list)
    for i in range(n_attr):
        update_dict[attr_ls[i]] = qz_info[i]
    qz_obj.edit(quiz = update_dict)
