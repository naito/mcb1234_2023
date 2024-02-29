#!/usr/bin/env python3
# coding: utf-8

from canvasapi import Canvas

import sys, csv, pprint, datetime
import numpy as np
from datetime import datetime


API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = "mi6UWq2vwyuio1srUcTptY4FFq2XNrZmLZxsBDu8XIS19dxO4oZf8Rc4NKMicImL"

course_name = '基礎分子生物学２'

course_id = 5283
# template_quiz = 2666
assignment_group_id = 5946  # 'Chapter Quiz'

titles = [f'Chapter Quiz {i}' for i in ['06', '07', '08', '09', '10']]

description = """<p>The time limit is 8 minutes and there are XX questions.</p>
<p>One question is displayed at a time, and you cannot go back after answering.</p>
<p>You can also move on to the next question without answering it (in which case you cannot go back).</p>"""
quiz_type = 'assignment'
shuffle_answers = True
time_limit = 8
allowed_attempts = 1
scoring_policy = 'keep_highest'
hide_results = 'always'
show_correct_answers = False
one_question_at_a_time = True
cant_go_back = True

#################################################
# 授業 （Course object） を取得
#################################################

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(course_id)

for title in titles:
    course.create_quiz( dict(
        title = title,
        description = description,
        quiz_type = quiz_type,
        shuffle_answers = shuffle_answers,
        time_limit = time_limit,
        allowed_attempts = allowed_attempts,
        scoring_policy = scoring_policy,
        hide_results = hide_results,
        show_correct_answers = show_correct_answers,
        assignment_group_id = assignment_group_id,
        one_question_at_a_time = one_question_at_a_time,
        cant_go_back = cant_go_back,
    ))
