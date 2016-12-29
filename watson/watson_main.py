from keras.optimizers import adam
from watson.qa_eval import Evaluator
import numpy as np

datapath_insurance = '/home/havikbot/PycharmProjects/data/watson_insurance/'
datapath_tele =  '/home/havikbot/PycharmProjects/data/watson_tele/'

class configs():
    config = None
    def __init__(self, dataset, model):
        self.config = {
            'n_words': 22353,   # need to be set from word count by word2vec embedding file
            'question_len': 75,
            'answer_len': 75,

            'training': {
                'batch_size': 100,
                'nb_epoch': 100,
                'validation_split': 0.2,
                },

            'similarity': {
                'mode': 'cosine_tf',
                'gamma': 1,
                'c': 1,
                'd': 2,
                'dropout': 0
                }
        }

        if model == 'embedding':
            self.config['margin'] = 0.05
            self.config['model'] = 'Embedding'
        elif model == 'convolutional':
            self.config['margin'] = 0.15
            self.config['model'] = 'Convolutional'
        elif model == 'convLSTM':
            self.config['margin'] = 0.05
            self.config['model'] = 'ConvolutionalLSTM'
        else:
            print('Not a proper model type')

        if dataset == 'insurance':
            self.config['dataset'] = 'insurance'
            self.config['datapath'] = datapath_insurance
            self.config['initial_embed_weights'] = datapath_insurance + 'word2vec_100_dim_w8_mc3_skip_ins'
        else:
            self.config['dataset'] = dataset
            self.config['datapath'] = datapath_tele
            self.config['initial_embed_weights'] = datapath_tele + 'word2vec_100_dim_w8_mc3_skip_tele'


config_class = configs('insurance', 'embedding')
conf = config_class.config
from keras_models import EmbeddingModel, ConvolutionModel, ConvolutionalLSTM
opt = adam(clipnorm=1.)
evaluator = Evaluator(conf, model=EmbeddingModel, optimizer=opt)

# train the model
best_loss = evaluator.train()

# evaluate mrr for a particular epoch
evaluator.load_epoch(best_loss['epoch'])
evaluator.get_score(verbose=True)
