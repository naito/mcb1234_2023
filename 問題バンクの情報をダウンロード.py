#!/usr/bin/env python3
# coding: utf-8
'''
問題バンクの内容をダンプする
'''
#import chromedriver_binary
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
save_folder = '.'

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
driver = Chrome(ChromeDriverManager().install())


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


'''
解答ブロックの内容を、問題タイプ別に返す
長大なif文を避けるために、関数オブジェクトの辞書をつくって、問題タイプのキーで検索するしくみを実装
'''
def get_multiple_choice_question_answers(question_holder):
    answers = dict()
    form_answers = question_holder.find_element(By.CSS_SELECTOR, 'form.question_form div.form_answers')

    for answer in form_answers.find_elements(By.CSS_SELECTOR, 'div.answer'):
        # 選択肢番号
        aid = int(answer.find_element(By.CSS_SELECTOR, 'label').get_attribute('id')[len('answer'):])
        # print(f'問題番号：{aid}')
        # 正解？
        is_correct = 1 if answer.get_attribute('class').split()[-1] == 'correct_answer' else 0
        # print(f'正解：{is_correct}')
        # 選択肢のHTML
        try:
            answer_text = None
            # 解答の編集UIを表示
            edit_answer_link = get_dom(answer, 'div.question_actions > a.edit_html')
            driver.execute_script("arguments[0].click();", edit_answer_link)
            time.sleep(0.2)
            # 解答の編集をリッチエディタからHTMLに切り替え
            answer_html_button = answer.find_element(By.CSS_SELECTOR, 'div.select_answer.answer_type button[data-btn-id="rce-edit-btn"]')
            driver.execute_script("arguments[0].click();", answer_html_button)
            time.sleep(.5)

            answer_html = answer.find_element(By.CSS_SELECTOR, 'div.select_answer.answer_type textarea').get_attribute('value')
            # print(answer_html)
        except:
            answer_html = None
            answer_text = answer.find_element(By.CSS_SELECTOR, 'table tr:nth-child(1) > td:nth-child(2) > div.fixed_answer > b.answer_text').get_attribute('innerHTML')
            # print(answer_text)

        answers[aid] = dict(
            is_correct = is_correct,
            answer_text = answer_text,
            answer_html = answer_html,
        )

    return answers

def get_true_false_question_answers(question_holder):
    pass

def get_short_answer_question_answers(question_holder):
    pass

def get_fill_in_multiple_blanks_question_answers(question_holder):
    pass

def get_multiple_answers_question_answers(question_holder):
    return get_multiple_choice_question_answers(question_holder)

def get_multiple_dropdowns_question_answers(question_holder):
    pass

def get_matching_question_answers(question_holder):
    pass

def get_numerical_question_answers(question_holder):
    answers = dict()

    numerical_answer_type = Select(question_holder.find_element(By.CSS_SELECTOR,
        'form.question_form div.form_answers select.numerical_answer_type')).first_selected_option.get_attribute('value')

    div_answers = question_holder.find_element(By.CSS_SELECTOR,
        'div.text div.answers_wrapper > div.answer')

    if numerical_answer_type == 'exact_answer':  # 正確な解答:
        answer_exact = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_exact_answer.answer_type > span.answer_exact').get_attribute('innerText')
        answer_error_margin = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_exact_answer.answer_type > span.answer_error_margin').get_attribute('innerText')
        return dict(
            type = numerical_answer_type,
            exact = answer_exact,
            error_margin = answer_error_margin,
        )
    elif numerical_answer_type == 'range_answer':  # 範囲内の解答::
        answer_range_start = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_range_answer.answer_type > span.answer_range_start').get_attribute('innerText')
        answer_range_end = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_range_answer.answer_type > span.answer_range_end').get_attribute('innerText')
        return dict(
            type = numerical_answer_type,
            range_start = answer_range_start,
            range_end = answer_range_end,
        )
    elif numerical_answer_type == 'precision_answer':  # 的確で正確な解答::
        answer_approximate = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_precision_answer.answer_type > span.answer_approximate').get_attribute('innerText')
        answer_precision = div_answers.find_element(By.CSS_SELECTOR,
            'div.numerical_precision_answer.answer_type > span.answer_precision').get_attribute('innerText')
        return dict(
            type = numerical_answer_type,
            approximate = answer_approximate,
            precision = answer_precision,
        )

def get_calculated_question_answers(question_holder):
    pass

def get_essay_question_answers(question_holder):
    pass

def get_file_upload_question_answers(question_holder):
    pass

def get_text_only_question_answers(question_holder):
    pass


get_answers_methods = dict(
    multiple_choice_question = get_multiple_choice_question_answers,
    true_false_question = get_true_false_question_answers,
    short_answer_question = get_short_answer_question_answers,
    fill_in_multiple_blanks_question = get_fill_in_multiple_blanks_question_answers,
    multiple_answers_question = get_multiple_answers_question_answers,
    multiple_dropdowns_question = get_multiple_dropdowns_question_answers,
    matching_question = get_matching_question_answers,
    numerical_question = get_numerical_question_answers,
    calculated_question = get_calculated_question_answers,
    essay_question = get_essay_question_answers,
    file_upload_question = get_file_upload_question_answers,
    text_only_question = get_text_only_question_answers,
)

def get_answers(question_type, question_holder):
    return get_answers_methods[question_type](question_holder)




# ログインページを開く
driver.get(login_url)
# ユーザー・パスワードを入力
user = get_dom(driver, '#pseudonym_session_unique_id')
user.send_keys(USER)
pw = get_dom(driver, '#pseudonym_session_password')
pw.send_keys(PASS)
# ログインボタンをクリック
login_btn = get_dom(driver, '#login_form > div.ic-Login__actions > div.ic-Form-control.ic-Form-control--login > button')
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
    if qb_title != 'ECB5-13-MCQ':
        continue

    driver.get( qb_url )

    qb_ls = []

    '''
    # 鉛筆アイコンをクリックして編集UIを表示
    for edit_question_link in driver.find_elements(By.CSS_SELECTOR,
        'div.display_question.question > div.links > a.edit_question_link'):
        driver.execute_script("arguments[0].click();", edit_question_link)
        time.sleep(0.2)
    '''
    '''
    'multiple_choice_question',      # 選択肢問題
    'multiple_answers_question',     # 選択肢問題（複数選択）
    'multiple_dropdowns_question',   # 複数ドロップダウン問題（穴埋めなど）
    'numerical_question',            # 数値問題
    '''
    for question_holder in driver.find_elements(By.CSS_SELECTOR,
        'div.quiz_sortable.question_holder'):

        print(question_holder)

        question_name = question_holder.find_element(By.CSS_SELECTOR,
            'div.header > span.name.question_name').get_attribute('innerText')
        '''
        # DEV
        if question_name != 'SA-11-01':
            continue
        '''
        # 鉛筆アイコンをクリックして編集UIを表示
        edit_question_link = question_holder.find_element(By.CSS_SELECTOR,
            'div.display_question.question > div.links > a.edit_question_link')
        driver.execute_script("arguments[0].click();", edit_question_link)
        time.sleep(0.2)

        # 問題文編集をリッチエディタからHTMLに切り替え
        html_button_el = get_dom(question_holder, 'form.question_form button[data-btn-id="rce-edit-btn"]')
        driver.execute_script("arguments[0].click();", html_button_el)
        time.sleep(.5)

        # 共通コメントの編集UIを表示
        edit_neutral_comment_link = get_dom(question_holder, 'div.question_comment.question_neutral_comment.comment > a.comment_focus')
        driver.execute_script("arguments[0].click();", edit_neutral_comment_link)
        time.sleep(0.2)
        # 共通コメントの編集をリッチエディタからHTMLに切り替え
        neutral_comment_html_button = get_dom(question_holder, 'div.question_comment.question_neutral_comment.comment.editing button[data-btn-id="rce-edit-btn"]')
        driver.execute_script("arguments[0].click();", neutral_comment_html_button)
        time.sleep(.5)

        div_display = get_dom(question_holder, 'div.display_question.question')
        form_question = get_dom(question_holder, 'form.question_form')

        # 問題タイプの取得
        question_type = Select(get_dom(form_question, 'select.question_type')).first_selected_option.get_attribute('value')

        q_dict = dict(
            type = question_type,
            id = int(form_question.get_attribute("action").split('/')[-1]),
            name = question_name,
            q_content = get_dom(form_question, 'textarea[name="question_text"]').get_attribute('value'),
            answers = get_answers(question_type, question_holder),
            # 共通コメント
            neutral_comments_html = form_question.find_element(By.CSS_SELECTOR, 'div.question_comment.question_neutral_comment.comment.editing textarea').get_attribute('value'),
        )
        pprint(q_dict)
        qb_ls.append(q_dict)
        sys.exit()

#editor-toggle-1

    sys.exit()



sys.exit()






for i in from_to_list:
    quiz_id, qbank_id  = i[0:2]
    Q_start = i[2] if len(i) > 2 else 1

    from_url = url_tmpl['course_quiz'].format(cource_id=cource_id,quiz_id=quiz_id)
    to_url = url_tmpl['qbank'].format(cource_id=cource_id,qbank_id=qbank_id)

    # 問題バンクを開く
    dr_to.get( to_url )

    # クイズ編集画面を開き、質問をクリック
    driver.get( from_url )
    question_link = get_dom(driver, '#ui-id-2')
    question_link.click()
    time.sleep(3)

    actions_from = ActionChains(driver)
    actions_to = ActionChains(dr_to)


    # question_teaser をクリックして通常の問題表記に変換
    for question_teaser_link in driver.find_elements_by_css_selector(
        'div.quiz_sortable.question_holder.question_teaser a.question_name.name.question_teaser_link'):
        driver.execute_script("arguments[0].click();", question_teaser_link)
        time.sleep(0.2)


    l = len('question_')
    n_Q = 0  # ページ内で何問目の問題かquestion display_question multiple_choice_question
    for div_question in driver.find_elements_by_css_selector('#questions div.question'):
        n_Q += 1
        if n_Q < Q_start:
            continue

        id_str = div_question.get_attribute("id")[l:]

        # 問題バンクで問題作成画面に推移
        get_dom(dr_to, '#right-side > div:nth-child(1) > a.btn.button-sidebar-wide.add_question_link').click()

        # クイズ編集画面に移行（鉛筆アイコンをクリック）
        driver.execute_script("arguments[0].click();",
            get_dom(driver, f'#question_{id_str} > div.links > a.edit_question_link.no-hover'))
        time.sleep(1)

        # HTML編集モードに移行
        html_button_el = get_dom(driver,
            f'#questions > div:nth-child({n_Q}) > form.question_form button[data-btn-id="rce-edit-btn"]')
        driver.execute_script("arguments[0].click();", html_button_el)
        html_button_el = get_dom(dr_to,
            '#questions form.question_form button[data-btn-id="rce-edit-btn"]')
        dr_to.execute_script("arguments[0].click();", html_button_el)
        time.sleep(.5)

        """
        問題名
        """
        question_name = get_dom(driver,
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
        question_type = Select(get_dom(driver,
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
        question_text = get_dom(driver, f'#questions > div:nth-child({n_Q}) textarea[name="question_text"]').get_attribute('value')
        print(question_text)
        # 書き込む
        get_dom(dr_to, 'form.question_form textarea[name="question_text"]').send_keys(question_text)

        """
        選択肢
        """
        n_answers = len(driver.find_elements_by_css_selector(f'#questions > div:nth-child({n_Q}) div.form_answers div.answer'))
        print(f"n_answers = {n_answers}")

        for i in range(1, n_answers + 1):
            div_from = get_dom(driver, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i})')
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
            driver.execute_script("arguments[0].click();",
                get_dom(driver, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) a.edit_html'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) a.edit_html'))
            time.sleep(.5)
            # HTML編集モードに移行
            driver.execute_script("arguments[0].click();",
                get_dom(driver, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) button[data-btn-id="rce-edit-btn"]'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) button[data-btn-id="rce-edit-btn"]'))
            time.sleep(.5)
            # HTMLを取得して書き込む
            answer_html = get_dom(driver, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) textarea.editor-toggle').get_attribute('value')
            get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) textarea.editor-toggle').send_keys(answer_html)
            time.sleep(.5)
            # Doneボタンをクリックして選択肢の編集を終了
            driver.execute_script("arguments[0].click();",
                get_dom(driver, f'#questions > div:nth-child({n_Q}) div.form_answers div.answer:nth-child({i}) a.btn.edit_html_done'))
            dr_to.execute_script("arguments[0].click();",
                get_dom(dr_to, f'#questions div.form_answers div.answer:nth-child({i}) a.btn.edit_html_done'))
            time.sleep(.5)
        """
        フィードバック
        """
        # 編集モードに移行
        driver.execute_script("arguments[0].click();",
            get_dom(driver, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment a.comment_focus'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment a.comment_focus'))
        time.sleep(.5)
        # HTML編集モードに移行
        driver.execute_script("arguments[0].click();",
            get_dom(driver, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment button[data-btn-id="rce-edit-btn"]'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment button[data-btn-id="rce-edit-btn"]'))
        time.sleep(.5)
        # HTMLを取得して書き込む
        answer_html = get_dom(driver, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment textarea.editor-toggle').get_attribute('value')
        get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment textarea.editor-toggle').send_keys(answer_html)
        time.sleep(.5)
        # Doneボタンをクリックして選択肢の編集を終了
        driver.execute_script("arguments[0].click();",
            get_dom(driver, f'#questions > div:nth-child({n_Q}) div.question_comment.question_neutral_comment a.btn.edit_html_done'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.question_comment.question_neutral_comment a.btn.edit_html_done'))
        time.sleep(.5)
        """
        １問のコピーを終了
        """
        driver.execute_script("arguments[0].click();",
            get_dom(driver, f'#questions > div:nth-child({n_Q}) div.button-container button.btn.btn-small.cancel_link'))
        dr_to.execute_script("arguments[0].click();",
            get_dom(dr_to, f'#questions div.button-container button.btn.btn-small.submit_button'))
        time.sleep(1)
