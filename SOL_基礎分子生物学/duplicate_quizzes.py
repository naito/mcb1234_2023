#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, json, glob, inspect, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint


def get_args():
    parser = argparse.ArgumentParser(
        description = '''同じコース内でクイズを複製する。例：python duplicate_quizzes.py -r "最終試験 \1" 4459 "^小テスト\s(\d+)$"'''
    )
    parser.add_argument('course_id', type=int,
        help='授業科目ID。'
    )
    parser.add_argument('quiz_re',
        help='複製元のクイズの名前。正規表現。'
    )
    parser.add_argument('-r', '--replica_name',
        help='複製先のクイズに付ける名前。target_reでキャプチャした文字列を使える。省略した場合、複製元のクイズ名の末尾に "(COPY)" を付加した名前になる。'
    )

    return parser.parse_args()

args = get_args()


the_course = get_course(canvas, args.course_id)

# 複製元クイズ名のパターンをコンパイル
quiz_name_pattern = re.compile(args.quiz_re)

# 複製先クイズ名のパターン
if args.replica_name:
    repl = args.replica_name
else:
    repl = r'\g<0> (COPY)'

def copy_quiz(qz):

    #クイズの複製
    quiz_dict = dict_from_object(qz, quiz_attr_list)
    quiz_dict['title'] = quiz_name_pattern.sub(repl, qz.title)
    quiz_dict['published'] = False
    dup_qz = the_course.create_quiz(quiz_dict)

    #グループの複製
    group_id_list = list(set([ q.quiz_group_id for q in get_questions(qz)]))
    # print('group_id_list = {}'.format(group_id_list))

    gid_map = dict()
    for gid in group_id_list:
        qg = qz.get_quiz_group(gid)
        # print('Group Object')
        # pprint(qg)
        # print('Group Dict')
        # pprint(dict_from_object(qg, quiz_groups_attr_list))
        qg_dict = dict_from_object(qg, quiz_groups_attr_list)
        dup_qg = dup_qz.create_question_group([qg_dict])
        gid_map[gid] = dup_qg.id

    #問題の複製
    for qq in get_questions(qz):
        qq_dict = dict_from_object(qq, question_attr_list)
        qq_dict['quiz_group_id'] = gid_map[qq_dict['quiz_group_id']]
        dup_qz.create_question(question = qq_dict)

    print('Copied: {} -> {}'.format(qz.title, quiz_dict['title']))
    return


def main():
    for qz in the_course.get_quizzes():
        print(qz.title)
        if quiz_name_pattern.match(qz.title):
            copy_quiz(qz)

if __name__ == '__main__':
    main()
