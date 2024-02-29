#!/usr/bin/env python3
# coding: utf-8
'''
問題バンクの詳細情報を開く
'''
#import chromedriver_binary
# from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select

from bs4 import BeautifulSoup
from pprint import pprint

import time, sys

USER = ''
PASS = ''

""" ■■■■ 移動元のクイズと移動先の問題バンク ■■■■
各要素は [course_id, quiz_id, qbank_id]
"""
# from_to_dict = dict(cource_id=5282, quiz_id=3142, qbank_id=511)
cource_id = 6708
qbank_name = 'ECB5-13-MCQ'



url_tmpl = dict(
    qbank_ls = 'https://sol.sfc.keio.ac.jp/courses/{cource_id}/question_banks',
    qbank = 'https://sol.sfc.keio.ac.jp/courses/{cource_id}/question_banks/{qbank_id}',
)

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
# options = Options()
# options.add_experimental_option('detach', True)
driver = Chrome(ChromeDriverManager().install())

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

# コースの問題バンクページを取得
qbank_ls_url = url_tmpl['qbank_ls'].format(cource_id=cource_id)
driver.get( qbank_ls_url )

# 問題バンクのURLの辞書を作成。キーは問題バンク名
qbank_selector = '#questions > div.question_bank div.header.clearfix > div.header_content > a'
qbanks = {a.text : a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, qbank_selector)}
print(qbanks)

for qb_title, qb_url in qbanks.items():
    # DEV
    if qb_title != qbank_name:
        continue

    driver.get( qb_url )

    # 鉛筆アイコンをクリックして編集UIを表示
    for edit_question_link in driver.find_elements(By.CSS_SELECTOR,
        'div.display_question.question > div.links > a.edit_question_link'):
        driver.execute_script("arguments[0].click();", edit_question_link)
        time.sleep(0.2)

    sys.exit()
