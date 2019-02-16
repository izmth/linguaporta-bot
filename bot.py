import sys
from time import sleep
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from googletrans import Translator

def login():
    print('IDを入力')
    uid = input()
    print('パスワードを入力')
    upassword = input()

    id = driver.find_element_by_name('id')
    password = driver.find_element_by_name('password')
    submit = driver.find_element_by_id('btn-login')

    id.clear()
    id.send_keys(uid)
    password.send_keys(upassword)
    submit.submit()

    sleep(1)
    try:
        driver.find_element_by_class_name("small_error")
    except:
        pass
    else:
        raise ValueError('invalid id or password')

def selectCocet():
    try:
        driver.execute_script("document.sStudy.submit()") # 本の選択画面へ移行
        driver.execute_script("select_reference('70')") # cocet2600を選択
    except:
        driver.quit()
        sys.exit()

def selectUnit(unit_num):
    unit_num = (unit_num-1)/25 + 1
    script = "select_unit('drill', '" + str(1813 + (unit_num-1)*4) + "', '');"
    try:
        driver.execute_script(script)
    except:
        driver.quit()
        sys.exit()

def answer_by_translate(answers, question):
    # Google翻訳の結果を取得
    translator = Translator()
    guess = translator.translate(question.text, dest='ja').text
    print("翻訳結果:", guess)

    # 翻訳と合致するものがあれば選択
    for i, answer in enumerate(answers):
        text = answer.get_attribute('value')
        if text in guess or guess in text:
            return i # 合致するものの番号を返す
            # answer.click()
    return -1 # 合致しなかった場合

def answer_by_history(answers, question, history):
    for i, answer in enumerate(answers):
        answer_text = answer.get_attribute('value')
        if answer_text in history[question.text]:
            return i

def create_history(answers, quesiton, history):
    for answer in answers:
        history.setdefault(quesiton.text, []).append(answer.get_attribute('value'))
    return history

def update_history(answers, question, history):
    tmp = []
    for answer in answers:
        answer_text = answer.get_attribute('value')
        if answer_text in history[question.text]: # 前回にも選択肢に存在していた場合
            tmp.append(answer_text) # その選択肢の番号を記録する
    history[question.text] = tmp
    return history

def Answer():
    history = {}
    while(True):
        sleep(2)

        print("=================================================")

        # 英単語の取得
        try:
            question = driver.find_element_by_id('qu02')
        except:
            print("このユニットは既に完了しています。")
            break

        print("問題:", question.text)

        # 選択肢の取得
        answers = []
        answers.append(driver.find_element_by_id('answer_0_0'))
        answers.append(driver.find_element_by_id('answer_0_1'))
        answers.append(driver.find_element_by_id('answer_0_2'))
        answers.append(driver.find_element_by_id('answer_0_3'))
        answers.append(driver.find_element_by_id('answer_0_4'))

        print("選択肢: {}, {}, {}, {}, {}".format(answers[0].get_attribute('value'),
                                                answers[1].get_attribute('value'),
                                                answers[2].get_attribute('value'),
                                                answers[3].get_attribute('value'),
                                                answers[4].get_attribute('value')))

        if question.text not in history: # historyにない（初めて出てきた問題の）場合
            history = create_history(answers, question, history)
            choice = answer_by_translate(answers, question)
            if choice == -1:
                print("選択:", answers[0].get_attribute('value'))
                answers[0].click() # 翻訳合致せず
            else:
                print("選択:", answers[choice].get_attribute('value'))
                answers[choice].click()
        else:
            history = update_history(answers, question, history)
            print("絞り込み:", history[question.text])

            choice = answer_by_history(answers, question, history)
            print("選択:", answers[choice].get_attribute('value'))
            answers[choice].click()
            history[question.text].remove(answers[choice].get_attribute('value'))
            
        # submit
        driver.find_element_by_id('ans_submit').submit()

        sleep(2)
        # 正解と不正解の判定
        try:
            driver.find_element_by_id('true_msg')
            print('結果: 正解')
        except:
            print("結果: 不正解")

        # 次へすすめる場合は進む、なければユニット終了
        try:
            driver.find_element_by_class_name('btn-problem-next').submit()
        except:
            break

if __name__ == '__main__':
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get('https://w5.linguaporta.jp/user/seibido/index.php')
    driver.set_window_size(720, 1280)

    for i in range(0, 3):
        try:
            login()
        except:
            if i == 2:
                print("失敗回数の上限に達しました。プログラムを終了します。")
                driver.quit()
                sys.exit()
            else:
                print("ログインに失敗しました。再度入力して下さい。")
        else:
            break

    while(True):
        print('を入力して下さい。(1-25の場合は1, 126-150の場合は126)')
        num = int(input())
        if num % 25 == 1:
            break
        else:
            print("無効な番号です。入力しなおして下さい。")

    while(True):
        print('終了する番号を入力して下さい。(976-1000を最後にするなら1000)')
        end_num = int(input())
        if end_num % 25 == 0:
            break
        else:
            print("無効な番号です。入力しなおして下さい。")

    while(True):
        selectCocet()
        print('現在のユニット:', str(num)+'-'+str(num+24))
        selectUnit(num)
        Answer()
        if num >= (end_num-24):
            break
        num += 25

    print("指定されたユニットの回答を完了しました。プログラムを終了します。")
    driver.quit()  # ブラウザーを終了する。
    sys.exit()