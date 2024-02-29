#!/usr/bin/env python3
# coding: utf-8

import chromedriver_binary
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import pprint, time

USER = ''
PASS = ''

""" ■■■■ 移動先の問題バンク ■■■■ """
# dest_qbank_id = 186  # 科学史21-まとめスライド01
# dest_qbank_id = 189  # 科学史21-まとめスライド02
# dest_qbank_id = 190  # 科学史21-まとめスライド03
# dest_qbank_id = 191  # 科学史21-まとめスライド04
# dest_qbank_id = 192  # 科学史21-まとめスライド05
# dest_qbank_id = 193  # 科学史21-まとめスライド06A
# dest_qbank_id = 204  # 科学史21-まとめスライド06B
# dest_qbank_id = 194  # 科学史21-まとめスライド07
# dest_qbank_id = 195  # 科学史21-まとめスライド08
# dest_qbank_id = 196  # 科学史21-まとめスライド09
# dest_qbank_id = 197  # 科学史21-まとめスライド10
# dest_qbank_id = 198  # 科学史21-まとめスライド11
# dest_qbank_id = 199  # 科学史21-まとめスライド12
# dest_qbank_id = 200  # 科学史21-まとめスライド13
# dest_qbank_id = 201  # 科学史21-まとめスライド14

cource_id = 2989  # 科学史 2021春
tmp_qbank_id = 188    # バンク『未整理の問題』

url_tmpl = dict(
    qbank = 'https://sol.sfc.keio.ac.jp/courses/{cource_id}/question_banks/{qbank_id}',
)

tmp_qbank_url = url_tmpl['qbank'].format(cource_id = cource_id, qbank_id = tmp_qbank_id)

# Chromeの初期化
driver = Chrome()

def get_dom(query):
    dom = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located(
        (By.CSS_SELECTOR, query)))
    return dom

# ログインページを開く
url = 'https://sol.sfc.keio.ac.jp/login/ldap'
driver.get(url)
# ユーザー・パスワードを入力
user = get_dom('#pseudonym_session_unique_id')
user.send_keys(USER)
pw = get_dom('#pseudonym_session_password')
pw.send_keys(PASS)
# ログインボタンをクリック
login_btn = get_dom('#login_form > div.ic-Login__actions > div.ic-Form-control.ic-Form-control--login > button')
login_btn.click()

driver.get( tmp_qbank_url )
mv_q_link = get_dom('#right-side > div:nth-child(1) > a.btn.button-sidebar-wide.move_questions_link')
mv_q_link.click()
time.sleep(5)

mv_q_list = driver.find_elements_by_css_selector(
    '#move_question_dialog li.list_question input.list_question_checkbox')
print( 'Move Questions: {}'.format( len( mv_q_list )))

"""
actions = selenium_actions()
for a_label in mv_q_list:
    actions.move_to_element(a_label)
    actions.click(a_label)
    actions.perform()
"""
# すべての問題を移動対象としてチェック
for a_label in mv_q_list:
    script = 'document.querySelector("input#{}").checked = true;'.format(a_label.get_attribute("id"))
    driver.execute_script(script)

# 移動先の問題バンクをチェック
script = 'document.querySelector("input#question_bank_{}").checked = true;'.format(dest_qbank_id)
driver.execute_script(script)

# 『問題の移動』ボタンをクリック
get_dom('#move_question_dialog > div.move_question_dialog_actions > button.Button.Button--primary.submit_button').click()
