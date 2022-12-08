from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import spacy
import time
import csv
import os
import math
import re
from collections import Counter

WORD = re.compile(r"\w+")


data = list

# opens the browser with the given link
def open_browser():
    browser.get('http://p-bot.ru/en/index.html')
    time.sleep(5)

# selects the chat window based on the xpath
def open_chat():
    user_name = 'Emerson AI'
    links = browser.find_elements("xpath", "//input[@id='user_request']")
    for link in links:
        if "Emerson AI" in link.get_attribute("innerHTML"):
            link.click()
            break


def read_data(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        d = list(reader)[1:]
    return d


# preprocessing the text for similarity comparision

def preprocess_word(word):
    word = word.lower()
    res = ''
    for s in word:
        if s.isalpha() or s == ' ' or s.isnumeric():
            res += s
    return res

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)


if __name__ == '__main__':
    start_time = time.time()
    load_dotenv()
    fp = webdriver.FirefoxProfile(os.environ.get('FIREFOX_PROFILE_PATH'))
    browser = webdriver.Firefox(executable_path='drivers/geckodriver', firefox_profile=fp)
    open_browser()
    #open_chat()
    time.sleep(5)

    #data = read_data("domain_knowledge.csv")
    #data = read_data("chatbot_memory.csv")
    #data = read_data("chat_patterns.csv")
    #data = read_data("qa_interactions.csv")
    data = read_data("alltestcases.csv")


    expected_responses = None
    positive_results = 0
    negative_results = 0
    for i in range(len(data)):
        in_message = data[i][0]
        expected_responses = data[i][1].split("|")

        #clear the text field
        browser.find_element(By.XPATH, "//input[@id='user_request']").clear()

        # Input the message into the chat textbox
        message_box = browser.find_element(By.XPATH, "//input[@id='user_request']")
        message_box.send_keys(in_message)

        # Send the input message
        send_button = browser.find_element(By.XPATH, "//button[@id='btnSay']")
        send_button.click()

        # Extract the response to the input message
        last_response_xpath = "/html[1]/body[1]/div[6]/div[4]/div[2]"

       
        time.sleep(3)

        actual_response = None
        try:
            response = browser.find_element(By.XPATH, last_response_xpath);
            actual_response = response.text.split(': ')[1]
        except:
            actual_response = in_message

        
        print(actual_response)

        # Perform cosine similarity check
        nlp = spacy.load('en_core_web_sm')

        #actual_response = preprocess_word(actual_response)
        actual_out = nlp(actual_response)
        similarity = 0
        for expected_response in expected_responses:
            vector1 = text_to_vector(expected_response)
            vector2 = text_to_vector(actual_response)
            cosine = get_cosine(vector1, vector2)
            similarity = max(similarity,cosine)

        print("Test case %s:" % str(i))
        print("Input: %s" % in_message)
        print("Output: %s" % actual_response)
        print("Similarity: %s" % similarity)
        if similarity > 0.56:
            positive_results += 1
            print("True")
        else:
            negative_results += 1
            print("False")
        print()
        
        

    end_time = time.time()
    print("Total positive results: %d" % positive_results)
    print("Total negative results: %d" % negative_results)
    print("Total time consumed: %d secs" % (end_time - start_time))

    browser.quit()
