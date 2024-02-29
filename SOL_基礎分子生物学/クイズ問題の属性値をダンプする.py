#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, glob, inspect
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint
import numpy as np

quiz_info = [
    # 基礎分子生物学４
    dict( course_id = 9888, quiz_id = 5850, ch = '16', type = 'ReadingQuiz', lang = 'ja' ),
]

quiz_course_map = { qi['quiz_id']:qi['course_id'] for qi in quiz_info}


course_name_start = '基礎分子生物学'

#################################################
# 授業 （Course object） を取得
#################################################

course_id_ls = list(set([ i['course_id'] for i in quiz_info ]))
course_list = {}
for cid in course_id_ls:
    course_list[cid] = get_course(canvas, cid)

for c in course_list.values():
    print('Course Name: {}'.format( c.name ))

# sys.exit()

#################################################
# クイズ （Quiz object） を取得
#################################################

quiz_list = []
for qi in quiz_info:
    quiz_list.append(course_list[qi['course_id']].get_quiz(qi['quiz_id']))

for qz in quiz_list:
    csv_out_list = [['種別','ID','英文のみ','原文'],]
    print('Quiz Name: {}'.format( qz.title ))
    for qq in get_questions(qz):
        print('Question ID: {}'.format( qq.id ))
        print('Question Type: {}'.format( qq.question_type ))
        # multiple_choice_question, multiple_answers_question, multiple_dropdowns_question
        # numerical_question, fill_in_multiple_blanks_question
        print('Question Text: {}'.format( qq.question_text ))
        # print('Available Answers: {}'.format( qq.answers ))
        csv_out_list.append(['question', qq.id, qq.question_text, qq.question_text])
        if qq.question_type in ('multiple_choice_question', 'multiple_answers_question', 'multiple_dropdowns_question'):
            for ans in qq.answers:
                if 'html' in ans.keys():
                    txt_key = 'html'
                else:
                    txt_key = 'text'
                print('Answer ID: {}'.format( ans['id'] ))
                print('Answer Text: {}'.format( ans[txt_key] ))
                csv_out_list.append(['answer', ans['id'], ans[txt_key], ans[txt_key]])

    with open('./{course_id}_{quiz_id}_{quiz_title}.csv'.format(
            course_id = quiz_course_map[qz.id],
            quiz_id = qz.id,
            quiz_title = qz.title ), 'w') as cf:
        w = csv.writer(cf)
        for l in csv_out_list:
            w.writerow(l)
