#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, glob, inspect, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint
import numpy as np

course_name_starts = '基礎分子生物学'
group_name_starts = first_time_question_group_tag

""" 初出問題の """
first_time_tag = '<div style="display: none;">FA</div>'

is_first_time_question = {}  # キー：問題グループID 値：初出ならTrue、違えばFalse
quiz_group_name_list = []

def update_is_first_time_question_dict(qz, q):
    """
    クイズ qz の問題 q のクイズグループIDが、辞書 is_first_time_dict のキーに含まれない
    ようなら登録する
    値は、未出問題グループの場合 True、既出問題グループの場合 False
    """
    if q.quiz_group_id not in is_first_time_question.keys():
        qg = qz.get_quiz_group(q.quiz_group_id)
        is_first_time_question[q.quiz_group_id] = True if qg.name.startswith(group_name_starts) else False
        quiz_group_name_list.append(qg.name)


#################################################
# 授業 （Course object） を取得
#################################################

course_list = []
for c in get_courses_by_name_forward_match(canvas, course_name_starts):
    if is_current_course(c):
        course_list.append(c)
        print('\nCourse Name: {}'.format( c.name ))

# sys.exit()

#################################################
# クイズ （Quiz object） を取得
#################################################

for c in course_list:
    for qz in c.get_quizzes():
        if qz.quiz_type == 'assignment':
            print('Quiz Name: {}'.format( qz.title ))
            for q in qz.get_questions():
                if q.quiz_group_id is not None:
                    update_is_first_time_question_dict(qz, q)
                    if is_first_time_question[q.quiz_group_id]:
                        # print('Question ID: {}'.format( q.quiz_id ))
                        # print('   Group ID: {}'.format( q.quiz_group_id ))
                        # print('       text: {}'.format( q.question_text ))
                        # print('       HTML: {}'.format( is_html(q.question_text) ))
                        pass

unique_list = list(set(quiz_group_name_list))
unique_list.sort()
pprint(unique_list)
