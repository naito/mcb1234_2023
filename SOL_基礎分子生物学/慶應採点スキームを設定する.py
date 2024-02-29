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
対象課題：対象科目の課題のうち、課題名がリスト grading_assignment_names に含まれるもの
処理内容：科目の採点スキームに Keio Grading Scheme がなければ作成する
　　　　　対象科目の採点スキームに Keio Grading Scheme を設定し、満点を 100 に設定する
　　　　　既存の Keio Grading Scheme がある場合、それが設定される
"""
course_name_starts = '基礎分子生物学４'
grading_assignment_names = ['小テストの結果に基づく暫定評語', '成績評語',
    'Tentative grades based on Chapter Quiz results', 'Final Grade']

keio_grading_standard = dict(
    title = 'Keio Grading Scheme',
    grading_scheme=[])

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
    """
    Keio Grading Scheme が未登録なら登録する
    """
    keio_gs_exist = False
    keio_gs = None
    for gs in c.get_grading_standards():
        print('  Grading Standard Name: {}'.format( gs.title ))
        print('    grading_scheme: {}'.format( gs.grading_scheme ))

        if gs.title == keio_grading_standard['title']:
            keio_gs = gs
            keio_gs_exist = True
            break

    if not keio_gs_exist:
        print('\n  Keio Grading Scheme を追加する')
        keio_gs = c.add_grading_standards(
            title = keio_grading_standard['title'],
            grading_scheme_entry = keio_grading_standard['grading_scheme']
        )
    """
    成績登録課題に採点スキームを設定する
    """
    for a in c.get_assignments():
        if a.name in grading_assignment_names:
            print('  Assignment Name: {}'.format( a.name ))
            print('    grading_type: {}'.format( a.grading_type ))
            print('    grading_standard_id: {}'.format( a.grading_standard_id ))

            a.edit(assignment = dict(
                points_possible = 100,
                grading_type = 'letter_grade',
                grading_standard_id = keio_gs.id,
            ))
