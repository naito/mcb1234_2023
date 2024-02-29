#!/usr/bin/env python3
# coding: utf-8

import sys, os, argparse, re, urllib.request, csv, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from copy import deepcopy

from canvasapi import Canvas
from canvasapi.util import combine_kwargs
from sol import *

import pandas as pd

from pprint import pprint


def get_args():
    parser = argparse.ArgumentParser(
        description = '''小テストの結果をアナウンスする。複数のクイズ（例：日本語科目とGIGA科目の同じ試験）の合計をアナウンスできる。'''
    )
    parser.add_argument('urls', nargs='*',
        help='集計対象のクイズのURL（複数可）複数指定するとすべてのクイズを合わせた統計が示される'
    )
    parser.add_argument('-s', '--silent', action='store_true',
        help='ユーザーに科目名、アナウンス内容の確認を求めず、自動的に実行する'
    )

    return parser.parse_args()

args = get_args()


create_kwargs_tmpl = dict(
    published = True,
    delayed_post_at = None,
    is_announcement = True,
)

kwargs_title_tmpl = dict(
    j = '{title} の結果',
    e = 'Results of {title}',
)
kwargs_message_tmpl = dict(
    j = '''<p>{title} の結果が確認できるようになっています。</p>
        <p>{sum}概要は以下の通りでした。</p>
        <p>&nbsp;</p>
        <p>　受験者数：{n_examinee}人</p>
        <p>　最高正解数：{highscore}問（30問中）</p>
        <p>　25問以上正解した人数：{n_geq25}人</p>''',
    e = '''<p>The summary {sum}was as follows.</p>
        <p style="padding-left: 40px;">Number of examinees: {n_examinee}</p>
        <p style="padding-left: 40px;">Highest score: {highscore} (out of 30)</p>
        <p style="padding-left: 40px;">Number of examinees who got at least 25: {n_geq25}</p>''',
)
kwargs_message_sum = dict(
    j = '日本語科目、GIGA科目を合わせての',
    e = '(sum of GIGA and non-GIGA courses) '
)


def get_stats(qz_info):
    '''
    受験者数、ハイスコア、25問以上正解した人数の合計を返す
    '''
    n_examinee = 0
    highscore = 0
    n_geq25 = 0
    for qi in qz_info:
        qz = get_course(canvas, qi['cid']).get_quiz(qi['qid'])
        qz_report = qz.create_report('student_analysis', kwargs=dict(include=['file'],))

        # ファイルの生成には時間がかかるので、できるまで待つ。
        while True:
            if hasattr(qz_report, 'file'):
                break
            else:
                time.sleep(0.5)
                qz_report = qz.get_quiz_report(qz_report.id)

        qz_report_df = pd.read_csv(qz_report.file['url'])
        # デバッグ用、レポートのない状態に戻す
        # qz_report.abort_or_delete()
        pprint(qz_report_df)
        n_examinee += len(qz_report_df)
        for score_str in ['正解数', 'n correct']:
            if score_str in qz_report_df.keys():
                highscore = max([highscore, qz_report_df[score_str].max()])
                n_geq25 += (qz_report_df[score_str] >= 25).sum()
                break

    sum = kwargs_message_sum if len(qz_info) > 1 else dict(j='', e='')
    return dict(
        n_examinee = n_examinee,
        highscore = highscore,
        n_geq25 = n_geq25,
        sum = sum,
    )


def create_announcement(qi, stats):
    c = get_course(canvas, qi['cid'])
    lang = 'e' if is_giga(c) else 'j'

    format_str = deepcopy(stats)
    format_str['title'] = c.get_quiz(qi['qid']).title
    format_str['sum'] = stats['sum'][lang]

    kwargs = create_kwargs_tmpl
    kwargs['title'] = kwargs_title_tmpl[lang].format(**format_str)
    kwargs['message'] = kwargs_message_tmpl[lang].format(**format_str)

    if not args.silent:
        # 確認
        print('科目：{}'.format(c.name))
        print(kwargs['title'] + "\n")
        print(kwargs['message'])
        confirm = None
        while confirm not in ['','y','n']:
            confirm = input('この内容でアナウンスしますか？（[y],n）: ')
        if confirm == 'n':
            sys.exit()

    c.create_discussion_topic(**kwargs)


def main():
    qz_info = [parse_quiz_url(u, args.silent) for u in args.urls]
    # pprint(qz_info)

    stats = get_stats(qz_info)
    print('受験者数: {}'.format(stats['n_examinee']))
    print('ハイスコア: {}'.format(stats['highscore']))
    print('25問以上正解: {}'.format(stats['n_geq25']))

    for qi in qz_info:
        create_announcement(qi, stats)

    # sys.exit()


if __name__ == '__main__':
    main()
