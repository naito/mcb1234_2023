#!/usr/bin/env python3
# coding: utf-8
'''
クイズの詳細情報を開く
'''
#import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from pprint import pprint

import time, sys, traceback, argparse

""" ■■■■ 引数の設定 ■■■■ """
def get_args():
    parser = argparse.ArgumentParser(
        description = '''Chromeでクイズを開き、MCQ以外の問題の詳細を開く。（過年度科目からのコピーで正解にエラーが入る場合があるので、その確認用）'''
    )
    parser.add_argument('CourseID', type=int,
        help='コースID'
    )
    parser.add_argument('QuizID', type=int,
        help='クイズID'
    )

    return parser.parse_args()

args = get_args()


USER = ''
PASS = ''

quiz_questions_url = f'https://sol.sfc.keio.ac.jp/courses/{args.CourseID}/quizzes/{args.QuizID}/edit#questions_tab'

login_url = 'https://sol.sfc.keio.ac.jp/login/ldap'

q_type_class_ls = (
    'multiple_choice_question',      # 選択肢問題
    'multiple_answers_question',     # 選択肢問題（複数選択）
    'multiple_dropdowns_question',   # 複数ドロップダウン問題（穴埋めなど）
    'numerical_question',            # 数値問題
)
"""
multiple_choice_question            選択
true_false_question                 真/偽
short_answer_question               穴埋め
fill_in_multiple_blanks_question    複数穴埋め
multiple_answers_question           複数解答
multiple_dropdowns_question         複数ドロップダウン
matching_question                   整合
numerical_question                  数値による解答
calculated_question                 数式問題
essay_question                      小論文問題
file_upload_question                ファイル アップロード問題
text_only_question                  テキスト (問題ではない)
"""
qid_header_length = len('question_')

# Chromeの初期化
options = Options()
options.add_experimental_option('detach', True)
driver = Chrome(ChromeDriverManager().install(), options=options)

# ログインページを開く
driver.get(login_url)
# ユーザー・パスワードを入力
user = driver.find_element(By.CSS_SELECTOR, '#pseudonym_session_unique_id')
user.send_keys(USER)
pw = driver.find_element(By.CSS_SELECTOR, '#pseudonym_session_password')
pw.send_keys(PASS)
# ログインボタンをクリック
login_btn = driver.find_element(By.CSS_SELECTOR, '#login_form > div.ic-Login__actions > div.ic-Form-control.ic-Form-control--login > button')
login_btn.click()

# クイズ問題編集ページを取得
driver.get( quiz_questions_url )

for question_holder in driver.find_elements(By.CSS_SELECTOR,
    'div.quiz_sortable.question_holder.group'):

    # 鉛筆アイコンをクリックして編集UIを表示
    edit_question_link = question_holder.find_element(By.CSS_SELECTOR, 'div.links > a.edit_question_link')
    driver.execute_script("arguments[0].click();", edit_question_link)
    time.sleep(0.2)

    # MCQだったら閉じる
    is_mcq = question_holder.find_elements(By.CSS_SELECTOR, 'div.display_question.question.multiple_choice_question')
    if len(is_mcq) > 0:
        cancel_button = question_holder.find_element(By.CSS_SELECTOR, 'div.button-container > button.btn.btn-small.cancel_link')
        driver.execute_script("arguments[0].click();", cancel_button)
        time.sleep(0.2)
