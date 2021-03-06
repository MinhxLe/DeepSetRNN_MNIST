import tensorflow as tf
from tensorflow.contrib import rnn
from ops import linear
import os
from rnn_cell import BasicDeepSetLSTMCell

class BasicRNNClassifier(object):
    def __init__(self,config):
        self.config = config
        #TODO seperate out into functions 
        with tf.variable_scope(config.name):
            config = self.config
            self.X = tf.placeholder(tf.float32,\
                    [None,config.timesteps,config.input_size])
            X = tf.unstack(self.X,config.timesteps,1)
            self.y = tf.placeholder(tf.int32,[None]) 
            
            lstm_cell = rnn.BasicLSTMCell(config.hidden_size,forget_bias=1.0)
            rnn_outputs,states = rnn.static_rnn(lstm_cell,X,dtype=tf.float32)
            output = linear(rnn_outputs[-1],config.output_size)
    #prediction
            self._prediction = tf.nn.softmax(output)
            #loss
            self._loss = tf.reduce_mean((tf.losses.sparse_softmax_cross_entropy(self.y,self._prediction)))
            #optimizer
            #TODO can change optimizer 
            optimizer = tf.train.MomentumOptimizer(\
                    learning_rate=config.learning_rate,\
                    momentum=config.momentum,\
                    use_nesterov=True)
            self._optimize = optimizer.minimize(self._loss)
    @property
    def prediction(self):
        return self._prediction        
    @property
    def loss(self):
        return self._loss
    @property 
    def optimize(self):
        return self._optimize

class DeepSetRNNClassifier(object):
    def __init__(self,config):
        self.config = config
        #TODO seperate out into functions 
        with tf.variable_scope(config.name):
            config = self.config
            self.X = tf.placeholder(tf.float32,\
                    [config.batch_size,config.timesteps,config.input_size])
            X = tf.unstack(self.X,config.timesteps,1)
            self.y = tf.placeholder(tf.int32,[config.batch_size]) 
            lstm_cell = BasicDeepSetLSTMCell(config.hidden_size,forget_bias=1.0,alpha_contrib=config.alpha_contrib)
            rnn_outputs,states = rnn.static_rnn(lstm_cell,X,dtype=tf.float32)
            #TODO make this also a deepset(?)
            output = linear(rnn_outputs[-1],config.output_size)
            
            self._rnn_ouput = output
            #prediction
            self._prediction = tf.nn.softmax(output)
            #loss
            self._loss = tf.reduce_mean((tf.losses.sparse_softmax_cross_entropy(self.y,self._prediction)))
            #optimizer
            #TODO can change optimizer 
            optimizer = tf.train.MomentumOptimizer(\
                    learning_rate=config.learning_rate,\
                    momentum=config.momentum,\
                    use_nesterov=True)
            
            self._optimize = optimizer.minimize(self._loss)

    @property
    def prediction(self):
        return self._prediction        

    @property
    def loss(self):
        return self._loss
    
    @property 
    def optimize(self):
        return self._optimize



class BasicRNNSeq2Seq(object):
    def __init__(self,config):
        self.config = config
        #TODO seperate out into functions 
        with tf.variable_scope(config.name):
            config = self.config
            
            self.X = tf.placeholder(tf.float32,\
                    [None,config.timesteps,config.input_size])
            self.y = tf.placeholder(tf.int32,[None,config.timesteps]) 
            self.mask = tf.placeholder(tf.bool, [None,config.timesteps])
            
            lstm_cell1 = rnn.LSTMCell(config.hidden_size//2,forget_bias=1.0,\
                    activation=tf.nn.softsign)
            
            lstm_cell2 = rnn.LSTMCell(config.hidden_size,\
                    num_proj=config.output_size,forget_bias=1.0,\
                    activation=tf.nn.softsign)
            lstm_cell = rnn.MultiRNNCell([lstm_cell1,lstm_cell2])
            rnn_outputs,states = tf.nn.dynamic_rnn(lstm_cell,self.X,dtype=tf.float32)
            
            #prediction
            self._prediction = tf.nn.softmax(rnn_outputs) #last axis
            labels = tf.boolean_mask(self.y,self.mask)
            labels = tf.multiply(self.y, tf.cast(self.mask,self.y.dtype))
            #loss
            loss = tf.losses.sparse_softmax_cross_entropy(labels,rnn_outputs)
            loss = tf.multiply(loss,tf.cast(self.mask,loss.dtype))
            self._loss = tf.reduce_mean(loss) 
            #optimizer
            #TODO can change optimizer 
            optimizer = tf.train.MomentumOptimizer(\
                    learning_rate=config.learning_rate,\
                    momentum=config.momentum,\
                    use_nesterov=True)
            self._optimize = optimizer.minimize(self._loss)
    @property
    def prediction(self):
        return self._prediction        
    @property
    def loss(self):
        return self._loss
    @property 
    def optimize(self):
        return self._optimize
