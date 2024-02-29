#!/usr/bin/env python3
# coding: utf-8

''' TODO
図表番号を改訂
'''

DEBUG_SKIP = ['MSA', 'ShA']

import re, sys, os, csv, glob, inspect, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bs4 import BeautifulSoup
# from copy import deepcopy

from canvasapi import Canvas
from canvasapi.util import combine_kwargs
from sol import *

from pprint import pprint

CHAPTERS = [ 10, ]

CSV_DIST_PATH = './SOL_基礎分子生物学/ECB5の問題毎の学修目標'

TB_HTML_PATH = "./ECB5 instructor resources/ECB5 Test Bank/ECB5_TB_Chapters {ch:0=2}_filtered.html"
TB_IMG_FOLDER_PATH = "./ECB5 instructor resources/ECB5 Test Bank/ECB5_TB_Chapters {ch:0=2}_filtered.fld"

API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = ""

COURSE_ID = 5282  #  2022 基礎分子生物学１（GIGA）
TMPL_QUIZ_ID = 2666  # バグ取り用の設定
QUIZ_TITLE = 'ECB5-{ch:0=2}-{t}'
Q_NAME_TMPL = '{t}-{ch:0=2}-{q:0=2}'
TFQ_NAME_TMPL = '{t}-{ch:0=2}-{q}'
IMG_FOLDER_NAME = '{ch:0=2}'
IMG_PARENT_FOLDER_ID = 62119  #  'course files/TestBank'
IMG_PARENT_FOLDER_PATH = 'course files/TestBank'

'''
MULTIPLE CHOICE
MULTIPLE SELECT
MATCHING
SHORT ANSWER
'''

'''
下処理
'''
TB_IMG_FOLDER_PATH.rstrip('/')

'''
書き換えテンプレート
'''
default_SQ_html = '<h2>FIX ME!</h2>'
red24 = r'<strong><span style="color: #e03e2d; font-size: 24pt;">{}</span></strong>'
'''
p.class 一覧
'Q1', 'Q',
'QS',
'ANS1', 'ANS',
'ANSSA' : 小問の正解（マッチング問題、短答問題）
'NL1', 'NL', 'NL2' : 数字箇条書き　小問（マッチング問題、短答問題）,
'NLAL' : 箇条書き（学修目標）
'UL1', 'UL', 'UL2' : マークなし箇条書き　空欄充填問題の語句リスト,
'BL1', 'BL', 'BL2' : ドット箇条書き,
'FIGN' : 図表番号
'FIGN' : 図表
'EXCFC' :
'EXCLC' :
'A' : 見出し 章番号
'CF' : 見出し 章タイトル
'C' : 見出し 学修目標の小見出し
'D' : 見出し 問題の種類
'MsoNormal' : 不明　末尾の空行に１回だけ使用
'''

''' TODO
<span class=dash>　下線
<span class=greek>
<span class=SUB>
<span class=B> 太字
'''

ignore_classes = ['Q1', 'Q', 'QS', 'ANS1', 'ANS', 'ANSSA', 'NL1', 'NL', 'NL2', 'UL1', 'UL', 'UL2', ]


def get_Q_list(ch, uploaded_files):
    '''
    引数 ch の章のクイズバンク HTML を読み込んで、BS4<p>オブジェクトをセクションごと、問題ごとに二次元リスト化して返す。
    '''
    def trim_attrs(tag):
        '''
        SOLに持ち込まない属性を削除、改訂する
        '''
        for attr in ['style', 'height', 'width']:
            if attr in tag.attrs.keys():
                del tag.attrs[attr]
        return

    def replace_tag(tag, new_tag):
        '''
        別のタグに置換する
        '''
        new_ = soup.new_tag(new_tag)
        new_.string = tag.string
        tag.replace_with(new_)
        return new_

    def is_Q_1st_p(p):
        '''
        段落が問題文第１段落なら、問題番号（int）を返す。
        そうでなければ False を返す。
        '''
        if p['class'][0] in ['Q1', 'Q']:
            n = re.match('^<p.*?>\s*(\d+)\.\s*', str(p))
            if n:
                return int(n.group(1))
        return False


    with open( TB_HTML_PATH.format(ch=ch), 'r') as f:
        whole = ''.join([l.replace('\n',' ') for l in f.readlines()])
        #print(whole)
        soup = BeautifulSoup(whole, 'html.parser')
        # 改行で単語間のスペースが省略されている場合があるので、' 'でjoinする

    #sys.exit()

    # img.src を SOL のurlに書き換え
    # img_parent_folder = TB_IMG_FOLDER_PATH.format(ch=ch).split('/')[-1]
    for img_tag in soup.findAll('img'):
        file_name = img_tag.attrs['src'].split('/')[-1]
        if file_name in uploaded_files:
            img_tag.attrs['src'] = uploaded_files[file_name]['url']
            # img_tag.attrs['src'] = uploaded_files[file_name]['preview_url']

    # Microsoft固有の span タグを通常の HTML タグに置換
    [replace_tag(tag, 'i') for tag in soup.findAll('span', class_='I')]
    [replace_tag(tag, 'b') for tag in soup.findAll('span', class_='B')]
    [replace_tag(tag, 'sub') for tag in soup.findAll('span', class_='SUB')]
    [replace_tag(tag, 'sup') for tag in soup.findAll('span', class_='SUP')]

    # 残った span タグを除去
    [tag.replaceWithChildren() for tag in soup.findAll('span')]
    # 不要な属性を削除
    [trim_attrs(tag) for tag in soup.findAll(re.compile('.*'))]
    #[tag.extract() for tag in soup(string='n')]

    '''
    セクションごと、問題ごとに<p>要素を仕分ける
    '''
    Q_list = dict(MCQ = [], Mch = [], ShA = [])
    section = False
    current_Q = None

    for p in [p for p in soup.findAll('p')]:
        txt = p.get_text().replace("\n","")
        if p['class'][0] == 'D':
            print(txt)
            if txt in ['MULTIPLE CHOICE', 'MULTIPLE SELECT']:
                section = 'MCQ'
            elif txt == 'MATCHING':
                section = 'Mch'
            elif txt == 'SHORT ANSWER':
                section = 'ShA'
            else:
                section = False
            continue

        if not section:
            continue

        n_Q = is_Q_1st_p(p)
        if n_Q:
            Q_list[section].append(dict(n = n_Q, ps = [p,]))
            current_Q = Q_list[section][-1]
        elif current_Q is not None:
            current_Q['ps'].append(p)

    return Q_list


def get_Q_bank(ch, Q_list):

    def arrange_p(p):
        '''
        <p>要素のBSオブジェクトををSOL向けに編集し、HTMLテキストを返す。
        一番外側の<p>の属性を削除
        図表番号を削除し、要確認装飾を施す
        '''
        rethtm = re.sub(r'^<p.+?>', r'<p>', str(p))
        # 図表番号サブパネル名あり
        rethtm = re.sub(r'Figure\s+\d+-\d+([A-Za-z])',
                        red24.format(r'Figure \1'), rethtm)
        # 図表番号サブパネル名なし　HTMLタグの可能性があるので、タグには入れない
        rethtm = re.sub(r'Figure\s+\d+-\d+([^a-zA-Z])',
                        red24.format(r'Figure') + r'\1', rethtm)
        return rethtm

    section = False
    # is_TF = False   # TFか（真偽問題の一部が真偽問題）
    context = None
    Q_bank = dict(MCQ = [], Mch = [], ShA = [], MSA = [], TFQ = [])


    ''' ===================================================
    Q_list['MCQ'] の処理
    =================================================== '''
    for q in Q_list['MCQ']:
        first_p = q['ps'].pop(0)
        context = 'Q'
        Q_bank['MCQ'].append(
            dict(
                t = 'MCQ',
                n = q['n'],
                Q = arrange_p(first_p),
                QS = [default_SQ_html for i in range(4)],
                COR_A = [],  # 複数回答問題もある
                A = '',
        ))
        i_SQ = -1
        current_Q = Q_bank['MCQ'][-1]
        for p in q['ps']:
            cls = p['class'][0]
            htm = arrange_p(p)

            if cls in ['Q1', 'Q']:
                if context == 'Q': # 問題文段落の２つ目以降
                    current_Q['Q'] += "\n" + htm
                elif context == 'QS': # １問に選択肢群が複数ある
                    context = 'Q'
                    # 前の選択肢群を Q に流し込む
                    for qs in current_Q['QS'][:i_SQ+1]:
                        current_Q['Q'] += "\n" + qs
                    current_Q['QS'] = [default_SQ_html for i in range(4)] # リセット
                    i_SQ = -1
                    current_Q['Q'] += "\n" + htm
            elif cls == 'QS':
                context = 'QS'
                is_first_p = re.match(r'^<p>\s*([A-Da-d])\.[^a-zA-Z0-9_]', htm )
                if is_first_p:
                    # すでに選択肢が複数あるのに a|A に戻ったら以前の選択肢を Q に流し込む
                    if (i_SQ > -1) and is_first_p.group(1) in ['a', 'A']:
                        for qs in current_Q['QS'][:i_SQ+1]:
                            current_Q['Q'] += "\n" + qs
                        current_Q['QS'] = [default_SQ_html for i in range(4)] # リセット
                        i_SQ = -1
                    i_SQ += 1
                    if i_SQ < 4:
                        current_Q['QS'][i_SQ] = htm
                    else:
                        current_Q['QS'].append(htm)
                else:
                    current_Q['QS'][i_SQ] += "\n" + htm
            elif cls in ['ANS1', 'ANS']:
                context = 'A'
                current_Q['A'] += htm
            else:
                if context in ['Q', 'A']:
                    current_Q[context] += "\n" + htm
                elif context == 'QS':
                    current_Q['QS'][i_SQ] += "\n" + htm


    def is_TFQ(p):
        '''
        引数の<p>オブジェクトが TFQ の正解（p.ANSSA）ならTrue
        非 TFQ の正解（p.ANSSA）ならFalse
        それ以外ならNoneを返す
        '''
        pat_ANSTF = r'^<p.*?>\s*[A-Za-z]\.\s+(True|False)\s*(.*)<\/p>'

        if p['class'][0] == 'ANSSA':
            if re.match(pat_ANSTF, arrange_p(p), re.I):
                return True
            else:
                return False
        else:
            return None

    def is_MSA(p):
        '''
        引数の<p>オブジェクトが MSA の正解（p.ANSSA）ならTrue
        非 MSA の正解（p.ANSSA）ならFalse
        それ以外ならNoneを返す
        '''
        _is_TFQ = is_TFQ(p)
        if _is_TFQ:
            return False
        elif _is_TFQ is None:
            return None
        pat_ANSMSA = r'^<p.*?>\s*[A-Za-z]\.[^a-zA-Z0-9_]'
        if re.match(pat_ANSMSA, arrange_p(p)):
            return True
        else:
            return False

    ''' ===================================================
    Q_list['ShA'] の処理
    =================================================== '''
    for q in Q_list['ShA']:
        '''
        問題のサブタイプを判定
            ShA: 単答
            MSA: 複数の小問からなる
            TFQ: 真偽問題
        '''
        subtype = 'ShA'  #  'ShA', 'MSA', 'TFQ' のどれか
        for p in q['ps']:
            if is_TFQ(p):
                subtype = 'TFQ'
                break
            elif is_MSA(p):
                subtype = 'MSA'
                break

        '''
        第１段落を切り出して問題オブジェクトを初期化
        '''
        first_p = q['ps'].pop(0)
        # print('\nContext = {}: {}'.format(context, htm))
        context = 'Q'
        Q_bank[subtype].append(
            dict(
                t = subtype,
                n = q['n'],
                Q = arrange_p(first_p),
                QS = [], # MSA, TFQ のみ使用、要素は小問の問題文
                COR_A = [], # MSA, TFQ のみ使用、要素は小問の真偽
                A = [], # MSA, TFQ のみ使用、要素は偽の場合の説明、真の場合 ''
                C = '', # コメント
        ))
        current_Q = Q_bank[subtype][-1]

        '''
        ２段落目以降の処理

        ShA の処理
        '''
        if subtype == 'ShA':
            '''
            正解（ANS/ANS1, コンテクストC）と
            それ以外（コンテクストQからなる）
            コンテクストの推移：Q → C 終了
            '''
            for p in q['ps']:
                cls = p['class'][0]
                htm = arrange_p(p)
                if cls in ['ANS1', 'ANS']:
                    context = 'C'
                    if len(current_Q['C']):
                        current_Q['C'] += "\n" + htm
                    else:
                        current_Q['C'] += htm
                else:
                    current_Q[context] += "\n" + htm
            continue  #  次の問題 q の処理へ

        '''
        MSA, TFQ の処理
        '''
        if subtype in ['TFQ', 'MSA']:
            '''
            正解（ANS/ANS1, コンテクストC）と
            それ以外（コンテクストQからなる）
            コンテクストの推移：Q → C 終了
            '''
            print(f'\nsubtype: {subtype}')
            for p in q['ps']:
                cls = p['class'][0]
                htm = arrange_p(p)
                print(f'  context: {context}')
                print(f"  class: {cls}")
                print(f"  html: {htm}")
                if cls in ['Q1', 'Q']:
                    if context == 'Q': # 問題文段落の２つ目以降
                        current_Q['Q'] += "\n" + htm
                    elif context == 'QS': # 真偽問題の問題文（通常ありえない）
                        # if is_TF:
                        print(f'真偽問題の問題文（通常ありえない）: {current_Q}')
                        current_Q['QS'][-1] += "\n" + htm
                elif cls == 'QS':
                    #if not is_TF:
                    #    current_Q['t'] = 'TFQ'
                    #    is_TF == True
                    #    current_Q['A'] = []
                    context = 'QS'
                    is_first_p = re.match(r'^<p>\s*([A-Za-z])\.[^a-zA-Z0-9_]', htm )
                    if is_first_p:
                        current_Q['QS'].append(htm)
                    else:
                        current_Q['QS'][-1] += "\n" + htm
                elif cls in ['ANS1', 'ANS']:
                    context = 'C'
                    if not re.match(r'^<p>\s*ANS:\s*<\/p>', htm ):
                        current_Q['C'] += htm
                elif cls == 'ANSSA':
                    context = 'A'
                    is_first_p = re.match(r'^<p>\s*([A-Za-z])\.[^a-zA-Z0-9_]', htm )
                    if is_first_p:
                        current_Q['A'].append(htm)
                    else:
                        # print(current_Q['A'])
                        if len(current_Q['A']):
                            current_Q['A'][-1] += "\n" + htm
                else:
                    if context in ['Q', 'C']:
                        current_Q[context] += "\n" + htm
                    elif context in ['QS', 'A']:
                        current_Q[context][-1] += "\n" + htm

    # 短答と真偽のバンクを分ける
    #pat_anssa = r'^<p>\s*[A-Za-z]\.\s+(True|False)\s*(.*)<\/p>'
    #Q_bank['TFQ'] = [ q for q in Q_bank['ShA'] if q['t'] == 'TFQ' and len(q['A'])]
    #Q_bank['TFQ'] = [ q for q in Q_bank['TFQ'] if re.match(pat_anssa, q['A'][0], re.I)]
    #Q_bank['ShA'] = [ q for q in Q_bank['ShA'] if q['t'] == 'ShA']


    '''
    整形
    '''
    '''
    for q in mcq_bank:
        for t, c in q.items():
            if t == 'QS':
                for qs in c:
                    print("QS: {}".format(qs))
            else:
                print("{}:  {}".format(t, c))
    '''

    print(' ')
    for q in Q_bank['MCQ']:
        print('\n整形中: 多選択肢問題')
        print(f"\n  q['Q']: {q['Q']}")
        print(f"\n  q['QS']: {q['QS']}")
        print(f"\n  q['A']: {q['A']}")
        # 問題番号を削除
        q['Q'] = re.sub(r'^<p>\s*\d+\.\s*', r'<p>', q['Q'])
        # 選択肢番号を削除
        q['QS'] = [re.sub(r'^<p>\s*[A-Da-d]\.\s*', r'<p>', qs ) for qs in q['QS']]
        # print('  解答原文: {}'.format(q['A']))
        # 正解を削除して、COR_Aに追加
        # [A-Da-d] が最低1つは含まれる
        pat_cap = r'^<p>\s*ANS:\s*([A-Da-d],*\s*[B-Db-d]*,*\s*[CDcd]*,*\s*?[Dd]*)[^a-zA-Z0-9_]'
        pat_rep = r'^<p>\s*ANS:\s*[A-Da-d],*\s*[B-Db-d]*,*\s*[CDcd]*,*\s*?[Dd]*([^a-zA-Z0-9_])'
        rep_txt = r'<p>\1'
        q['COR_A'] = [a.strip().upper() for a in re.findall(pat_cap, q['A'])[0].split(',')]
        print('  正解: {}'.format(q['COR_A']))
        q['A'] = re.sub(pat_rep, rep_txt, q['A'])
        # 空の段落を削除
        q['Q'] = re.sub(r'<p><\/p>', r'', q['Q'])
        q['A'] = re.sub(r'<p><\/p>', r'', q['A'])
        q['QS'] = [re.sub(r'<p><\/p>', r'', qs ) for qs in q['QS']]

    print(' ')
    for q in Q_bank['ShA']:
        print('整形中: 短答問題')
        # 問題番号を削除
        q['Q'] = re.sub(r'^<p>\s*\d+\.\s*', r'<p>', q['Q'])
        print('  解答原文: {}'.format(q['C']))
        # 空の段落を削除
        q['Q'] = re.sub(r'<p><\/p>', r'', q['Q'])
        q['C'] = re.sub(r'<p><\/p>', r'', q['C'])

    print(' ')
    for q in Q_bank['TFQ']:
        print('整形中: 真偽問題')
        # 問題番号を削除
        q['Q'] = re.sub(r'^<p>\s*\d+\.\s*', r'<p>', q['Q'])

        if len(q['QS']) != len(q['A']):
            print("TFQ Q{} ERROR: 問題数が合致しません".format(q['n']))
            print(f"q['QS'] = {len(q['QS'])}     q['A'] = {len(q['QS'])}")
            print(q)
            print("処理を中止します")
            sys.exit()

        # 問題番号 例：12A
        pat_qs = r'^<p>\s*([A-Za-z])\.[^a-zA-Z0-9_]'
        q['n'] = ['{:0=2}{}'.format(q['n'], re.match(pat_qs, qs).group(1))
                    for qs in q['QS']]
        # 選択肢番号を削除
        q['QS'] = [re.sub(r'^<p>\s*[A-Za-z]\.\s*', r'<p>', qs ) for qs in q['QS']]
        [print('  小問題文: {}'.format(a)) for a in q['A']]
        # 正解を削除して、COR_Aに追加
        pat_anssa = r'^<p>\s*[A-Za-z]\.\s+(True|False|true|false)\s*(.*)<\/p>'
        rep_anssa = r'<p>\2'
        q['COR_A'] = [(re.match(pat_anssa, a).group(1).lower() == 'true')
                        for a in q['A']]
        print('  正解: {}'.format(q['COR_A']))
        q['A'] = [re.sub(pat_anssa, rep_anssa, a) for a in q['A']]
        # 空の段落を削除
        q['Q'] = re.sub(r'<p><\/p>', r'', q['Q'])
        q['C'] = re.sub(r'<p><\/p>', r'', q['C'])
        q['QS'] = [re.sub(r'<p><\/p>', r'', qs ) for qs in q['QS']]
        q['A'] = [re.sub(r'<p><\/p>', r'', a ) for a in q['A']]

    print(' ')
    for q in Q_bank['MSA']:
        if 'MSA' in DEBUG_SKIP:
            print('DEBUG_SKIP (MSA): 複数の小問からなる短答問題の整形処理をスキップ')
            break

        print('整形中: 複数の小問からなる短答問題')
        # 問題番号を削除
        q['Q'] = re.sub(r'^<p>\s*\d+\.\s*', r'<p>', q['Q'])

        if len(q['QS']) != len(q['A']):
            print("TFQ Q{} ERROR: 問題数が合致しません".format(q['n']))
            print(q)
            print("処理を中止します")
            sys.exit()

        # 問題番号 １つ目の要素がゼロ埋め数字、２つ目以降が小問ラベル
        q['n'] = ['{:0=2}'.format(q['n']),]
        pat_qs = r'^<p>\s*([A-Za-z])\.[^a-zA-Z0-9_]'
        q['n'] += [re.match(pat_qs, qs).group(1) for qs in q['QS']]
        # 選択肢番号を削除
        q['QS'] = [re.sub(r'^<p>\s*[A-Za-z]\.\s*', r'<p>', qs ) for qs in q['QS']]
        q['A'] = [re.sub(r'^<p>\s*[A-Za-z]\.\s*', r'<p>', qs ) for a in q['A']]
        # 空の段落を削除
        q['Q'] = re.sub(r'<p><\/p>', r'', q['Q'])
        q['C'] = re.sub(r'<p><\/p>', r'', q['C'])
        q['QS'] = [re.sub(r'<p><\/p>', r'', qs ) for qs in q['QS']]
        q['A'] = [re.sub(r'<p><\/p>', r'', a ) for a in q['A']]

    '''
    テストプリント
    '''
    for q in Q_bank['MCQ']:
        for t, c in q.items():
            if t == 'QS':
                for qs in c:
                    print("QS: {}".format(qs))
            else:
                print("{}:  {}".format(t, c))

    return Q_bank
# END: def get_Q_bank(ch):


def upload_image_files(the_course, ch):
    '''
    イメージファイルを IMG_PARENT_FOLDER_PATH/IMG_FOLDER_NAME 以下にアップロード
    '''
    # イメージファイル格納フォルダを作成
    #[print('Folder ID: {},    Name: {},    Parent: {}'.format(f.id, f.name, f.parent_folder_id)) for f in the_course.get_folders()]
    kwargs=dict(parent_folder_path=IMG_PARENT_FOLDER_PATH)
    folder = the_course.create_folder(IMG_FOLDER_NAME.format(ch=ch), **kwargs)
    print('フォルダ: {}'.format(folder.full_name))
    # sys.exit()
    files = glob.glob("{}/*".format(TB_IMG_FOLDER_PATH.format(ch=ch)))
    upload_results = [folder.upload(f) for f in files]
    uploaded_files = {u[1]['display_name'] : u[1] for u in upload_results if u[0]}
    pprint(uploaded_files)
    #sys.exit()
    return uploaded_files


def create_ch_quizzes(the_course, ch, Q_bank):

    new_quiz = {}

    '''
    Quiz（問題集）をつくる
    '''
    for t in ['MCQ', 'Mch', 'ShA', 'TFQ', 'MSA']:
        if len(Q_bank[t]):
            new_quiz[t] = the_course.create_quiz( dict(
                course_id=COURSE_ID,
                title=QUIZ_TITLE.format(ch=ch, t=t),
                quiz_type='assignment',
                time_limit=None,
                timer_autosubmit_disabled=False,
                shuffle_answers=False,
                show_correct_answers=False,
                scoring_policy='keep_highest',
                allowed_attempts=1,
                one_question_at_a_time=False,
                question_count=0,
                points_possible=None,
                cant_go_back=False,
                access_code=None,
                ip_filter=None,
                due_at=None,
                lock_at=None,
                unlock_at=None,
                published=False,
                unpublishable=True,
                hide_results='always',
                show_correct_answers_at=None,
                hide_correct_answers_at=None,
                can_unpublish=True,
                can_update=True,
                require_lockdown_browser=False,
                require_lockdown_browser_for_results=False,
                require_lockdown_browser_monitor=False,
                lockdown_browser_monitor_data=None,
                speed_grader_url=None,
                one_time_results=False,
                only_visible_to_overrides=False,
                show_correct_answers_last_attempt=False,
                anonymous_submissions=False,
            ))


    for q in Q_bank['MCQ']:
        print("MCQ Q{}: 処理中".format(q['n']))
        if len(q['COR_A']) == 1:
            question_type = 'multiple_choice_question'
        elif len(q['COR_A']) >= 2:
            question_type = 'multiple_answers_question'
        else:
            print("Q{} ERROR: 正解が設定されていません".format(q['n']))
            sys.exit()

        if  len(q['QS']) > 4:
            print("Q{} ERROR: 選択肢数={}".format(q['n'], len(q['QS'])))
            sys.exit()

        new_question_kwargs = dict( question = dict(
            question_name = Q_NAME_TMPL.format(t=q['t'], ch=ch, q=q['n']),
            question_text = q['Q'],
            question_type = question_type,
            points_possible = 1.0,
            neutral_comments_html = q['A'],
            answers = [
                dict(
                    html = q['QS'][0],
                    weight = (100.0 if 'A' in q['COR_A'] else 0.0)
                ),
                dict(
                    html = q['QS'][1],
                    weight = (100.0 if 'B' in q['COR_A'] else 0.0)
                ),
                dict(
                    html = q['QS'][2],
                    weight = (100.0 if 'C' in q['COR_A'] else 0.0)
                ),
                dict(
                    html = q['QS'][3],
                    weight = (100.0 if 'D' in q['COR_A'] else 0.0)
                ),
            ],
        ))
        # multiple_answers_question の場合、選択肢に HTML が指定できない。たぶんバグ。
        for a in new_question_kwargs['question']['answers']:
            if new_question_kwargs['question']['question_type'] == 'multiple_answers_question':
                a['text'] = a.pop('html')

        pprint(combine_kwargs(**new_question_kwargs))
        new_quiz['MCQ'].create_question(**new_question_kwargs)


    for q in Q_bank['ShA']:
        print("ShA Q{}: 処理中".format(q['n']))

        new_question_kwargs = dict( question = dict(
            question_name = Q_NAME_TMPL.format(t=q['t'], ch=ch, q=q['n']),
            question_text = q['Q'],
            question_type = 'essay_question',
            points_possible = 1.0,
            neutral_comments_html = q['C'],
        ))

        pprint(combine_kwargs(**new_question_kwargs))
        new_quiz['ShA'].create_question(**new_question_kwargs)


    for q in Q_bank['TFQ']:
        for n, qs, cor_a, a \
            in zip(q['n'], q['QS'], q['COR_A'], q['A']):
            # Python 3.10以降なら引数 strict を使える
            # in zip(q['n'], q['QS'], q['COR_A'], q['A'], strict=True):

            new_question_kwargs = dict( question = dict(
                question_name = TFQ_NAME_TMPL.format(t=q['t'], ch=ch, q=n),
                question_text = qs,
                question_type = 'true_false_question',
                points_possible = 1.0,
                neutral_comments_html = a + "\n" + q['C'],
                answers = [
                    dict(
                        text = 'True',
                        weight = (100.0 if cor_a else 0.0)
                    ),
                    dict(
                        text = 'False',
                        weight = (0.0 if cor_a else 100.0)
                    ),
                ],
            ))

            pprint(combine_kwargs(**new_question_kwargs))
            new_quiz['TFQ'].create_question(**new_question_kwargs)


    for q in Q_bank['MSA']:
        if 'MSA' in DEBUG_SKIP:
            print('DEBUG_SKIP (MSA): 複数の小問からなる短答問題のQuiz作成処理をスキップ')
            break
        # 最初に問題文のテキストをつくる
        # q['n'] 問題番号 １つ目の要素がゼロ埋め数字、２つ目以降が小問ラベル
        n_Q = q['n'].pop(0)
        new_question_kwargs = dict( question = dict(
            question_name = TFQ_NAME_TMPL.format(t=q['t'], ch=ch, q=n_Q),
            question_text = q['Q'],
            question_type = 'text_only_question',
            points_possible = 0.0,
            neutral_comments_html = q['C'],
        ))
        pprint(combine_kwargs(**new_question_kwargs))
        new_quiz['MSA'].create_question(**new_question_kwargs)

        for n, qs, a \
            in zip(q['n'], q['QS'], q['A']):
            # Python 3.10以降なら引数 strict を使える
            # in zip(q['n'], q['QS'], q['COR_A'], q['A'], strict=True):

            new_question_kwargs = dict( question = dict(
                question_name = TFQ_NAME_TMPL.format(t=q['t'], ch=ch, q=(n_Q+n)),
                question_text = qs,
                question_type = 'essay_question',
                points_possible = 1.0,
                neutral_comments_html = a + "\n" + q['C'],
            ))

            pprint(combine_kwargs(**new_question_kwargs))
            new_quiz['MSA'].create_question(**new_question_kwargs)

    return [quiz.id for quiz in new_quiz.values()]

# END: def create_ch_quizzes(the_coursem, ch):


def save_question_objectives(the_course, Quiz_ids):
    '''
    Questionの学修目標をCSVに出力する
    '''
    for Quiz_id in Quiz_ids:
        Quiz = the_course.get_quiz(Quiz_id)
        question_list = [['タイプ', '問題番号', '選択肢', '難易度', '範囲', '学修目標']]
        question_csv = []
        for Q in Quiz.get_questions():
            Qname_split = Q.question_name.split('-')
            Qnumber = re.search(r'^(?P<n>\d+)(?P<o>[A-z]*)$', Qname_split[2])
            # print(f'  Qname_split[2] : {Qname_split[2]}')
            if Qnumber.group('o') in ['', 'A']:
                if len(question_csv):
                    question_list.append(question_csv)
                    question_csv = []
                neutral_com = BeautifulSoup(Q.neutral_comments_html, 'html.parser').get_text().strip()
                print(f'\n{Q.question_name}:')
                question_csv = [Qname_split[0], Qnumber.group('n'), Qnumber.group('o')]
                m = re.search(r'DIF:\s+(?P<DIF>.+?)\s+REF:\s+(?P<REF>.+?)\s+OBJ:', neutral_com)
                question_csv.append(m.group('DIF'))
                question_csv.append(m.group('REF'))
                print(f'  DIF: {m.group("DIF")}\n  REF: {m.group("REF")}')

                obj = []
                for m in re.finditer(r'(?:OBJ:|\|)\s*(?P<OBJ>\d+\.\d+\.[a-z]+)\s', neutral_com):
                    obj.append(m.group('OBJ'))
                    print(f'  OBJ: {m.group("OBJ")}')
                question_csv.append('&'.join(obj))
            else:
                question_csv[2] += Qnumber.group('o')

            if question_csv[2] == '':
                question_list.append(question_csv)
                question_csv = []

        if len(question_csv):
            question_list.append(question_csv)

        dist_path = os.path.normpath(CSV_DIST_PATH)

        with open(os.path.join(dist_path, f'{Quiz.id}_{Quiz.title}.csv'), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows( question_list )


def main():
    #################################################
    # 授業 （Course object） を取得
    #################################################

    canvas = Canvas(API_URL, API_KEY)
    the_course = get_course(canvas, COURSE_ID)

    '''
    オブジェクトの内容確認のためのコード
    '''
    # tmp_quiz = the_course.get_quiz(TMPL_QUIZ_ID)
    # pprint( tmp_quiz )
    # [pprint( Qn ) for Qn in tmp_quiz.get_questions()]

    # tmp_quiz = the_course.get_quiz(4459)
    # [pprint( Qn ) for Qn in tmp_quiz.get_questions()]
    """
    MCB4_21 = {
        #4461:[1526,1527,1528,1529,1530,1534,1535,1536,1537,1538,
        #    1539,1540,1541,1542,1543],
        #4459:[1329,1330,1331,1332,1333,1337,1338,1339,1340,1341,
        #    1342,1343,1344,1345,1346],
        4459:[1330,]
    }
    for cid, qid_ls in MCB4_21.items():
        c = get_course(canvas, cid)
        for qid in qid_ls:
            '''
            [print('\n{}: {}'.format(Qn.question_name, Qn.question_type))
                for Qn in c.get_quiz(qid).get_questions()
                if Qn.question_type not in
                    ['multiple_choice_question', 'multiple_answers_question']]
            '''
            [pprint(Qn) for Qn in c.get_quiz(qid).get_questions()
                if Qn.question_name == 'K8-09-29']
    """
    # sys.exit()

    for ch in CHAPTERS:
        uploaded_files = upload_image_files(the_course, ch)
        Q_list = get_Q_list(ch, uploaded_files)
        Q_bank = get_Q_bank(ch, Q_list)
        Quiz_ids = create_ch_quizzes(the_course, ch, Q_bank)
        save_question_objectives(the_course, Quiz_ids)

if __name__ == '__main__':
    main()
