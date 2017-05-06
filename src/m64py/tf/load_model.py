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
from m64py.tf.data_prep import DataPrep

# Data Stuffs!!
dataset_paths = "/pub/dataset/mario/"
# input_filename = 'super_set.npz'
input_filename = 'mariokart64_dataset_0.npz'
input_files = os.path.join(dataset_paths, input_filename)
load = np.load(input_files)
imgs = load['images']
labels = load['labels']
dataset_examples = imgs.shape[0]
dataset_h = imgs.shape[1]
dataset_w = imgs.shape[2]
dataset_c = imgs.shape[3]
dataset_classes = labels.shape[1]
dataset_shape = imgs[0].shape
label_example = labels[0]
IMG_W = dataset_w
IMG_H = dataset_h
OUT_SHAPE = dataset_classes
print("Images: {}".format(imgs.shape))
print("Labels: {}".format(labels.shape))
print("Image shape: {}".format(dataset_shape))
print("Label: {}".format(label_example))

# Data Output Stuffs!!
#save_path = '/pub/models/mupen64/mariokart64/'
#save_dirname = 'outputmodel__'
#save_path = os.path.join(save_path, save_dirname)
save_path = '/pub/models/mupen'
save_filename = 'alphagriffin'
print(save_path)

batcher = data_prep(imgs, labels)
sess = tf.InteractiveSession()
checkpoint_file = tf.train.latest_checkpoint(save_path)
# filename = '/pub/models/mupen64/mariokart64/outputmodel__/alphagriffin-29901'
# filename2 = '/pub/models/mupen64/mariokart64/outputmodel__/alphagriffin-29901.data-00000-of-00001'
# filename3 = '/pub/models/mupen64/mariokart64/outputmodel__/alphagriffin-29901.index'
print("Checkpoint File: {}".format(checkpoint_file))
meta_path = checkpoint_file + ".meta"
new_saver = tf.train.import_meta_graph(meta_path)
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
# init_op = tf.get_collection_ref('init_op')[0]
# print(init_op.name)


test_batch = batcher.next_batch(42)
loss_value = sess.run(loss, feed_dict={x:test_batch[0], y_: test_batch[1], keep_prob: 1.0})
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
        batch = batcher.next_batch(batch_size, True)
        train.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.65})
        # if i % 100 == 0:
        #     step = sess.run(global_step)
        #     loss_value = sess.run(loss, feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
        # test = epochs = batcher.epochs_completed

        if i % 250 == 0:
            saver.save(sess, save_path + '/alphagriffin', global_step)

for i in range(50, 75):
    test_img = imgs[i]
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