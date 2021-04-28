#!/usr/bin/env python
#-*- coding:utf-8 -*-

# 4 tags for character tagging: B, E, M, S

import sys
sys.path.append("..")
from utils import string_utils
from utils.string_utils import clean_and_tokenize, is_punctuation, UnicodeBlock

from codecs import open
import argparse
import pandas as pd
import unicodedata
import re


class Preprocessor(object):
    def __init__(self):
        return
    
    def split_hashtag(self, s):
        res = ''
        for i in range(len(s)):
            if not s[i].isalnum():
                res += ' '
            elif (s[i].isupper())and(i < len(s)-1)and(s[i+1].islower()):
                res += ' ' + s[i]
            elif (s[i].islower())and(i < len(s)-1)and(s[i+1].isupper()):
                res += s[i] + ' '
            else:
                res += s[i]
        res = re.sub(' +', ' ', res)
        res = res.strip()
        return res

    def force_number_sep(self, line):
        seperated_li = re.findall(r'[0-9]+|\D+',line)
        separated_line = ' '.join(seperated_li)
        separated_line = re.sub(' +', ' ', separated_line) #squeeze space
        return separated_line

    def force_punctuation_sep(self, line):
        res = ''
        for char in line:
            if is_punctuation(char):
                res += ' ' + char + ' '
            else:
                res += char 
        res = re.sub(' +', ' ', res.strip())
        return res

    def squeeze_space(self, line):
        length = len(line)
        num_space = len(line.split(' '))-1
        if (num_space > float(length) / 3):
            return line.replace(' ', '')
        else:
            return line

    def pre_process(self, line):
        line = re.sub(r'\s+', ' ', line)
        line = line.strip()
        line = re.sub(' +', ' ', line)
        line = self.split_hashtag(line)
        line = self.squeeze_space(line)
        line = self.force_punctuation_sep(line)
        line = self.force_number_sep(line)
        line = line.lower()
        return line  


class FeatureGenerater(object):
    def __init__(self):
        self.block_generater = UnicodeBlock()
        return

    def generate_features(self, char, label):
        output = []
        output.append(char)
        output.append(int(is_punctuation(char)))
        output.append(int(char.isdigit()))
        output.append(self.block_generater.unicode_block(char))
        output.append(unicodedata.category(char))
        output.append(label)
        return '\t'.join([str(x) for x in output]) + '\n'


class Encoder(object):
    def __init__(self):
        self.featureGenerater = FeatureGenerater()
        self.preprocessor = Preprocessor()
        return

    def character_tagging(self, sentence):
        output_list = []

        # preprocess
        word_list = clean_and_tokenize(sentence)
        word_list = self.preprocessor.pre_process(' '.join(word_list)).split()

        # all_chars = ''.join(word_list)
        # char_idx = 0 #indicate the char's position in string all_chars
        for word in word_list:
            length = len(word)
            if length == 1:
                # pre_ngram = word
                # suc_ngram = word
                features = self.featureGenerater.generate_features(word, label = 'S')
                output_list.append(features)
                # char_idx += 1
            else:
                for i in range(length):
                    # pre_ngram = all_chars[max(0, char_idx-2) : char_idx+1] # the length of pre_gram is at most 3
                    # suc_ngram = all_chars[char_idx : min(len(all_chars), char_idx+3)]
                    if i == 0:
                        features = self.featureGenerater.generate_features(word[i], label = 'B')
                        output_list.append(features)
                    elif i == length - 1:
                        features = self.featureGenerater.generate_features(word[i], label = 'E')
                        output_list.append(features)
                    else:
                        features = self.featureGenerater.generate_features(word[i], label = 'M')
                        output_list.append(features)
                    # char_idx += 1
        output_list.append('\n')
        return output_list


class Decoder(object):
    def __init__(self):
        return

    def to_sentence(self, list_of_char_tag):
        output_sentence = ''
        for char, tag in list_of_char_tag:
            if tag == 'B':
                output_sentence += ' ' + char
            elif tag == 'M':
                output_sentence += char
            elif tag == 'E':
                output_sentence += char + ' '
            else: # tag == 'S'
                output_sentence += ' ' + char + ' '
        output_sentence = ' '.join(output_sentence.strip().split())
        return output_sentence

class Postprocessor(object):
    def __init__(self):
        return

    def post_process(self, line):
        return line