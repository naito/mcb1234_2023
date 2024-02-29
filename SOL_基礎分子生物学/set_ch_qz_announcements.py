#!/usr/bin/env python3
# coding: utf-8

import re, sys, os, datetime, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bs4 import BeautifulSoup
# from copy import deepcopy

from canvasapi import Canvas
from canvasapi.util import combine_kwargs
from sol import *

from pprint import pprint


def get_args():
    parser = argparse.ArgumentParser(
        description = '''小テスト終了当日に自動配信するアナウンスを登録する。コースIDを指定するだけで、その時点で小テスト（Chapter Quiz）に登録されており、ロック日時が設定されているすべてのクイズに対するアナウンスが登録される。'''
    )

    return parser.parse_args()

args = get_args()


COURSE_ID = [ # 4458,  #  2021 基礎分子生物学３
              4459,  #  2021 基礎分子生物学４
              # 4460,  #  2021 基礎分子生物学３（GIGA）
              4461,  #  2021 基礎分子生物学４（GIGA）
            ]

target_assignment_groups = ['小テスト', 'Chapter Quiz']

create_kwargs_tmpl = dict(
    title = dict(
        j = '{title}の試験期間は本日（{d}）までです。',
        e = 'The Exam Period for the {title} ends today ({d}).',
    ),
    message = dict(
        j = '<p><a title="{title}" href="https://sol.sfc.keio.ac.jp/courses/{cid}/quizzes/{qid}" data-api-endpoint="https://sol.sfc.keio.ac.jp/api/v1/courses/{cid}/quizzes/{qid}" data-api-returntype="Quiz">{title}</a>の試験期間は本日（{d}）までです。</p>',
        e = '<p>The Exam Period for the <a title="{title}" href="https://sol.sfc.keio.ac.jp/courses/{cid}/quizzes/{qid}" data-api-endpoint="https://sol.sfc.keio.ac.jp/api/v1/courses/{cid}/quizzes/{qid}" data-api-returntype="Quiz">{title}</a>  ends today ({d}).</p>',
    ),
    published = True,
    delayed_post_at = None,
    is_announcement = True,
)


def get_quiz_info_list(course):
    '''
    course: コースオブジェクト
    cid: コースid
    lock_at（締切）の設定があるクイズの id, title, lock_at の値のリストを返す
    2021-11-02T14:59:00Z
    '''
    agid_ls = [ag.id for ag in course.get_assignment_groups()
                if ag.name in target_assignment_groups]
    ret_ls = []
    for qz in course.get_quizzes():
        # pprint(qz)
        if qz.lock_at and (qz.assignment_group_id in agid_ls):
            ret_ls.append(dict(
                id = qz.id,
                title = qz.title,
                lock_at = qz.lock_at,
            ))
    return ret_ls


def format_date(datetime_str_sol, lang):
    date_jst = from_iso_to_jst(datetime_str_sol).date()

    if lang == 'j':
        return '{}月{}日'.format(date_jst.month, date_jst.day)
    elif lang == 'e':
        return '{}. {}'.format(date_jst.strftime('%b'), date_jst.day)


def delayed_post_datetime_str(datetime_str_sol):
    '''
    クイズがロックされる日時のisoフォーマット文字列から、
    当日午前０時のisoフォーマット文字列を得る。
    '''
    datetime_jst = from_iso_to_jst(datetime_str_sol)
    datetime_jst = datetime_jst.replace(hour = 0, minute = 0, second = 0)
    return datetime_jst.isoformat(timespec = 'seconds')


def create_announcement(course, quiz_info):
    '''
    クイズロック当日のアナウンスを登録する
    '''
    lang = 'e' if is_giga(course) else 'j'
    date_str = format_date(quiz_info['lock_at'], lang)

    kwargs = dict(
        title = create_kwargs_tmpl['title'][lang].format(
                    title = quiz_info['title'],
                    d = date_str),
        message = create_kwargs_tmpl['message'][lang].format(
            title = quiz_info['title'],
            d = date_str, cid = course.id, qid = quiz_info['id'] ),
        published = True,
        delayed_post_at = delayed_post_datetime_str(quiz_info['lock_at']),
        is_announcement = True,
    )

    course.create_discussion_topic(**kwargs)


def main():
    #################################################
    # 授業 （Course object） を取得
    #################################################

    # the_course = get_course(canvas, COURSE_ID)

    '''
    オブジェクトの内容確認のためのコード
    '''
    # kwargs = dict(latest_only = False, start_date = '2021-10-01', end_date = '2021-11-27')
    for cid in COURSE_ID:
        #for a in canvas.get_announcements(["course_{}".format(cid)], **kwargs):
        #    pprint(a)
        #for qz in get_course(canvas, cid).get_quizzes():
        #    pprint(qz)
        c = get_course(canvas, cid)
        for qz_info in get_quiz_info_list(c):
            create_announcement(c, qz_info)

    # sys.exit()


if __name__ == '__main__':
    main()
