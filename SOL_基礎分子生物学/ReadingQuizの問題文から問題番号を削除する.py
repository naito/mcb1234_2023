#!/usr/bin/env python3
# coding: utf-8

from canvasapi import Canvas

import sys, csv, pprint, re
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup

API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = "mi6UWq2vwyuio1srUcTptY4FFq2XNrZmLZxsBDu8XIS19dxO4oZf8Rc4NKMicImL"

course_name = '基礎分子生物学２'

course_id = 5283
#template_quiz = 2664

rq_ids = [2704, 2705, 2706, 2707, 2708]

#################################################
# 授業 （Course object） を取得
#################################################

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(course_id)
# qz = course.get_quiz(rq_ids[0])
# q_list = list(qz.get_questions())
# print(f'Question: {dir(q_list[0])}')

for rq_id in rq_ids:
    qz = course.get_quiz(rq_id)
    for q in qz.get_questions():
        print(f'''question_text(original):
{q.question_text}''')
        question_name = re.search(r"\((Q\d+)\)\s*", q.question_text)
        question_text = re.sub(r'\(Q\d+\)\s*', '', q.question_text)
        # soup = BeautifulSoup(q.question_text, 'html.parser')
        # inner_html = soup.span.decode_contents(formatter="html")
        """
        print(f'''question_text:
{question_text}''')
        """
        # pprint.pprint(q)
        q.edit(question = dict(
            question_name = question_name.group(1) if question_name else q.question_name,
            question_text = question_text,
            position = q.position,
            question_type = q.question_type,
            points_possible = q.points_possible,
            correct_comments = q.correct_comments,
            incorrect_comments = q.incorrect_comments,
            neutral_comments = q.neutral_comments,
            answers = q.answers,
            correct_comments_html = q.correct_comments_html,
            incorrect_comments_html = q.incorrect_comments_html,
            neutral_comments_html = q.neutral_comments_html,
            variables = q.variables,
            formulas = q.formulas,
            answer_tolerance = q.answer_tolerance,
            formula_decimal_places = q.formula_decimal_places,
            matching_answer_incorrect_matches = q.matching_answer_incorrect_matches,
            ))
        # if question_name:
        #    sys.exit()
