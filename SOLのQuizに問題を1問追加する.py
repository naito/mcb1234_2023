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
QUIZ_ID = 3269  #  Chapter Quiz 04

TFQ_NAME_TMPL = '{t}-{ch:0=2}-{q}'
IMG_FOLDER_NAME = '{ch:0=2}'
IMG_PARENT_FOLDER_ID = 62119  #  'course files/TestBank'
IMG_PARENT_FOLDER_PATH = 'course files/TestBank'

canvas = Canvas(API_URL, API_KEY)
the_course = get_course(canvas, COURSE_ID)
the_quiz = the_course.get_quiz(QUIZ_ID)

new_question_kwargs = dict( question = dict(
    question_name = 'TFQ-14ABV-4.3.acd',
    question_text = '<p><span>Choose all correct statements.</span></p>',
    question_type = 'multiple_answers_question',
    points_possible = 1.0,
    neutral_comments_html = '''<p>DIF: Difficult REF: 4.3 OBJ: 4.3.a Explain how and why different forms of feedback control might be used to regulate enzyme activity. | 4.3.c Explain how chemical modification such as phosphorylation can influence a protein’s location and interactions. | 4.3.d Contrast how protein activity is regulated by phosphorylation or by the binding of nucleotides such as GTP or ATP. MSC: Evaluating</p>''',
    answers = [
        dict(
            text = '''Feedback inhibition is defined as a mechanism of down-regulating enzyme activity by the accumulation of a product earlier in the pathway.''',
            weight = 0.0
        ),
        dict(
            text = '''If an enzyme’s allosteric binding site is occupied, the enzyme may adopt an alternative conformation that is not optimal for catalysis.''',
            weight = 100.0
        ),
        dict(
            text = '''Protein phosphorylation is another way to alter the conformation of an enzyme and serves exclusively as a mechanism to increase enzyme activity.''',
            weight = 0.0
        ),
    ],
))
# multiple_answers_question の場合、選択肢に HTML が指定できない。たぶんバグ。

pprint(combine_kwargs(**new_question_kwargs))
the_quiz.create_question(**new_question_kwargs)


"""
■ 多選択肢問題（複数解答）
QuizQuestion(
    _requester=<canvasapi.requester.Requester object at 0x7fc8404114c0>,
    id=20864,
    quiz_id=2062,
    quiz_group_id=None,
    assessment_question_id=18193,
    position=None,
    question_name=MultipleAnswers,
    question_type=multiple_answers_question,
    question_text=<p><strong>question</strong> text</p>,
    points_possible=1.0,
    correct_comments=,
    incorrect_comments=,
    neutral_comments=,
    correct_comments_html=,
    incorrect_comments_html=,
    neutral_comments_html=<p>General Comments</p>,
    answers=[{'id': 3935,
    'text': 'AAAA',
    'comments': '',
    'comments_html': '',
    'weight': 100.0},
    {'id': 1692,
    'text': 'BBBB',
    'comments': '',
    'comments_html': '',
    'weight': 100.0},
    {'id': 7979,
    'text': 'CCCC',
    'comments': '',
    'comments_html': '',
    'weight': 0.0},
    {'id': 754,
    'text': 'DDDD',
    'comments': '',
    'comments_html': '',
    'weight': 0.0}],
    variables=None,
    formulas=None,
    answer_tolerance=None,
    formula_decimal_places=None,
    matches=None,
    matching_answer_incorrect_matches=None,
    course_id=4460
)
"""
