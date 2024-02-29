#!/usr/bin/env python3
# coding: utf-8

from canvasapi import Canvas

import sys, csv, pprint, datetime
import numpy as np
from datetime import datetime


API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = "mi6UWq2vwyuio1srUcTptY4FFq2XNrZmLZxsBDu8XIS19dxO4oZf8Rc4NKMicImL"

course_name = '基礎分子生物学１'

course_id = 5282
#template_quiz = 2664

titles = [f'Mock Exam {i}' for i in ['04', '05']]

description = """<ul>
<li>
<p>This is a mock exam of approximately the same difficulty level as Chapter Quiz and Final Exam.</p>
</li>
<li>
<p>You can take it as many times as you want during the semester.</p>
</li>
<li>
<p>Your score will be displayed as soon as you submit your answers.</p>
</li>
<li>
<p>The correct and incorrect answers for each question will be displayed.</p>
<ul>
<li>
<p>The correct answers to questions that were answered incorrectly will not be displayed.</p>
</li>
</ul>
</li>
</ul>"""
quiz_type = 'practice_quiz'
shuffle_answers = True
time_limit = 20
allowed_attempts = -1
scoring_policy = 'keep_highest'
hide_results = None
show_correct_answers = False


#################################################
# 授業 （Course object） を取得
#################################################

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(course_id)
# qz = course.get_quiz(template_quiz)
# print(f'Quiz: {dir(qz)}')

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
    ))
