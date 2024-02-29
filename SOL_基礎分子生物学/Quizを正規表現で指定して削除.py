#!/usr/bin/env python3
# coding: utf-8

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from canvasapi.util import combine_kwargs
from sol import *

from pprint import pprint

API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = ""

COURSE_ID = 5282  #  2022 基礎分子生物学１（GIGA）
QUIZ_RE = r'^ECB5\-.+$'


def main():
    #################################################
    # 授業 （Course object） を取得
    #################################################

    canvas = Canvas(API_URL, API_KEY)
    the_course = get_course(canvas, COURSE_ID)

    for quiz in [ q for q in the_course.get_quizzes() if re.match(QUIZ_RE, q.title)]:
        confirm = None
        while confirm not in ['','y','n']:
            confirm = input(f'Quiz『{quiz.title}』を削除していいですか？（[y],n）: ')
        if confirm == 'n':
            continue
        else:
            quiz.delete()


if __name__ == '__main__':
    main()
