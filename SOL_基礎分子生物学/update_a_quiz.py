#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, glob, inspect, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from bs4 import BeautifulSoup
from pprint import pprint

def get_args():
    parser = argparse.ArgumentParser(
        description='csvファイル内容で、SOL上のクイズ問題を更新する'
    )
    parser.add_argument('csv_file',
        help='dump_QuizQuestions.pyで生成されたcsvファイルを編集したもの。ファイル名冒頭が"{科目ID}_{クイズID}"になっていると、該当するクイズを更新する'
    )
    parser.add_argument('-c', '--course_id', type=int,
        help='更新するクイズが属する科目ID（クイズIDの設定がないと無効）'
    )
    parser.add_argument('-q', '--quiz_id', type=int,
        help='クイズID（科目IDの設定がないと無効）'
    )

    return parser.parse_args()


args = get_args()

# course_id, quiz_id を取得
if args.course_id and args.quiz_id:
    course_id, quiz_id = args.course_id, args.quiz_id
else:
    course_id, quiz_id = [int(i) for i in args.csv_file.split(os.sep)[-1].split('_', 2) [0:2]]
    print('Course ID: {}'.format( course_id ))
    print('Quiz ID: {}'.format( quiz_id ))

#sys.exit()

course_name_start = '基礎分子生物学'

#################################################
# 更新対象のクイズ （Quiz object） を取得
#################################################

the_course = get_course(canvas, course_id)
print('Course Name: {}'.format( the_course.name ))

# sys.exit()

the_quiz = the_course.get_quiz(quiz_id)

# 更新内容を記載したCSVをロード
update_question_list = []
"""
以下の子リストを要素とするリスト
子リストの内容
    要素 0: 問題ID (int)
    要素 1: 問題テキスト（question_text）(str)
    要素 2: answers (dict)
            キー: 解答ID (int)
            値: 解答テキスト (str)
"""
with open(args.csv_file, newline='') as cf:
    _csv_line = []
    for l in csv.reader(cf):
        if l[0] == 'question':
            if len(_csv_line):
                update_question_list.append(_csv_line)
            _csv_line = [int(l[1]), l[2], {}]
        elif l[0] == 'answer':
            _csv_line[2][int(l[1])] = l[2]
    if len(_csv_line): # 最終行の処理
        update_question_list.append(_csv_line)

for qq_update in update_question_list:
    """
    qq_update[0]: 問題ID (int)
    qq_update[1]: 問題テキスト（question_text）(str)
    qq_update[2]: answers (dict)
          キー: 解答ID (int)
          値: 解答テキスト (str)
    """
    print('更新内容')
    pprint(qq_update)
    print('')
    the_question = get_question(the_quiz, qq_update[0])
    #print(dir(the_question))
    revise_dict = dict_from_object(the_question, question_attr_list)
    print('SOL上の問題データ')
    pprint(revise_dict)
    print('')
    revise_dict['question_text'] = qq_update[1]
    if len(qq_update[2]):
        reviced_answers = []
        for ans_opt in revise_dict['answers']:
            if 'html' in ans_opt.keys():
                ans_opt['html'] = qq_update[2][int(ans_opt['id'])]
            # HTMLタグを除去
            ans_opt['text'] = BeautifulSoup(qq_update[2][int(ans_opt['id'])], 'html.parser').get_text(strip=True)
            reviced_answers.append(ans_opt)
        revise_dict['answers'] = reviced_answers
    # else:
    # revise_dict.pop('answers')  #  誤った書き換え防止 → 効果なし
    print('更新後の問題データ')
    pprint(revise_dict)
    print("\n\n")
    ''' get_question(the_quiz, qq_update[0]) で修復済
    if revise_dict['question_type'] == 'numerical_question':
        for ans in revise_dict['answers']:
            ans['answer_exact'] = ans.pop('exact')
            ans['answer_error_margin'] = ans.pop('margin')
    '''
    the_question.edit(question = revise_dict)
