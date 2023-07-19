# -*- coding: utf-8 -*-
"""DNN_sentimental_analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mberLbYexrcr6_uU3PSkOSQLqfK_KS3_
"""

import numpy as np
import pandas as pd

train = pd.read_csv("ratings_train.txt", header=0, delimiter="\t", quoting=3)
train

"""#### 네이버 영화 리뷰 데이터로 감성분류를 할건데,
#### 간단한 전처리를 해줘야 딥러닝 모델에 들어갈 수 있다.
"""

!pip install konlpy

import re
from konlpy.tag import Okt

okt = Okt()

text = "안녕하세요."

okt.morphs(text, stem=True)

okt.morphs(text, stem=False)

"""1. 문자열을 추출
2. 정규표현식으로 필터링. (특수문자, 이모티콘)
3. stopword 제거해서 리스트를 만들었다.
"""

stop_word = ['은', '는','이', '가','이다']

def preprocessing(content, okt):
    content_re = re.sub("[^가-힣 ]", "",content)
    content_word = okt.morphs(content_re, stem=True)

    word_list = []

    for word in content_word:
        if word not in stop_word:
            word_list.append(word)

    return word_list

preprocessing("안녕하세요 HJK입니다. 감성분류를 하고 있습니다.", okt)

# Data preprocessing

train_review = [] # empty list for data preprocessing

for review in train['document'][:500]: # only 5 million words since not possible for 15 million words.
    train_review.append(preprocessing(review, okt)) # preprocessing function with reviews and stemming.
                                                    # append the return values, stack them at the train reviews.
                                                    # Then, train review becomes 2d array.

train_review

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer() #tool that changes words into numbers.

#Defining the overall orders by tokenizers.
#Define numbers by words
#Construct dict for word - numbers.
tokenizer.fit_on_texts(train_review)

# change words into numbers by tokenizers for each reviews.
train_sequence = tokenizer.texts_to_sequences(train_review)
train_sequence # 확인

#Deeplearning model's input size has a length
# Each reviews have different lengths.

# if input size > 17, then can not enter.
# Fit the size -> fill in with padding.

train_input = pad_sequences(train_sequence, maxlen=8, padding="post")

# maxlen=8: paddin, length size of 8.
# padding="post": fill in with 0 from the back.
train_input

# Target val.

train_label = np.array(train['label'])
train_label

#Constructing a model.

# Function to split the data in an 8(training):2(evaluation) ratio
from sklearn.model_selection import train_test_split

# Training data, evaluation data, training answers, evaluation answers
# Feature data, answer data, val data size ratio
x_train, x_val, y_train, y_val = train_test_split(train_input, train_label[:500], test_size=0.2)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten,Dense, Embedding

model = Sequential() # Define model object
word_size = len(tokenizer.word_index)+1
model.add(Embedding(word_size, 128, input_length = 8)) # Word size, 128 output, 8 size input
model.add(Flatten()) # If the embedding result is 2D, flatten it to make it a 1D vector
model.add(Dense(1,activation='relu')) # Pass through the activation function relu to get an output of 1
model.compile(optimizer="adam",loss="binary_crossentropy", metrics =['accuracy'])
             # Model configuration section, set optimizer to adam, compute loss with binary_crossentropy,
             # Measure model performance with accuracy.

model.fit(x_train,y_train, epochs=5, batch_size = 32)

model.evaluate(x_val,y_val)

text = "이 영화 너무 다시볼거야 너무 재밌다"

re_text = preprocessing(text, okt) # Preprocessing: regular expression, stemming, stopword processing
text_data = []
text_data.append(re_text) # It must be made in the form of n x n, as there is only one data,
                          # It should go in like [[word list]].
                          # If there are 2 pieces of data, It should go in 2 x n like [[word list],[word list]].
text_seq = tokenizer.texts_to_sequences(text_data) # Convert word list to number list. It should be padded to a size of 8
text_seq = pad_sequences(text_seq, maxlen = 11, padding = "post")
model.predict(text_seq) # Evaluate positivity and negativity by inserting it into the model, negative towards 0, positive towards 1
                        # As only 500 sentences are currently entered, the accuracy is low.

"""LSTM 모델 사용하기"""

from tensorflow.keras.layers import LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten,Dense, Embedding
from tensorflow.keras.callbacks import EarlyStopping

model = Sequential()
model.add(Embedding(word_size, 128, input_length = 8)) #Embedding layer configuration
model.add(LSTM(units=128)) #Define LSTM model, units are the number of output features
model.add(Dense(1,activation="relu")) #Dense takes the output features of LSTM, passes through relu and outputs one.
model.compile(optimizer="adam",loss="binary_crossentropy", metrics =['accuracy'])
early = EarlyStopping(monitor = "val_loss" , mode = "min", verbose = 1, patience = 5)
model.fit(x_train,y_train, epochs=100, batch_size = 32, callbacks = [early],
          validation_split = 0.2) #Total learning epochs 5, batch size is 32

model.evaluate(x_val,y_val)

text = "이 영화 너무 다시볼거야 너무 재밌다"

re_text = preprocessing(text, okt) #Preprocessing: regular expression, stemming, stopword processing
text_data = []
text_data.append(re_text) #It must be made in the form of n x n, since there is only one data
                          #It should be entered like [[word list]]. If there are two data, it should go in as 2 x n like [[word list],[word list]].
text_seq = tokenizer.texts_to_sequences(text_data) #Convert the word list into a list of numbers
text_seq = pad_sequences(text_seq, maxlen = 8, padding = "post") #It should be padded to a size of 8.
model.predict(text_seq) #Put it in the model and evaluate positive/negative, the closer to 0, the more negative, the closer to 1, the more positive.
                        #As only 500 sentences are currently entered, the accuracy is low.