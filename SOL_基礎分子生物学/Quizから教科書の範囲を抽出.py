#!/usr/bin/env python3
# coding: utf-8

import re, sys, os, csv, glob, inspect, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bs4 import BeautifulSoup
# from copy import deepcopy

from canvasapi import Canvas
from canvasapi.util import combine_kwargs
from sol import *

from pprint import pprint

API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = ""

COURSE_ID = 5282  #  2022 基礎分子生物学１（GIGA）
Quiz_ids = [ 3441, 3442, 3443 ]

DIST_PATH = './SOL_基礎分子生物学/ECB5の問題毎の学修目標'

def main():
    #################################################
    # 授業 （Course object） を取得
    #################################################

    canvas = Canvas(API_URL, API_KEY)
    the_course = get_course(canvas, COURSE_ID)

    for Quiz_id in Quiz_ids:
        Quiz = the_course.get_quiz(Quiz_id)
        question_list = [['タイプ', '問題番号', '選択肢', '難易度', '範囲', '学修目標']]
        question_csv = []
        for Q in Quiz.get_questions():
            Qname_split = Q.question_name.split('-')
            Qnumber = re.search(r'^(?P<n>\d+)(?P<o>[A-z]*)$', Qname_split[2])
            # print(f'  Qname_split[2] : {Qname_split[2]}')
            if Qnumber.group('o') in ['', 'A']:
                if len(question_csv):
                    question_list.append(question_csv)
                    question_csv = []
                neutral_com = BeautifulSoup(Q.neutral_comments_html, 'html.parser').get_text().strip()
                print(f'\n{Q.question_name}:')
                question_csv = [Qname_split[0], Qnumber.group('n'), Qnumber.group('o')]
                m = re.search(r'DIF:\s+(?P<DIF>.+?)\s+REF:\s+(?P<REF>.+?)\s+OBJ:', neutral_com)
                question_csv.append(m.group('DIF'))
                question_csv.append(m.group('REF'))
                print(f'  DIF: {m.group("DIF")}\n  REF: {m.group("REF")}')

                obj = []
                for m in re.finditer(r'(?:OBJ:|\|)\s*(?P<OBJ>\d+\.\d+\.[a-z]+)\s', neutral_com):
                    obj.append(m.group('OBJ'))
                    print(f'  OBJ: {m.group("OBJ")}')
                question_csv.append('&'.join(obj))
            else:
                question_csv[2] += Qnumber.group('o')

            if question_csv[2] == '':
                question_list.append(question_csv)
                question_csv = []

        if len(question_csv):
            question_list.append(question_csv)

        dist_path = os.path.normpath(DIST_PATH)

        with open(os.path.join(dist_path, f'{Quiz.id}_{Quiz.title}.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows( question_list )




if __name__ == '__main__':
    main()
