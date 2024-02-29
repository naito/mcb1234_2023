#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, glob, inspect, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint
import numpy as np

"""
対象科目：今学期の開講科目のうち、文字列 course_name_starts で始まる科目
対象問題グループ：対象科目に含まれる問題グループのうち、リスト target_group_names に含まれる
    もの
処理内容：問題グループ名の冒頭に、文字列 first_time_tag を付加する
    （既に付加されている場合はスキップする）
"""
course_name_starts = '基礎分子生物学'
first_time_tag = '未出_'

"""
未出問題グループ名タグ first_time_tag を付加するグループ名のリスト
クイズ問題グループ名のリストを出力する.py の出力を加工して作成
"""
target_group_names = []


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

for c in course_list:
    print('\nCourse Name: {}'.format( c.name ))
    for qz in c.get_quizzes():
        if qz.quiz_type == 'assignment':
            print('  Quiz Name: {}'.format( qz.title ))
            for q in qz.get_questions():
                if q.quiz_group_id is not None:
                    qg = qz.get_quiz_group(q.quiz_group_id)
                    if qg.name in target_group_names:
                        update_dict = dict_from_object(qg, quiz_groups_attr_list)
                        # pprint(update_dict)
                        qg_name_before = qg.name
                        qg_name_after = first_time_tag + qg.name
                        update_dict['name'] = qg_name_after
                        qg.update(
                            id = q.quiz_group_id,
                            quiz_groups = [update_dict,]
                        )
                        print('    問題グループ名 "{}" を "{}" に変更しました'.format(qg_name_before, qg_name_after))
            """
            クイズ内容（問題や問題グループ）を変更した際、クイズを保存しないと変更内容が更新
            されないが、その作業を自動化できていない（以下のように現状のまま保存するだけでは
            ダメだった）
            qz_update_dict = dict_from_object(qz, quiz_attr_list)
            qz.edit(quiz = qz_update_dict)
            print('    クイズ "{}" を保存しました'.format(qz.title))
            sys.exit()
            """
