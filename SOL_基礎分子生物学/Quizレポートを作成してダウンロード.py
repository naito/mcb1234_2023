#!/usr/bin/env python3
# coding: utf-8

import sys, os, time, requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from bs4 import BeautifulSoup
# from copy import deepcopy

from canvasapi import Canvas, exceptions
from canvasapi.util import combine_kwargs
from sol import *

from pprint import pprint

API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = ""

COURSE_NAME_STARTS = '基礎分子生物学４'  # 全角・半角に注意
EXAM_TYPE = '最終試験'  # '小テスト' または '最終試験'

# DIST_PATH = './SOL_基礎分子生物学/Quiz_reports'  # Amanawa
DIST_PATH = './SOL_基礎分子生物学/Quiz_reports'  # Ohgigayatsu


quizzes_name_start = {
    '小テスト' : ['小テスト', 'Chapter Quiz'],
    '最終試験' : ['最終試験', 'Final Exam']
}
quiz_title_starts = quizzes_name_start[EXAM_TYPE]


def get_report(Quiz):
    try:
        return Quiz.create_report('student_analysis', include = ['file',])
    except exceptions.Conflict as e:
        print(e)
        time.sleep(1)
        # wait_report_generation(Quiz)


def main():
    # 対象授業オブジェクトを取得
    course_list = []
    for c in get_courses_by_name_forward_match(canvas, COURSE_NAME_STARTS):
        if is_current_course(c):
            course_list.append(c)

    # 対象Quizオブジェクトを取得
    quiz_list = []
    for c in course_list:
        for start_tag in quiz_title_starts:
            hits = get_quizzes_by_name_forward_match(c, start_tag)
            if hits is not None:
                quiz_list.extend(hits)

    # クイズレポート作成開始
    for qz in quiz_list:
        qz.create_report('student_analysis', include = ['file',])

    # クイズレポート完成確認
    for qz in quiz_list:
        """すでにレポートがあると、例外発生
        ・2.2.0で再発 → バージョン2.1.0にしたら解決
        $ pip install canvasapi==2.1.0
        2023.02.03
        "report is already being generated" 発生後に
        $ pip install canvasapi --upgrade
        すると解決した。（canvasapi-3.0.0でOKだった）
        というか、エラー後に再実行すると通った。原因不明。

        ・canvasapiを2.1.0に更新したら解決した
        ・3.0.0で再発 → バージョン2系列最新版にしたら解決
        $ pip install 'canvasapi>=2,<3'
        ・canvasapiを2.1.0に更新したら解決した
        $ pip install canvasapi --upgrade # 最新版をインストール
        raise Conflict(response.text)
        canvasapi.exceptions.Conflict: {"status":"conflict","message":"report is already being generated"}
        """
        '''
        # student_analysisがあれば削除する
        for xqr in Quiz.get_all_quiz_reports():
            if xqr.report_type == 'student_analysis':
                print(f'Delete Quiz Report: Quiz:{Quiz.id}, Report:{xqr.id}')
                pprint(xqr)
                xqr.abort_or_delete()
        '''
        qr = get_report(qz)
        while ('file' in dir(qr)) == False:
            time.sleep(0.2)
        print(qr.file['display_name'])
        print(qr.file['url'])
        report_data = requests.get(qr.file['url']).content
        dist_path = os.path.normpath(DIST_PATH)
        with open(os.path.join(dist_path,
            f'{qr.id}-{qr.file["display_name"]}') ,mode='wb') as f:
            f.write(report_data)


if __name__ == '__main__':
    main()
