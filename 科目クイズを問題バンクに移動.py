#!/usr/bin/env python3
# coding: utf-8

#import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select

import pprint, time, sys

USER = ''
PASS = ''

""" ■■■■ 移動元のクイズと移動先の問題バンク ■■■■
各要素は [course_id, quiz_id, qbank_id]
"""
# from_to_dict = dict(cource_id=5282, quiz_id=3142, qbank_id=511)
cource_id=5283

# コピー元のクイズID, コピー先の問題バンクIDを要素とするリストのリスト
# 3番目の要素を指定すると、移動を開始する問題番号（Quiz中での序数）を指定できる。
from_to_list = [
    # [3427, 554], # ECB5-05-MCQ
    # [3429, 555], # ECB5-05-TFQ
    # [3436, 556], # ECB5-06-MCQ
    # [3437, 557], # ECB5-06-ShA
    # [3438, 558], # ECB5-06-TFQ
    # [3439, 559], # ECB5-06-MSA
    # [3440, 560], # ECB5-07-MCQ
    # [3441, 561, 42], # ECB5-08-MCQ
    # [3442, 562], # ECB5-08-ShA
    # [3443, 563], # ECB5-08-MSA
    # [3444, 564], # ECB5-09-MCQ
    # [3445, 565], # ECB5-09-ShA
    # [3446, 566], # ECB5-09-TFQ
    # [3447, 567], # ECB5-09-MSA
    # [3448, 568], # ECB5-10-MCQ
    # [3449, 569], # ECB5-10-ShA
    # [3450, 570], # ECB5-10-MSA
    # [2705, 574], # Reading Quiz 06
    [2704, 575], # Reading Quiz 07
    [2706, 576], # Reading Quiz 08
    [2708, 577], # Reading Quiz 09
    [2707, 578], # Reading Quiz 10
]

url_tmpl = dict(
    course_quiz = 'https://sol.sfc.keio.ac.jp/courses/{cource_id}/quizzes/{quiz_id}/edit',
    qbank = 'https://sol.sfc.keio.ac.jp/courses/{cource_id}/question_banks/{qbank_id}',
)

login_url = 'https://sol.sfc.keio.ac.jp/login/ldap'

# Chromeの初期化
dr_from = Chrome(ChromeDriverManager().install())
dr_to = Chrome(ChromeDriverManager().install())


def get_dom(dr, query):
    dom = WebDriverWait(dr, 10).until(
      EC.presence_of_element_located(
        (By.CSS_SELECTOR, query)))
    return dom


def copy_html(d_qz, d_bk, css_qz, css_bk):
    '''
    d_qz クイズページのDriverオブジェクト
    d_bk 問題バンクページのDriverオブジェクト
    css_qz クイズページのテキストエディタへのselector
    css_bk 問題バンクページのテキストエディタへのselector
    '''

    # TODO a.comment_focus とは限らない？
    # 編集モードに移行
    d_qz.execute_script("arguments[0].click();",
        get_dom(d_qz, f'{css_qz} a.comment_focus'))
    d_bk.execute_script("arguments[0].click();",
        get_dom(d_bk, f'{css_bk} a.comment_focus'))
    time.sleep(.5)
    # HTML編集モードに移行
    d_qz.execute_script("arguments[0].click();",
        get_dom(d_qz, f'{css_qz} button[data-btn-id="rce-edit-btn"]'))
    d_bk.execute_script("arguments[0].click();",
        get_dom(d_bk, f'{css_bk} button[data-btn-id="rce-edit-btn"]'))
    time.sleep(.5)
    # HTMLを取得して書き込む
    answer_html = get_dom(d_qz, f'{css_qz} textarea.editor-toggle').get_attribute('value')
    get_dom(d_bk, f'{css_bk} textarea.editor-toggle').send_keys(answer_html)
    time.sleep(.5)
    # Doneボタンをクリックして選択肢の編集を終了
    d_qz.execute_script("arguments[0].click();",
        get_dom(d_qz, f'{css_qz} a.btn.edit_html_done'))
    d_bk.execute_script("arguments[0].click();",
        get_dom(d_bk, f'{css_bk} a.btn.edit_html_done'))
    time.sleep(.5)







# ログインページを開く
dr_from.get(login_url)
dr_to.get(login_url)

for d in [dr_from, dr_to]:
    # ユーザー・パスワードを入力
    user = get_dom(d, '#pseudonym_session_unique_id')
    user.send_keys(USER)
    pw = get_dom(d, '#pseudonym_session_password')
    pw.send_keys(PASS)
    # ログインボタンをクリック
    login_btn = get_dom(d, '#login_form > div.ic-Login__actions > div.ic-Form-control.ic-Form-control--login > button')
    login_btn.click()


for i in from_to_list:
    quiz_id, qbank_id  = i[0:2]
    Q_start = i[2] if len(i) > 2 else 1

    from_url = url_tmpl['course_quiz'].format(cource_id=cource_id,quiz_id=quiz_id)
    to_url = url_tmpl['qbank'].format(cource_id=cource_id,qbank_id=qbank_id)

    # 問題バンクを開く
    dr_to.get( to_url )

    # クイズ編集画面を開き、質問をクリック
    dr_from.get( from_url )
    question_link = get_dom(dr_from, '#ui-id-2')
    question_link.click()
    time.sleep(3)

    actions_from = ActionChains(dr_from)
    actions_to = ActionChains(dr_to)


    # question_teaser をクリックして通常の問題表記に変換
    for question_teaser_link in dr_from.find_elements_by_css_selector(
        'div.quiz_sortable.question_holder.question_teaser a.question_name.name.question_teaser_link'):
        dr_from.execute_script("arguments[0].click();", question_teaser_link)
        time.sleep(0.2)


    l = len('question_')
    n_Q = 0  # ページ内で何問目の問題かquestion display_question multiple_choice_question
    for div_question in dr_from.find_elements_by_css_selector('#questions div.question'):
        n_Q += 1
        if n_Q < Q_start:
            continue

        id_str = div_question.get_attribute("id")[l:]

        # 問題バンクで問題作成画面に推移
        get_dom(dr_to, '#right-side > div:nth-child(1) > a.btn.button-sidebar-wide.add_question_link').click()

        # クイズ編集画面に移行（鉛筆アイコンをクリック）
        dr_from.execute_script("arguments[0].click();",
            get_dom(dr_from, f'#question_{id_str} > div.links > a.edit_question_link.no-hover'))
        time.sleep(1)

        # HTML編集モードに移行
        html_button_el = get_dom(dr_from,
            f'#questions > div:nth-child({n_Q}) > form.question_form button[data-btn-id="rce-edit-btn"]')
        dr_from.execute_script("arguments[0].click();", html_button_el)
        html_button_el = get_dom(dr_to,
            '#questions form.question_form button[data-btn-id="rce-edit-btn"]')
        dr_to.execute_script("arguments[0].click();", html_button_el)
        time.sleep(.5)

        """
        問題名
        """
        question_name = get_dom(dr_from,
            f'#questions > div:nth-child({n_Q}) > form div.header > input[name="question_name"]').get_attribute('value')
        print('question_name =' + question_name)
        # 書き込む
        question_name_to_el = get_dom(dr_to,
            '#questions form div.header > input[name="question_name"]')
        question_name_to_el.clear()
        time.sleep(.1)
        question_name_to_el.send_keys(question_name)

        """ ####################
        問題の種類 question_type
        """
        question_type = Select(get_dom(dr_from,
            f'#questions > div:nth-child({n_Q}) > form div.header > select[name="question_type"]'))
        selected_question_type = question_type.first_selected_option
        if selected_question_type:
            selected_question_type_value = selected_question_type.get_attribute('value')
        else:
            selected_question_type_value = "multiple_choice_question"  #デフォルト
        print('selected_question_type_value = ' +  selected_question_type_value)
        # 書き込む
        question_type_to = Select(get_dom(dr_to, '#questions form div.header > select[name="question_type"]'))
        question_type_to.select_by_value(selected_question_type_value)

        """
        問題文
        """
        question_text = get_dom(dr_from, f'#questions > div:nth-child({n_Q}) textarea[name="question_text"]').get_attribute('value')
        print(question_text)
        # 書き込む
        get_dom(dr_to, 'form.question_form textarea[name="question_text"]').send_keys(question_text)

        """
        選択肢
        """
        n_answers = len(dr_from.find_elements_by_css_selector(f'#questions > div:nth-child({n_Q}) div.form_answers div.answer'))
        print(f"n_answers = {n_answers}")

        for i in range(1, n_answers + 1):
            div_from = get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i})')
            div_to = get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i})')
            print(f'div_from[class] = {div_from.get_attribute("class")}')  # answer answer_for_none correct_answer
            # 正解ならボタンを押す
            if 'correct_answer' in div_from.get_attribute('class').split(' '):
                dr_to.execute_script("arguments[0].click();",
                    get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) button.select_answer_link'))
            time.sleep(.5)

            # 真偽問題なら選択肢の編集はスキップ
            if selected_question_type_value == 'true_false_question':
                continue

            # 選択肢のテキストを書き込む
            # 編集モードに移行
            dr_from.execute_script("arguments[0].click();",
                get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) a.edit_html'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) a.edit_html'))
            time.sleep(.5)
            # HTML編集モードに移行
            dr_from.execute_script("arguments[0].click();",
                get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) button[data-btn-id="rce-edit-btn"]'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) button[data-btn-id="rce-edit-btn"]'))
            time.sleep(.5)
            # HTMLを取得して書き込む
            answer_html = get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) textarea.editor-toggle').get_attribute('value')
            get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) textarea.editor-toggle').send_keys(answer_html)
            time.sleep(.5)
            # Doneボタンをクリックして選択肢の編集を終了
            dr_from.execute_script("arguments[0].click();",
                get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) a.btn.edit_html_done'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) a.btn.edit_html_done'))
            time.sleep(.5)
        """
        フィードバック
        """
        # 編集モードに移行
        dr_from.execute_script("arguments[0].click();",
            get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment a.comment_focus'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment a.comment_focus'))
        time.sleep(.5)
        # HTML編集モードに移行
        dr_from.execute_script("arguments[0].click();",
            get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment button[data-btn-id="rce-edit-btn"]'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment button[data-btn-id="rce-edit-btn"]'))
        time.sleep(.5)
        # HTMLを取得して書き込む
        answer_html = get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment textarea.editor-toggle').get_attribute('value')
        get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment textarea.editor-toggle').send_keys(answer_html)
        time.sleep(.5)
        # Doneボタンをクリックして選択肢の編集を終了
        dr_from.execute_script("arguments[0].click();",
            get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment a.btn.edit_html_done'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment a.btn.edit_html_done'))
        time.sleep(.5)
        """
        １問のコピーを終了
        """
        dr_from.execute_script("arguments[0].click();",
            get_dom(dr_from, f'#questions > div:nth-child({n_Q}) div.button-container button.btn.btn-small.cancel_link'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.button-container button.btn.btn-small.submit_button'))
        time.sleep(1)
