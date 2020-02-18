# -*- coding: utf-8 -*-
# 模型训练

import numpy as np
from load_data import get_train_test_pd
from keras.utils import to_categorical
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import Input, Dense
from bert.extract_feature import BertVector

from att import Attention
from keras.layers import GRU, Bidirectional


# 读取文件并进行转换
train_df, test_df = get_train_test_pd()
bert_model = BertVector(pooling_strategy="NONE", max_seq_len=80)
print('begin encoding')
f = lambda text: bert_model.encode([text])["encodes"][0]

train_df['x'] = train_df['text'].apply(f)
test_df['x'] = test_df['text'].apply(f)
print('end encoding')

# 训练集和测试集
x_train = np.array([vec for vec in train_df['x']])
x_test = np.array([vec for vec in test_df['x']])
y_train = np.array([vec for vec in train_df['label']])
y_test = np.array([vec for vec in test_df['label']])
# print('x_train: ', x_train.shape)

# 将类型y值转化为ont-hot向量
num_classes = 14
y_train = to_categorical(y_train, num_classes)
y_test = to_categorical(y_test, num_classes)

# 模型结构：BERT + 双向GRU + Attention + FC
inputs = Input(shape=(80, 768,))
gru = Bidirectional(GRU(128, dropout=0.2, return_sequences=True))(inputs)
attention = Attention(32)(gru)
output = Dense(14, activation='softmax')(attention)
model = Model(inputs, output)

# 模型可视化
# from keras.utils import plot_model
# plot_model(model, to_file='model.png')

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(),
              metrics=['accuracy'])

# 模型训练以及评估
model.fit(x_train, y_train, batch_size=8, epochs=30)
model.save('people_relation.h5')
print(model.evaluate(x_test, y_test))

# 训练结果记录如下
# 训练集(train), loss: 0.0210, acc: 0.9951
# 测试集(test),  loss: 1.1099, acc: 0.7709