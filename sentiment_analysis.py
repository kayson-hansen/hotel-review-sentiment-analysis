from load_data import get_outputs
import tensorflow as tf
import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, InputLayer
from tensorflow.keras.regularizers import L2
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


def create_inputs_and_outputs(input_file, output_files):
    """ Takes a .npy input file of sentence embeddings and a list of files
    containing the reviews to get outputs from and generates numpy arrays X and Y.

    Args:
        input_file (String): a .npy file containing the sentence embeddings for the input reviews
        output_files (List[String]): a list containing the filenames that have all the input reviews

    Returns:
        X (nparray), Y (nparray): the inputs and outputs for the model
    """
    embeddings = np.load(input_file)
    ratings = get_outputs(output_files)

    m = embeddings.shape[0]
    n = embeddings.shape[1]
    # randomize data points so that each dataset is more evenly distributed across reviews from each hotel
    random.seed(10)
    reviews = []
    for i in range(m):
        reviews.append((embeddings[i], ratings[i]))
    random.shuffle(reviews)
    X = np.zeros((m, n))
    Y = np.zeros((m, 1))
    for i in range(m):
        X[i] = reviews[i][0]
        Y[i] = reviews[i][1]

    return X, Y


def train_neural_network_model(x_train, y_train):
    """ Given a set of inputs and outputs, train a neural network model using tensorflow

    Args:
        x_train (ndarray): train set inputs
        y_train (ndarray): train set outputs

    Returns:
        (tensorflow mode): trained neural network model
    """
    # n = number of input features
    n = x_train.shape[1]

    model = Sequential(
        [
            InputLayer(input_shape=(n, )),
            Dense(units=48, activation='relu', name='layer2'),
            Dense(units=20, activation='relu', name='layer3'),
            Dense(units=10, activation='relu', name='layer4'),
            Dense(units=1, activation='sigmoid', name='output')
        ]
    )

    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.05)
    )

    model.fit(
        x_train, y_train,
        epochs=3, batch_size=64
    )

    return model


def train_logistic_regression_model(x_train, y_train):
    """ Given a set of inputs and outputs, train a logistic regression model using tensorflow

    Args:
        x_train (ndarray): train set inputs
        y_train (ndarray): train set outputs

    Returns:
        (tensorflow model): trained logistic regression model
    """
    # n = number of input features
    n = x_train.shape[1]

    model = Sequential(
        [
            InputLayer(input_shape=(n, )),
            Dense(units=1, activation='sigmoid',
                  name='output', kernel_regularizer=L2(0.01))
        ]
    )

    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.05)
    )

    model.fit(
        x_train, y_train,
        epochs=3, batch_size=64
    )

    return model


def evaluate_model(input_filename, output_filenames, algorithm):
    X, Y = create_inputs_and_outputs(
        input_filename, output_filenames)
    m = X.shape[0]

    # splits are 80/10/10 train/cross-validation/test
    m1 = int(m * 8/10)
    m2 = int(m * 9/10)
    x_train = X[:m1, :]
    x_cv = X[m1:m2, :]
    x_test = X[m2:m, :]
    y_train = Y[:m1, :]
    y_cv = Y[m1:m2, :]
    y_test = Y[m2:m, :]

    if algorithm == 'neural network':
        model = train_neural_network_model(x_train, y_train)
    elif algorithm == 'logistic regression':
        model = train_logistic_regression_model(x_train, y_train)

    # evaluate model on train set
    train_set_predictions = model.predict(x_train)
    train_set_yhat = np.zeros_like(train_set_predictions)
    for i in range(len(x_train)):
        if train_set_predictions[i] >= 0.5:
            train_set_yhat[i] = 1
        else:
            train_set_yhat[i] = 0
    print("Train set accuracy: ", accuracy_score(y_train, train_set_yhat))
    print("Train set precision: ", precision_score(y_train, train_set_yhat))
    print("Train set recall: ", recall_score(y_train, train_set_yhat))

    # evaluate model on cross-validation set
    cv_set_predictions = model.predict(x_cv)
    cv_set_yhat = np.zeros_like(cv_set_predictions)
    for i in range(len(x_cv)):
        if cv_set_predictions[i] >= 0.5:
            cv_set_yhat[i] = 1
        else:
            cv_set_yhat[i] = 0
    print("Cross-validation set accuracy: ", accuracy_score(y_cv, cv_set_yhat))
    print("Cross-validation set precision: ",
          precision_score(y_cv, cv_set_yhat))
    print("Cross-validation set recall: ", recall_score(y_cv, cv_set_yhat))

    # evaluate model on test set
    test_set_predictions = model.predict(x_test)
    test_set_yhat = np.zeros_like(test_set_predictions)
    for i in range(len(x_test)):
        if test_set_predictions[i] >= 0.5:
            test_set_yhat[i] = 1
        else:
            test_set_yhat[i] = 0
    print("Test set accuracy: ", accuracy_score(y_test, test_set_yhat))
    print("Test set precision: ", precision_score(y_test, test_set_yhat))
    print("Test set recall: ", recall_score(y_test, test_set_yhat))

    # create confusion matrix from model predictions
    cm = confusion_matrix(y_train, train_set_yhat)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title('Confusion matrix')
    plt.xlabel('Predicted sentiment')
    plt.ylabel('True sentiment')
    plt.show()
