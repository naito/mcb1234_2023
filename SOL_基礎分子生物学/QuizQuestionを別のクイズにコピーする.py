#!/usr/bin/env python3
# coding: utf-8

import sys, os, csv, json, glob, inspect, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from canvasapi import Canvas
from sol import *

from pprint import pprint


def get_args():
    parser = argparse.ArgumentParser(
        description = '''任意のクイズの問題を、既存の別のクイズにコピーする'''
    )
    parser.add_argument('src_url',
        help='コピー元のクイズのURL'
    )
    parser.add_argument('dist_url',
        help='コピー先のクイズのURL'
    )
    parser.add_argument('-g', '--groups_re',
        help='コピー対象のグループ名の正規表現。省略するとすべてのグループをコピーする。'
    )
    parser.add_argument('-s', '--silent', action='store_true',
        help='ユーザーに確認を求めず、自動的に実行する'
    )

    return parser.parse_args()

args = get_args()


def main():
    ids_src = parse_quiz_url(args.src_url, True)
    ids_dist = parse_quiz_url(args.dist_url, True)

    c_src = get_course(canvas, ids_src['cid'])
    c_dist = get_course(canvas, ids_dist['cid'])

    qz_src = c_src.get_quiz(ids_src['qid'])
    qz_dist = c_dist.get_quiz(ids_dist['qid'])

    if not args.silent:
        # 確認
        print('■ コピー元')
        print('　科　目：{}'.format(c_src.name_with_memo))
        print('　クイズ：{}'.format(qz_src.title))
        print('■ コピー先')
        print('　科　目：{}'.format(c_dist.name_with_memo))
        print('　クイズ：{}'.format(qz_dist.title))
        confirm = None
        while confirm not in ['','y','n']:
            confirm = input('コピー元とコピー先の科目、クイズ名は正しいですか？（[y],n）: ')
        if confirm == 'n':
            sys.exit()

    # コピー対象のグループ名のパターンをコンパイル
    if args.groups_re:
        group_name_pattern = re.compile(args.groups_re)
    else:
        group_name_pattern = re.compile(r'^.+$')

    #グループの複製（クズグループに属さない問題の属性quiz_group_idは、None）
    group_id_list = list(set(
        [ q.quiz_group_id for q in get_questions(qz_src) if q.quiz_group_id is not None]
    ))
    # print(group_id_list); sys.exit()
    gid_map = dict()  #  キー: コピー元グループID, 値: コピー先グループID
    for gid in group_id_list:
        qg = qz_src.get_quiz_group(gid)
        if group_name_pattern.match(qg.name):
            qg_dict = dict_from_object(qg, quiz_groups_attr_list)
            qg_copy = qz_dist.create_question_group([qg_dict,])
            if not args.silent:
                # 確認
                print('問題グループ：{}'.format(qg.name))
                confirm = None
                while confirm not in ['','y','n']:
                    confirm = input('この問題グループをコピーしますか？（[y],n）: ')
                if confirm == 'n':
                    continue
            gid_map[gid] = qg_copy.id

    #問題の複製
    for qq in get_questions(qz_src):
        qq_dict = dict_from_object(qq, question_attr_list)
        if qq.quiz_group_id in gid_map.keys():
            qq_dict['quiz_group_id'] = gid_map[qq_dict['quiz_group_id']]
        qz_dist.create_question(question = qq_dict)



if __name__ == '__main__':
    main()
