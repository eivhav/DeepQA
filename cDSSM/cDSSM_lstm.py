# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA
# Code base github.com/airalcorn2/Deep-Semantic-Similarity-Model


from keras import backend
from keras.optimizers import RMSprop, SGD
from keras.layers import Input, merge
from keras.layers.core import Dense, Lambda, Reshape, Dropout
from keras.layers import merge, LSTM
from keras.layers.convolutional import Convolution1D
from keras.models import Model, load_model
import time
from os.path import expanduser
import tensorflow as tf
tf.python.control_flow_ops = tf

class cDSSM_lstmClass():

    # System path
    HOME = expanduser("~")
    model_path = HOME + '/PycharmProjects/data/models/'

    training_model = None
    query_sem_model = None
    doc_sem_model = None
    pos_sim_model = None
    neg_sim_model = None
    query_conv_model = None
    doc_conv_model = None
    with_gamma = None

    # Model and training parameters
    LETTER_GRAM_SIZE = 3
    WINDOW_SIZE = 3
    TOTAL_LETTER_GRAMS = 0
    WORD_DEPTH = WINDOW_SIZE * TOTAL_LETTER_GRAMS
    nb_filters = 500
    lstm_size = 200
    J = 1
    FILTER_LENGTH = 1
    p = 0
    hinge_margin = 0.10
    gamma_log = -2.0

    # Different functions for calculating semantic similarity
    def R_tf(self, vects):
        (x, y) = vects
        return backend.dot(tf.nn.l2_normalize(x, dim=1), backend.transpose(tf.nn.l2_normalize(y, dim=1)))

    def R_th(self, vects):
        (x, y) = vects
        return backend.dot(x, backend.transpose(y)) / (x.norm(2) * y.norm(2))

    def GESD(self):
        gamma_value = 1
        c_value = 1.0
        dot = lambda a, b: backend.batch_dot(a, b, axes=1)
        l2_norm = lambda a, b: backend.sqrt(backend.sum(backend.square(a - b), axis=1, keepdims=True))
        euclidean = lambda x: 1.0 / (1.0 + l2_norm(x[0], x[1]))
        sigmoid = lambda x: 1.0 / (1.0 + backend.exp(-1.0 * gamma_value * (dot(x[0], x[1]) + c_value)))
        return lambda x: euclidean(x) * sigmoid(x)

    def cosine_lambda(self):
        return lambda x: backend.dot(tf.nn.l2_normalize(x[0], dim=1), backend.transpose(tf.nn.l2_normalize(x[1], dim=1)))


    def __init__(self, TOTAL_LETTER_GRAMS, J, backend_type):
        print("creating model")
        self.TOTAL_LETTER_GRAMS = TOTAL_LETTER_GRAMS
        self.J = J
        self.WORD_DEPTH = self.WINDOW_SIZE * self.TOTAL_LETTER_GRAMS

        # Input tensors holding the query, positive (clicked) document, and negative (unclicked) documents.
        # The first dimension is None because the queries and documents can vary in length.
        query = Input(shape = (None, self.WORD_DEPTH))
        pos_doc = Input(shape = (None, self.WORD_DEPTH))
        neg_doc = Input(shape = (None, self.WORD_DEPTH))

        # query_conv = Convolution1D(self.nb_filters, self.FILTER_LENGTH,  input_shape = (None, self.WORD_DEPTH), activation = "tanh")(query)
        # doc_conv = Convolution1D(self.nb_filters, self.FILTER_LENGTH, input_shape = (None, self.WORD_DEPTH), activation = "tanh")
        conv = Convolution1D(self.nb_filters, self.FILTER_LENGTH, input_shape = (None, self.WORD_DEPTH), activation = "tanh")

        query_conv = conv(query)
        pos_doc_conv = conv(pos_doc)
        neg_doc_conv = conv(neg_doc)

        f_rnn_query = LSTM(self.lstm_size, return_sequences=True, consume_less='mem')
        b_rnn_query = LSTM(self.lstm_size, return_sequences=True, consume_less='mem', go_backwards=True)

        f_rnn_doc = LSTM(self.lstm_size, return_sequences=True, consume_less='mem')
        b_rnn_doc = LSTM(self.lstm_size, return_sequences=True, consume_less='mem', go_backwards=True)

        qf_rnn = f_rnn_query(query_conv)
        qb_rnn = b_rnn_query(query_conv)
        question_pool = merge([qf_rnn, qb_rnn], mode='concat', concat_axis=-1)

        pf_rnn = f_rnn_doc(pos_doc_conv)
        pb_rnn = b_rnn_doc(pos_doc_conv)
        pos_answer_pool = merge([pf_rnn, pb_rnn], mode='concat', concat_axis=-1)

        nf_rnn = f_rnn_doc(neg_doc_conv)
        nb_rnn = b_rnn_doc(neg_doc_conv)
        neg_answer_pool = merge([nf_rnn, nb_rnn], mode='concat', concat_axis=-1)

        query_max = Lambda(lambda x: tf.reduce_max(x, reduction_indices=[1]))
        doc_max = Lambda(lambda x: tf.reduce_max(x, reduction_indices=[1]))

        query_sem = query_max(question_pool)
        pos_doc_sem = doc_max(pos_answer_pool)
        neg_doc_sem = doc_max(neg_answer_pool)

        hinge_sim_pos = merge([query_sem, pos_doc_sem], mode=self.GESD(), output_shape=lambda _: (None, 1))
        hinge_sim_neg = merge([query_sem, neg_doc_sem], mode=self.GESD(), output_shape=lambda _: (None, 1))

        hinge_loss = Lambda(lambda x: backend.relu((self.hinge_margin - x[0] + x[1])))
        prob = hinge_loss([hinge_sim_pos, hinge_sim_neg])

        self.training_model = Model(input=[query, pos_doc, neg_doc], output=prob)

        def y_pred_loss(y_true, y_pred):
            return y_pred

        self.training_model.compile(optimizer='adadelta', loss=y_pred_loss)

        # In addition we define models to extract the semantics vectors of query and pos documents
        self.query_sem_model = Model(input=query, output=query_sem)
        self.doc_sem_model = Model(input=pos_doc, output=pos_doc_sem)

        self.query_conv_model = Model(input=query, output=query_conv)
        self.doc_conv_model = Model(input=pos_doc, output=pos_doc_conv)

        self.query_lstm_model = Model(input=query, output=question_pool)
        self.doc_lstm_model = Model(input=pos_doc, output=pos_answer_pool)

        print("Model created")


    def save_model(self, my_model, params):
        my_model.save(self.model_path + 'model'+time.strftime("H:%d_%m_%Y")+'__'+str(params[0]) + 'samples_'+str(params[1])+'epoch_'+str(self.J)+'J_it' + str(params[2] + 1) + '.h5')
        print("Model saved")

    def load_model(self, path, only_weights):
        if only_weights:
            self.training_model.load_weights(path)
            print("Model weights loaded. ")
        else:
            self.training_model = load_model(path)
            print("Model loaded. ")



