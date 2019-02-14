import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from googletrans import Translator

def login(uid, upassword):
    id = driver.find_element_by_name('id')
    password = driver.find_element_by_name('password')
    submit = driver.find_element_by_id('btn-login')

    id.send_keys(uid)
    password.send_keys(upassword)
    submit.submit()

def selectCocet():
    driver.execute_script("document.sStudy.submit()") # 本の選択画面へ移行
    driver.execute_script("select_reference('70')") # cocet2600を選択

def selectUnit(unit_num):
    unit_num = (unit_num-1)/25 + 1
    script = "select_unit('drill', '" + str(1813 + (unit_num-1)*4) + "', '');"
    driver.execute_script(script)

def Answer():
    hist = {}
    while(True):
        time.sleep(2) # 待つ(サーバーにやさしく)

        print("=================================================")

        # 英単語の取得
        question = driver.find_element_by_id('qu02')
        print("Question:", question.text)

        # Google翻訳の結果
        translator = Translator()
        guess = translator.translate(question.text, dest='ja').text
        print("Translate:", guess)

        # 解答群の取得
        answers = []
        answers.append(driver.find_element_by_id('answer_0_0'))
        answers.append(driver.find_element_by_id('answer_0_1'))
        answers.append(driver.find_element_by_id('answer_0_2'))
        answers.append(driver.find_element_by_id('answer_0_3'))
        answers.append(driver.find_element_by_id('answer_0_4'))

        # 翻訳と合致したら選択する
        if question.text not in hist:
            answers[0].click()
            print('Choice: ', end='')
            for i, answer in enumerate(answers):
                text = answer.get_attribute('value')
                hist.setdefault(question.text, []).append(text)
                if text in guess or guess in text:
                    answer.click()
                print(text, end=", ")
            print(end='')
        else:
            tmp = []
            for i, answer in enumerate(answers):
                if answer.get_attribute('value') in hist[question.text]:
                    tmp.append(i)

            hist[question.text] = []
            for i in tmp:
                hist.setdefault(question.text, []).append(answers[i].get_attribute('value'))

            print('Narrow down:', hist[question.text], end='')
            answers[random.choice(tmp)].click()

        # submit
        submit = driver.find_element_by_id('ans_submit')
        submit.submit()

        time.sleep(2)
        # 正解と不正解の判定
        try:
            driver.find_element_by_id('true_msg')
            print('\n正解です')
        except:
            print("\n不正解です")

        # 次へすすめる場合は進む、なければユニット終了
        try:
            next = driver.find_element_by_class_name('btn-problem-next')
            next.submit()
        except:
            break


if __name__ == '__main__':
    options = Options()
    options.binary_location = '/usr/bin/google-chrome-stable'
    options.add_argument('--headless')
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get('https://w5.linguaporta.jp/user/seibido/index.php')
    driver.set_window_size(720, 1280)

    print('Input ID')
    id = input()
    print('Input Password')
    password = input()

    login(id, password)

    print('Input start number(1-25の場合は1, 126-150の場合は126)')
    num = int(input())
    print('Input finish unit number(976-1000を最後にするなら1000)')
    end = int(input())

    while(True):
        selectCocet()
        print('Now unit is', str(num)+'-'+str(num+24))
        selectUnit(num)
        Answer()
        if num == (end-24):
            break
        num += 25


    print('All unit was cleared. Exit.')
    driver.quit()  # ブラウザーを終了する。
