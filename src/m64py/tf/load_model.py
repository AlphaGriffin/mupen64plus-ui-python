#!/usr/bin/env python

""" Mupen64 TF-DataPrep
Process the FilePath of Npz to Model, Model to Model, Model to Print

Alphagriffin.com
Eric Petersen @Ruckusist <eric.alphagriffin@gmail.com>
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
import tensorflow as tf
import numpy as np
from tqdm import tqdm
import data_prep

__author__ = "Eric Petersen @Ruckusist"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.1"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Prototype"

# tf stuffs
#from m64py.tf.data_prep import DataPrep

dataset_paths = "/pub/dataset/mario/"
input_filename = 'mariokart64_dataset_0.npz'
save_path = "/home/eric/.local/share/mupen64plus/model/mariokart64/mariokart64Model"

save_filename = '/Mupen64plus'
print(save_path)

data = data_prep.DataPrep()
dataset = data.load_npz(os.path.join(dataset_paths, input_filename))
sess = tf.InteractiveSession()
checkpoint_file = tf.train.latest_checkpoint(save_path)
print("Checkpoint File: {}".format(checkpoint_file))
meta_path = checkpoint_file + ".meta"
saver = tf.train.import_meta_graph(meta_path)
sess.run(tf.global_variables_initializer())
saver.restore(sess, checkpoint_file)

x = tf.get_collection('x_image')[0]
print(x.name)
y = tf.get_collection('y')[0]
print(y.name)
y_ = tf.get_collection('y_')[0]
print(y.name)
keep_prob = tf.get_collection('keep_prob')[0]
print(keep_prob.name)
loss = tf.get_collection('loss')[0]
print(loss.name)
train = tf.get_collection('train_op')[0]
print(train.name)
learn = tf.get_collection('learn_rate')[0]
print(learn.name)
global_step = tf.get_collection_ref('global_step')[0]
print(global_step.name)

test_batch = data.next_batch(42)
loss_value = sess.run(loss, feed_dict={x: test_batch[0], y_: test_batch[1], keep_prob: 1.0})
print("loss: {0:.4f}".format(loss_value))
cur_step = sess.run(global_step)
print("This model has seen {} iterations".format(cur_step))
retrain = True
if retrain:
    iters = 25000
    batch_size = 100
    print("Training For {}".format(iters))
    test = 0
    for i in tqdm(range(iters), desc="Training:"):
        batch = data.next_batch(batch_size, True)
        train.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.85})
        # this messes with tqdm
        # if i % 100 == 0:
        #     step = sess.run(global_step)
        #     loss_value = sess.run(
        # loss, feed_dict={
        #   x: batch[0], y_: batch[1], keep_prob: 1.0})
        # test = epochs = batcher.epochs_completed

        if i % 250 == 0:
            saver.save(sess, save_path + save_filename, global_step)

for i in range(50, 75):
    test_img = dataset[0][i]
    feed_dict = {x: [test_img], keep_prob: 1.0}
    joystick = sess.run(y, feed_dict)[0]
    output = [
            int(joystick[0] * 80),
            int(joystick[1] * 80),
            int(round(joystick[2])),
            int(round(joystick[3])),
            int(round(joystick[4])),
        ]
    # plt.imshow(test_img, interpolation='nearest')
    # plt.show()
    print("prediction: {}".format(output))
