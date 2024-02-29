#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, json, glob, inspect, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint


def get_args():
    parser = argparse.ArgumentParser(
        description = '''クイズの属性をCSVファイルに出力する'''
    )
    parser.add_argument('course_id', type=int,
        help='授業科目ID。'
    )
    parser.add_argument('quiz_re',
        help='ダンプするクイズの名前。正規表現。'
    )

    return parser.parse_args()

args = get_args()

csv_out_list = [['course_id', 'id', 'title', 'description', 'quiz_type',
    'unlock_at', 'lock_at', 'time_limit', 'shuffle_answers',
    'show_correct_answers', 'scoring_policy', 'allowed_attempts',
    'one_question_at_a_time', 'points_possible', 'cant_go_back', 'due_at',
    'published', 'locked_for_user', 'hide_results',
    'show_correct_answers_at', 'hide_correct_answers_at'],]

the_course = get_course(canvas, args.course_id)

# 複製元クイズ名のパターンをコンパイル
quiz_name_pattern = re.compile(args.quiz_re)


def append_a_quiz(qz):
    csv_out_list.append([qz.course_id, qz.id, qz.title, qz.description, qz.quiz_type,
        None if qz.unlock_at is None
            else from_iso_to_jst(qz.unlock_at).isoformat(timespec = 'seconds'),
        None if qz.lock_at is None
            else from_iso_to_jst(qz.lock_at).isoformat(timespec = 'seconds'),
        qz.time_limit, qz.shuffle_answers, qz.show_correct_answers,
        qz.scoring_policy, qz.allowed_attempts, qz.one_question_at_a_time,
        qz.points_possible, qz.cant_go_back, qz.due_at,
        qz.published, qz.locked_for_user, qz.hide_results,
        qz.show_correct_answers_at, qz.hide_correct_answers_at
    ])


def write_csv():
    with open('./{course_id}_Quizzes_dump.csv'.format(
            course_id = the_course.id), 'w') as cf:
        w = csv.writer(cf)
        for l in csv_out_list:
            w.writerow(l)


def main():
    for qz in the_course.get_quizzes():
        if quiz_name_pattern.match(qz.title):
            append_a_quiz(qz)
    write_csv()

if __name__ == '__main__':
    main()
