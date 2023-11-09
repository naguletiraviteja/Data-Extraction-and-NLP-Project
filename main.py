import nltk
import requests
from bs4 import BeautifulSoup
import pandas as pd
from nltk import word_tokenize, sent_tokenize
import os
from nltk.stem import SnowballStemmer
from autocorrect import Speller
from nltk.corpus import stopwords
import re

stop_words_nltk = set(stopwords.words('english'))

spell = Speller(lang='en')


def complex_words(word):
    count = 0
    if word[len(word) - 2:] == 'ed' or word[len(word) - 1:] == 'es':
        return False
    else:
        for i in word:
            if i in ['a', 'e', 'i', 'o', 'u']:
                count += 1
            else:
                pass
        if count > 2:
            return True
        return False


pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b', re.I)

# input = pd.read_excel('Input.xlsx')
# count = 0
# column_list = input.columns
# for i in range(len(input['URL'])):
#     url = input['URL'][i]
#     page = requests.get(url)
#     if page:
#         soup = BeautifulSoup(page.content, "html.parser")
#         title = soup.find("title")
#         with open(str(input['URL_ID'][count])+".txt", 'a', encoding='UTF-8') as test_run:
#             test_run.write('\n')
#             test_run.write(title.text.strip())
#             test_run.write('\n')
#         print(count+1,title.text.strip())
#         content = soup.find("div", class_="td-post-content")
#         article_text = content.find_all("p")
#         for j in article_text:
#             with open(str(input['URL_ID'][count])+".txt", 'a', encoding='UTF-8') as test_run:
#                 test_run.write('\n')
#                 test_run.write(j.text)
#                 test_run.write('\n')
#         count += 1
#         i+=1
#     else:
#         with open("404 error"+str(input['URL_ID'][count]) + ".txt", 'a', encoding='UTF-8') as test_run:
#             test_run.write('Page Not Found')
#         print("404 Error",count+1)
#         count+=1
#         i+=1

# output = pd.read_excel('Output Data Structure.xlsx')

stop_words = []
positive_words = []
negative_words = []
index = 0
for i in os.listdir('StopWords'):
    with open(r'StopWords/' + str(i), 'r') as data:
        for i in data.readlines():
            if '|' in i:
                stop_words.append(i.split('|')[0].lower().split('\n')[0])
            else:
                stop_words.append(i.lower().split('\n')[0])

with open(r'MasterDictionary/positive-words.txt', 'r') as positive:
    for i in positive.readlines():
        positive_words.append(i.lower().split('\n')[0])

with open(r'MasterDictionary/negative-words.txt', 'r') as negative:
    for i in negative.readlines():
        negative_words.append(i.lower().split('\n')[0])

output = pd.read_excel('Output Data Structure.xlsx')

for url_id in output['URL_ID']:
    try:
        words = []
        cleaned_words = []
        words_positive = []
        words_negative = []
        sentences = []
        syllable_count = 0
        complex_word_score = 0
        positive_score = 0
        negative_score = 0
        word_count = 0
        total_characters = 0
        personal_pronouns = []
        with open(str(url_id) + '.txt', 'r', encoding='UTF-8') as data:
            text = data.readlines()
            for i in text:
                if i != '\n':
                    parts = word_tokenize(i)
                    sentences.append(sent_tokenize(i))
                    personal_pronouns.append(pronounRegex.findall(i))
                    for i in parts:
                        i = spell(i)
                        words.append(i.lower())
                        if complex_words(i):
                            complex_word_score += 1
                        else:
                            pass
                        # Syllable count for each word
                        if i[len(i) - 2:] == 'ed' or i[len(i) - 1:] == 'es':
                            pass
                        else:
                            for j in i:
                                if j in ['a', 'e', 'i', 'o', 'u']:
                                    syllable_count += 1
                                else:
                                    pass
                        # total characters in text
                        for k in i:
                            total_characters += 1
            for i in words:
                i = spell(i)
                if i in stop_words:
                    pass
                else:
                    cleaned_words.append(i)

            for i in cleaned_words:
                if i in positive_words:
                    words_positive.append(i)
                elif i in negative_words:
                    words_negative.append(i)
            positive_score = len(words_positive)
            Negative_score = len(words_negative)

            # Word Count
            for i in cleaned_words:
                if (i in stop_words_nltk) or (i in ['.', ',', '?', '!']):
                    pass
                else:
                    word_count += 1
        if float(output.loc[index]['URL_ID']) == url_id:
            output.loc[output['URL_ID'] == url_id, 'POSITIVE SCORE'] = positive_score
            output.loc[output['URL_ID'] == url_id, 'NEGATIVE SCORE'] = Negative_score
            output.loc[output['URL_ID'] == url_id,'POLARITY SCORE'] = round(
                (positive_score - Negative_score) / (positive_score + Negative_score + 0.000001), 2)
            output.loc[output['URL_ID'] == url_id,'SUBJECTIVITY SCORE'] = round(
                (positive_score + Negative_score) / (len(set(cleaned_words)) + 0.000001), 2)
            output.loc[output['URL_ID'] == url_id,'AVG SENTENCE LENGTH'] = round((len(cleaned_words) / len(sentences)), 2)
            output.loc[output['URL_ID'] == url_id,'PERCENTAGE OF COMPLEX WORDS'] = round(complex_word_score / len(words), 2)
            output.loc[output['URL_ID'] == url_id,'FOG INDEX'] = round(
                0.4 * ((len(words) / len(sentences)) + (complex_word_score / len(words))), 2)
            output.loc[output['URL_ID'] == url_id,'AVG NUMBER OF WORDS PER SENTENCE'] = round(len(words) / len(sentences), 2)
            output.loc[output['URL_ID'] == url_id,'COMPLEX WORD COUNT'] = complex_word_score
            output.loc[output['URL_ID'] == url_id,'WORD COUNT'] = word_count
            output.loc[output['URL_ID'] == url_id,'SYLLABLE PER WORD'] = syllable_count
            output.loc[output['URL_ID'] == url_id,'PERSONAL PRONOUNS'] = len(personal_pronouns)
            output.loc[output['URL_ID'] == url_id,'AVG WORD LENGTH'] = round(total_characters / len(words), 2)
            index+=1

        else:
            print('Not matched')

            # print('------------------------------------')
            # print('Positive words:', positive_score)
            # print('Negative words', Negative_score)
            # print('Polarity Score', round((positive_score - Negative_score) / (positive_score + Negative_score + 0.000001),2))
            # print('Subjectivity Score', round((positive_score + Negative_score) / (len(set(cleaned_words)) + 0.000001),2))
            # print('Avg sentence length:', round((len(cleaned_words) / len(sentences)),2))
            # print('Percentage of Complex Words', round(complex_word_score / len(words),2))
            # print('Fog Index',round(0.4*((len(words) / len(sentences)) + (complex_word_score / len(words))),2))
            # print('Avg number of words in a sentence',round(len(words)/len(sentences),2))
            # print('Complex word count',complex_word_score)
            # print('Word Count',word_count)
            # print('syllable per word',syllable_count)
            # print('personal pronouns',len(personal_pronouns))
            # print('avg word length',round(total_characters/len(words),2))
            #
            # print('------------------------------------')

    except:
        if float(output.loc[index]['URL_ID']) == url_id:
            output.loc[output['URL_ID'] == url_id,'POSITIVE SCORE'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'NEGATIVE SCORE'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'POLARITY SCORE'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'SUBJECTIVITY SCORE'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'AVG SENTENCE LENGTH'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'PERCENTAGE OF COMPLEX WORDS'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'FOG INDEX'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'AVG NUMBER OF WORDS PER SENTENCE'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'COMPLEX WORD COUNT'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'WORD COUNT'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'SYLLABLE PER WORD'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'PERSONAL PRONOUNS'] = 'NA'
            output.loc[output['URL_ID'] == url_id,'AVG WORD LENGTH'] = 'NA'
            index += 1
            print(f'{i} is not available as website is not available')

output.to_excel('output.xlsx',index=False)