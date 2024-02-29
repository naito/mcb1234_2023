#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, glob, inspect, datetime
# import time
# start = time.time()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint
import numpy as np

"""
対象科目：今学期の開講科目のうち、文字列 course_name_starts で始まる科目
対象クイズ：assignment 属性のクイズ
処理内容：対象クイズに含まれる未出問題の問題IDのリストをCSV形式で出力
"""
course_name_starts = '基礎分子生物学'
first_time_tag = first_time_question_group_tag


#################################################
# 授業 （Course object） を取得
#################################################

course_list = []
for c in get_courses_by_name_forward_match(canvas, course_name_starts):
    if is_current_course(c):
        course_list.append(c)
        #print('\nCourse Name: {}'.format( c.name ))

# sys.exit()

#################################################
# クイズ （Quiz object） を取得
#################################################

first_time_question_list = [['問題ID','問題名','クイズ名'],]
first_time_group_id_list = []

for c in course_list:
    print('\nCourse Name: {}'.format( c.name ))
    for qz in c.get_quizzes():
        if qz.quiz_type == 'assignment':  # 未出問題は課題クイズだけに含まれる
            print('  Quiz Name: {}'.format( qz.title ))
            for q in qz.get_questions():
                if is_first_time_question(qz, q, first_time_group_id_list = first_time_group_id_list):
                    first_time_question_list.append([q.id, q.question_name, qz.title])

current_semester = get_ay_semester_by_datetime(datetime.datetime.now())
with open('./未出問題ID_{course_name_starts}_{year}_{semester}.csv'.format(
        course_name_starts = course_name_starts,
        year = current_semester['AY'],
        semester = current_semester['semester'] ), 'w') as cf:
    w = csv.writer(cf)
    for l in first_time_question_list:
        w.writerow(l)

# pprint(first_time_question_list)
# pprint(first_time_group_id_list)
# print('\n所要時間: {}'.format( time.time() - start ))
