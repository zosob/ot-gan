import numpy as np
import tensorflow as tf
from tensorflow.contrib.framework.python.ops import arg_scope
from utils import nn

# //// discriminator ////
def disc_spec(x, init=False, nonlinearity='crelu', ema=None, **kwargs):

    with arg_scope([nn.conv2d, nn.dense], counters={}, init=init, weight_norm=True, ema=ema):

        x = nn.conv2d(x, 16, filter_size=[5,5], pre_activation=None)
        x = nn.conv2d(x, 32, filter_size=[5,5], pre_activation=nonlinearity, stride=[2, 2])
        x = nn.conv2d(x, 64, filter_size=[5,5], pre_activation=nonlinearity, stride=[2, 2])
        x = nn.conv2d(x, 128, filter_size=[5,5], pre_activation=nonlinearity, stride=[2, 2])
        xs = x.get_shape().as_list()
        x = tf.reshape(x, [-1, np.prod(xs[1:])])
        x = nn.dense(x, 128, pre_activation=nonlinearity)
        x /= tf.sqrt(tf.reduce_mean(tf.square(x),axis=1,keepdims=True)) # normalization for cosine distance

        # return the features
        return x

discriminator = tf.make_template('discriminator', disc_spec)


# //// generator ////
def gen_spec(batch_size, init=False, ema=None, **kwargs):
    u = tf.random_uniform(shape=(batch_size, 100), minval=-1., maxval=1.)

    with arg_scope([nn.conv2d, nn.dense], counters={}, init=init, weight_norm=True, ema=ema):

        x = nn.dense(u, 2*4*4*256, pre_activation=None)
        x,l = tf.split(x,2,1)
        x *= tf.nn.sigmoid(l) # gated linear unit, one of Alec's tricks
        x = tf.reshape(x, shape=(batch_size,4,4,256))
        x = tf.image.resize_nearest_neighbor(x, [8,8])
        x = nn.conv2d(x, 2*128, filter_size=[5,5], pre_activation=None)
        x, l = tf.split(x, 2, 3)
        x *= tf.nn.sigmoid(l)
        x = tf.image.resize_nearest_neighbor(x, [16,16])
        x = nn.conv2d(x, 2*64, filter_size=[5,5], pre_activation=None)
        x, l = tf.split(x, 2, 3)
        x *= tf.nn.sigmoid(l)
        x = tf.image.resize_nearest_neighbor(x, [32, 32])
        x = nn.conv2d(x, 2*32, filter_size=[5, 5], pre_activation=None)
        x, l = tf.split(x, 2, 3)
        x *= tf.nn.sigmoid(l)
        x = tf.nn.tanh(nn.conv2d(x, 3, filter_size=[5,5], pre_activation=None, init_scale=0.1))

        return x

generator = tf.make_template('generator', gen_spec)
