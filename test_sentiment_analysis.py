from load_data import get_inputs, get_outputs, load_dataset
from web_scraper import file_paths
import tensorflow as tf
import numpy as np
import csv
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


X = get_inputs(["/users/kaysonhansen/cs129/HotelReviewData/TestFile.csv"])
Y = get_outputs(["/users/kaysonhansen/cs129/HotelReviewData/TestFile.csv"])
m = X.shape[0]
n = X.shape[1]

# splits are 60/20/20 train/cross-validation/test
m1 = int(m * 3/5)
m2 = int(m * 4/5)
x_train = X[:m1, :]
x_cv = X[m1:m2, :]
x_test = X[m2:m, :]
y_train = Y[:m1, :]
y_cv = Y[m1:m2, :]
y_test = Y[m2:m, :]


# Tensorflow Neural Network
model = Sequential(
    [
        Dense(units=96, activation='relu', name='layer1'),
        Dense(units=1, activation='sigmoid', name='layer3')
    ]
)
model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(),
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.01)
)

model.fit(
    x_train, y_train,
    epochs=10, batch_size=20
)


predictions = model.predict(X)
yhat = np.zeros_like(predictions)
for i in range(m):
    if predictions[i] >= 0.5:
        yhat[i] = 1
    else:
        yhat[i] = 0

# evaluate model on train set
train_accuracy = 0
for i in range(len(y_train)):
    if yhat[i] == y_train[i]:
        train_accuracy += 1
train_accuracy /= m1
print(train_accuracy)

# evaluate model on cross-validation set
cv_accuracy = 0
for i in range(len(y_cv)):
    if yhat[i] == y_cv[i]:
        cv_accuracy += 1
cv_accuracy /= (m2 - m1)
print(cv_accuracy)

# evaluate model on test set
test_accuracy = 0
for i in range(len(y_test)):
    if yhat[i] == y_test[i]:
        test_accuracy += 1
test_accuracy /= (m - m2)
print(test_accuracy)