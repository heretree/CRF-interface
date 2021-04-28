# -*- coding: utf-8 -*-
#
# 3 tags for character tagging: B, I, O

import sys
sys.path.append("..")
import pandas as pd
import numpy as np
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from utils import string_utils
from utils.string_utils import clean_and_tokenize, pos_tagging, stem, is_stopword

class FeatureGenerater(object):
    def __init__(self, dropout_ratio = 0):
        self.dropout_ratio = dropout_ratio
        np.random.seed(42)
        return

    def set_dropout_ratio(self, ratio):
        self.dropout_ratio = ratio
        return

    def normalize_aspect(self, line):
        word_list = line.split()
        word_list = [stem((word,'NN')) for word in word_list]
        word_list = [stem((word,'VB')) for word in word_list]
        return ' '.join(word_list)


    def generate_features(self, token, label):
        if self.dropout_ratio > 0:
            dropout = np.random.choice([0, 1], size = (1,), p=[1-self.dropout_ratio, self.dropout_ratio])[0]
        else:
            dropout = 0

        word = token[0]
        pos = token[1]
        
        output = []
        if dropout==1:
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
            output.append('[mask]')
        else:
            output.append(word)
            output.append(pos)
            output.append(stem(token))
            output.append(int(word == '@'))
            output.append(int(word == '#'))
            output.append(int(is_stopword(word)))
            output.append(word[:3])
            output.append(word[-3:])

        output.append(label)
        return '\t'.join([str(x) for x in output]) + '\n'


class Encoder(object):

    def __init__(self):
        self.feature_generater = FeatureGenerater()
    
    def find_match(self, s_list, p_list):
        """
        s_list: list of words. For example: ['this', 'is', 'a', 'sentence']
        p_list: list for words that need to find in s_list. For example: ['a', 'sentence']
        return: list of matched positions. For example: [[2, 4]]
        """
        match_list = []
        i = 0
        j = 0
        for i in range(len(s_list)):
            while ((i + j) < len(s_list)) and (j < len(p_list)) and (s_list[i+j] == p_list[j]):
                j += 1
            if j >= len(p_list): # all words in p_list were found in s_list
                match_list.append([i, i+j])
            j = 0
        return match_list

    def generate_tags(self, word_list, entity_list, tags):   
        for entity in set(entity_list): # allow multiple entities
            w_list = clean_and_tokenize(entity) # when the entity has multiple words
            match_positions = self.find_match(word_list, w_list) # match when w equals to word
            if match_positions == []:
                continue
            for pos in match_positions:
                pos_start = pos[0]
                pos_end = pos[-1]
                for i in range(pos_start, pos_end):
                    if (i == pos_start) and ((tags[i] == 'O') or (tags[i] == 'B')):
                        tags[i] = 'B'
                    elif (tags[i] == 'O') or (tags[i] == 'I'):
                        tags[i] = 'I'
                    else:
                        raise IndexError("{} can't be tagged twice".format(w_list[i]))
        return tags

    def tagging(self, sentence, aspect=None):
        word_list = clean_and_tokenize(sentence)
        token_list = pos_tagging(word_list)
        tags = ['O'] * len(word_list)

        if (aspect is not None) and (aspect is not np.nan):
            entity_list = aspect.split('/')
            try:
                tags = self.generate_tags(word_list, entity_list, tags)
            except IndexError as e:
                logging.info("IndexError in sentene: {}, aspect: {}".format(sentence, aspect))
                logging.info("Error: {}".format(e))
                return []


        output_list = []
        for i in range(len(word_list)):
            output_features = self.feature_generater.generate_features(token_list[i], label = tags[i])
            output_list.append(output_features)
        return output_list


class Decoder(object):

    def __init__(self):
        return

    def normalize_aspect(self, line):
        word_list = line.split()
        word_list = [stem((word,'NN')) for word in word_list]
        word_list = [stem((word,'VB')) for word in word_list]
        return ' '.join(word_list)


    def tag2word(self, list_of_word_tag):
        """
        list_of_word_tag: [(word, tag), (word, tag), ...]
        """

        output_list = []
        aspect = []
        for word_tag_pair in list_of_word_tag:
            word = word_tag_pair[0]
            tag = word_tag_pair[1]

            if (tag == 'B') and (aspect == []):
                aspect = [word]
            elif (tag == 'B') and (len(aspect) > 0):
                output_list.append(self.normalize_aspect(' '.join(aspect)))
                aspect = [word]
            elif (tag == 'I') and (len(aspect) > 0):
                aspect.append(word)
            elif (tag == 'O') and (len(aspect) > 0):
                output_list.append(self.normalize_aspect(' '.join(aspect)))
                aspect = []
            elif (tag == 'O') and (len(aspect) == 0):
                continue
            else:
                raise Exception("Result cannot be decoded: {}".format(list_of_word_tag))
        if len(aspect) > 0:
            output_list.append(self.normalize_aspect(' '.join(aspect)))
        
        return output_list

