#!/usr/bin/env python3
# coding: utf-8

from canvasapi import Canvas

import sys, re, datetime
from pprint import pprint


API_URL = "https://sol.sfc.keio.ac.jp"
API_KEY = ""

canvas = Canvas(API_URL, API_KEY)

"""
SOL の環境に依存する定数
"""
quiz_url_re = re.compile('https://sol.sfc.keio.ac.jp/courses/(?P<cid>\d+)/quizzes/(?P<qid>\d+)')

"""
学則など規定に基づく定数
"""
keio_grading_standard = dict(
    title = 'Keio Grading Scheme',
    grading_scheme=[
        {'name': 'S', 'value': 0.9},
        {'name': 'A', 'value': 0.8},
        {'name': 'B', 'value': 0.7},
        {'name': 'C', 'value': 0.6},
        {'name': 'D', 'value': 0}
        ])

"""
ユーザーが自由に定義できる定数
"""
first_time_question_group_tag = '未出_'


"""
稼働する Canvas LMS の仕様によって定まる定数
"""
quiz_attr_list = ['title', 'description', 'quiz_type', 'assignment_group_id',
    'time_limit', 'shuffle_answers', 'hide_results', 'show_correct_answers',
    'show_correct_answers_last_attempt', 'show_correct_answers_at',
    'hide_correct_answers_at', 'allowed_attempts', 'scoring_policy',
    'one_question_at_a_time', 'cant_go_back', 'access_code', 'ip_filter',
    'due_at', 'lock_at', 'unlock_at', 'published', 'one_time_results',
    'only_visible_to_overrides']

quiz_groups_attr_list = ['name', 'pick_count', 'question_points',
    'assessment_question_bank_id']

question_attr_list = ['question_name','question_text', 'quiz_group_id',
    'question_type', 'position', 'points_possible', 'correct_comments',
    'incorrect_comments', 'neutral_comments', 'text_after_answers', 'answers',
    'variables', 'formulas', 'answer_tolerance', 'formula_decimal_places',
    'matches', 'matching_answer_incorrect_matches']

grade_standard_attr_list = ['context_id', 'context_type', 'grading_scheme',
    'id', 'set_attributes', 'title']


def dict_from_object(obj, attr_list):
    '''
    objの属性のうち、attr_listにあるものだけを抽出した辞書オブジェクトを返す
    '''
    d = dict()
    for attr in attr_list:
        if hasattr(obj, attr):
            d[attr] = getattr(obj, attr)
    return d

def is_html(text):
    '''
    Canvasのコンテンツに保存されているテキスト text がHTMLならTrue、
    そうでなければFalseを返す
    テキスト冒頭がタグで始まっているかどうかで判定（タグで始まっていなくても、<strong>などの
    タグが入っている場合もあるが、ここでは、<p>や<div>でテキスト全体がHTMLで構造化されている
    かどうかを判定する）
    テキストがタグでない"<"で始まる場合、エスケープされているはず
    '''
    return re.match(r"<[^>]*>", text) is not None


def get_course(canvas, course_id):
    '''
    course_idからCourseオブジェクトを取得する。
    失敗するとFalseを返す。
    '''
    for c in canvas.get_courses():
        if c.id == course_id:
            return c

    print('Course ID {} not found'.format( course_id ))
    return False


def get_course_by_id(canvas, course_id):
    '''
    get_course()のエイリアス
    course_idからCourseオブジェクトを取得する。
    失敗するとFalseを返す。
    '''
    return get_course(canvas, course_id)


def get_courses_by_name_forward_match(canvas, course_name):
    '''
    文字列 course_name に前方一致でヒットする科目の
    Courseオブジェクトのリストを取得する。
    該当する科目がない場合、Noneを返す。
    '''
    r = []
    for c in canvas.get_courses():
        if c.name.startswith(course_name):
            r.append(c)

    if len(r):
        return r
    else:
        return None


def get_quizzes_by_name_forward_match(course, quiz_name):
    '''
    文字列 quiz_name に前方一致でヒットする科目の
    Quiz オブジェクトのリストを取得する。
    該当する科目がない場合、Noneを返す。
    '''
    r = []
    for qz in course.get_quizzes():
        if qz.title.startswith(quiz_name):
            r.append(qz)

    if len(r):
        return r
    else:
        return None


def is_giga(course_obj):
    '''
    course_obj: コースオブジェクト
    GIGA科目なら True, でなければ False を返す
    '''
    if re.search(r'[^a-zA-Z0-9]GIGA[^a-zA-Z0-9]', course_obj.name_with_memo):
        # name_with_memo=基礎分子生物学３ / MOLECULAR AND CELLULAR BIOLOGY 3 (GIGA/GG/GI),
        return True
    else:
        return False


def fix_QuizQuestion(QQ_obj):
    '''
    QuizQuestionオブジェクトを修復する
    * 'numerical_question' の 'answers' のキーの誤り
        （誤） exact →（正） answer_exact
        （誤） margin →（正） answer_error_margin
    '''
    answer_key_erratum = dict(
        numerical_question = dict(
            exact = 'answer_exact',
            margin = 'answer_error_margin',
            start = 'answer_range_start',
            end = 'answer_range_end',
            approximate = 'answer_approximate',
            precision = 'answer_precision',
        ),
        multiple_dropdowns_question = dict(
            weight = 'answer_weight',
        ),
    )
    for qt in answer_key_erratum:
        if QQ_obj.question_type == qt:
            for answer in QQ_obj.answers:  #  listオブジェクト、要素はdict
                for attr in [a for a in answer if (a in answer_key_erratum[qt])]:
                    answer[answer_key_erratum[qt][attr]] = answer.pop(attr)

    return QQ_obj


def get_question(Quiz_obj, question, **kwargs):
    '''
    Quiz_obj.get_question(question, **kwargs) の代わりに使う
    バグを修復したQuizQuestionオブジェクトを返す
    '''
    QQ_obj = Quiz_obj.get_question(question, **kwargs)
    return fix_QuizQuestion(QQ_obj)


def get_questions(Quiz_obj, **kwargs):
    '''
    Quiz_obj.get_questions(**kwargs) の代わりに使う
    バグを修復したQuizQuestionオブジェクトのPaginatedListを返す
    '''
    QQ_obj_list = Quiz_obj.get_questions(**kwargs)
    for QQ_obj in QQ_obj_list:
        fix_QuizQuestion(QQ_obj)
    return QQ_obj_list

pat_isoZ = re.compile(r'(\d\d\d\d-[01]\d-[0-3]\dT[012]\d:[0-5]\d:[0-5]\d)Z')
tz_here = datetime.datetime.now().tzinfo

def from_iso_to_jst(datetime_str_sol):
    '''
    SOLの日時文字列からJSTのdatatimeオブジェクトを返す
    Python3.8の datetime.fromisoformat() は、時間帯を 'Z' とする表記に未対応なので対処する
    '''
    iso_str = pat_isoZ.sub(r'\1+00:00', datetime_str_sol)
    the_datetime = datetime.datetime.fromisoformat(iso_str)
    return the_datetime.astimezone(tz_here)

def get_ay_semester_by_datetime(dt):
    '''
    datetime.datetimeオブジェクト dt から辞書 dict(AY, semester) を返す。
      AY : int (年度)
      semester : str ('spring' or 'fall')
    学部学則25条に学期が定義されている。
    春学期は４月１日〜９月21日、秋学期は９月22日〜翌年３月31日
    '''
    if dt.month <= 3:
        return dict(AY = dt.year - 1, semester = 'fall')
    elif dt.month <= 8:
        return dict(AY = dt.year, semester = 'spring')
    elif dt.month == 9 and dt.day <= 21:
        return dict(AY = dt.year, semester = 'spring')
    else:
        return dict(AY = dt.year, semester = 'fall')

def get_course_ay_semester(course = None):
    '''
    Courseオブジェクト course から辞書 dict(AY, semester) を返す。
      AY : int (年度)
      semester : str ('spring' or 'fall')
    Courseオブジェクトの created_at 属性に基づいて決める。
    経験則で、春学期科目は３月上旬、秋学期科目は９月上旬に作成されている。
    12〜５月に作成された科目を春学期科目、６〜11月に作成された科目を秋学期科目と判定する。
    '''
    created_datetime = from_iso_to_jst(course.created_at)
    if created_datetime.month <= 5:
        return dict(AY = created_datetime.year, semester = 'spring')
    elif created_datetime.month <= 11:
        return dict(AY = created_datetime.year, semester = 'fall')
    else:
        return dict(AY = created_datetime.year + 1, semester = 'spring')

def is_current_course(course):
    '''
    Courseオブジェクト course の作成年度学期が現在であれば True を
    そうでなければ False を返す
    '''
    return True if get_ay_semester_by_datetime(datetime.datetime.now()) == \
                   get_course_ay_semester(course) else False

def is_first_time_question(quiz, question, first_time_group_id_list = []):
    '''
    問題 question が未出問題なら True、既出問題なら False を返す。
    問題が属する問題グループ名の冒頭が first_time_question_group_tag であれば True
    問題が問題グループに属していない場合、Noneを返す。
    first_time_group_id_list：未出問題グループのIDを要素とするリスト。処理高速化のために
      使用。不完全なリストでよい。１問題グループあたりの問題数によるが、2023年度秋学期の４科目
      の クイズ未出問題のIDリストをダウンロード.py の処理時間は20％ほど向上した。
      参照渡しなので、この関数の動作によって first_time_group_id_list の内容は更新される。
    '''
    if question.quiz_group_id is not None:
        if question.quiz_group_id in first_time_group_id_list:
            return True
        else:
            qg = quiz.get_quiz_group(question.quiz_group_id)
            if qg.name.startswith(first_time_question_group_tag):
                first_time_group_id_list.append(question.quiz_group_id)
                return True
            else:
                return False
    else:
        return None


def parse_quiz_url(an_url, is_silent=True):
    '''
    クイズのURLから、コースIDとクイズIDの辞書を返す
    '''
    m = quiz_url_re.match(an_url)
    if m is None:
        print('URLが正しくありません：{}'.format(an_url))
        sys.exit()

    cid=int(m.group('cid'))
    qid=int(m.group('qid'))
    c = get_course(canvas, cid)
    if c is None:
        print('URLが正しくありません：{}'.format(an_url))
        print('コースID {} の科目を取得できません'.format(cid))
        sys.exit()
    qz = c.get_quiz(qid)
    if qz is None:
        print('URLが正しくありません：{}'.format(an_url))
        print('クイズID {} のクイズを取得できません'.format(qid))
        sys.exit()

    if not is_silent:
        print('科目：{} クイズ：{}'.format(c.name_with_memo, qz.title))
        confirm = None
        while confirm not in ['','y','n']:
            confirm = input('科目、クイズ名は正しいですか？（[y],n）: ')
        if confirm == 'n':
            sys.exit()
    return dict(cid=int(m.group('cid')), qid=int(m.group('qid')))
