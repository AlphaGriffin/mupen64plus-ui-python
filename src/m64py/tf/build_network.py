#!/usr/bin/python
# Copyright (C) 2016 Alpha Griffin
# Copyright (C) 2017 Alpha Griffin

"""
Objective
---------
    build a more dynamic and easily tweakable TF frontend for eventual GUI.

Progress
--------
    2-25-17: Adding more decoration to functions for long term readability
    and use. Also making ready for the first complete run of TKart.

TODO
----
    * write a demo on how to go from start to finish. do a youtube video,
      build a docker. build a win exe. build wtf mac uses.
    * do a lot of catch variables for setup use... be verbose.
    * finish tensorboard dev output progess step.
    * finish distrubted gpu progess step. 
    * finish UML output image.

Target for master push
----------------------
    * produce the tutorial results of the MNIST lesson and the TKart lesson
      with this setup.
    * produce a Tensorboard output with a guide for setup
"""

import tensorflow as tf
from datetime import timedelta
# import numpy as np
import time
from tqdm import tqdm
import os

# import io
# for tensorboard output
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt

"""!!!DEV BUILD IN PROGRESS!!!"""


class Build_Adv_Network(object):
    """
    Dynamically create a Tensorflow Network from the given Input Options.
    """

    def __init__(self, dataset=None, init=True):
        """
        example
        -------
        >>> network = build_network.Build_Adv_Network(Mupen64_dataset)
        """
        self.dataset = dataset
        self.options = 0
        # this is in the wrong place ... i think
        self.step_size = 55  # int(self.dataset._num_examples / self.options.batch_size)

        # HERE WE GO!!

        # first start a new logDir folder DONT MESS THIS UP! ...
        # self.logDir()
        if init: self.init_new_graph();

    def logDir(self):
        path = self.options.logDir
        if os.path.isdir(path):
            num_logs = len(os.listdir(path))
            new_path = os.path.join(path,"log_{}".format(num_logs))
            os.mkdir(new_path)
            self.options.logDir = new_path
            print(new_path)

    def init_new_graph(self):
        self.build_default_values('/gpu:0')
        print("New Network is prepared for processing!")

    ###################################################################
    """This is bassically the init."""
    ###################################################################

    def build_default_values(self, worker):
        """
        This builds out the model from the options for a TF Graph

        Param
        -----
        worker: "/gpu:0"
            TODO:
            x = [y for y in worker.split(',')]
            if len(x) > 1:
                we have a distributed network
            else:
                we have a single computer
        """
        # with tf.device(tf.train.replica_device_setter(worker_device=worker, cluster=cluster)):
        # with tf.device(worker):

        """Start a Full Graph Scope"""
        with tf.variable_scope('Full_Graph'):
            """ Record Keeping """
            self.global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0),
                                               trainable=False)
            with tf.name_scope("learn_rate"):
                self.learn_rate = tf.train.exponential_decay(
                    0.1, self.global_step,
                    1e5, 0.96, staircase=True,
                    name="Learn_decay")
            tf.summary.scalar("learn_rate", self.learn_rate)

            """ Do Basic Steps """
            with tf.name_scope("input"):
                self.Input_Tensor_Images = tf.placeholder(tf.float32, [None, self.dataset.height, self.dataset.width,
                                                                       self.dataset.num_channels], name="Input_Tensor")
                self.Input_Tensor_Labels = tf.placeholder(tf.float32, [None, self.dataset.num_classes],
                                                          name="Input_Label")
                self.Input_True_Labels = tf.argmax(self.Input_Tensor_Labels, dimension=1)
                self.x_image = self.Input_Tensor_Images  # current default layer

            with tf.name_scope("keep_prob"):
                self.keep_prob = tf.placeholder(tf.float32)  # new feature goes with the dropout option

            """ Do Advanced Steps """
            with tf.name_scope("adv_steps"):
                self.convlayerNames, self.Conv_layers, self.Conv_weights = self.BUILD_CONV_LAYERS()  ## BUILD LAYERS
                self.x_image, self.features = self.flatten_layer(self.x_image)  ## SWITCH TO FC LAYERS
                self.fclayerNames, self.fc_layers = self.BUILD_FC_LAYER(self.options.fc_layers)  # build FC LAYERS
                # this is used but i dont know what to call it.

        with tf.name_scope("softmax"):
            self.Output_True_Layer = tf.nn.softmax(self.x_image, name="Final_Output")
        tf.summary.histogram('activations', self.Output_True_Layer)

        """ Working Maths """
        """ Variables """
        with tf.name_scope("Training_Methods"):
            with tf.name_scope("cross_entropy_softmax"):
                self.cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=self.x_image,
                                                                             labels=self.Input_Tensor_Labels)
                self.entropy_loss = tf.reduce_mean(self.cross_entropy)
            tf.summary.scalar("cross_entropy", self.entropy_loss)

            with tf.name_scope('Entropy_Optimizer_Train'):
                self.train_ent_loss = tf.train.AdamOptimizer(learning_rate=self.learn_rate).minimize(self.entropy_loss)

            with tf.name_scope('train'):
                self.cost = tf.reduce_mean(tf.square(tf.subtract(self.Input_Tensor_Labels, self.x_image)))
                training_vars = tf.add_n([tf.nn.l2_loss(v) for v in tf.trainable_variables()]) * 0.001
                self.loss = self.cost + training_vars
            tf.summary.scalar("train_cost", self.loss)
            with tf.name_scope('Dropout_Optimizer_Train'):
                 self.train_drop_loss = tf.train.AdamOptimizer(learning_rate=self.learn_rate).minimize(self.loss)
                # self.train_drop_loss = tf.train.AdagradOptimizer(learning_rate=self.learn_rate).minimize(self.loss)

        """ Finishing Steps """
        with tf.name_scope("accuracy"):
            with tf.name_scope('correct_prediction'):
                self.Output_True_Labels = tf.argmax(self.Output_True_Layer, dimension=1)
                self.correct_prediction = tf.equal(self.Output_True_Labels, self.Input_True_Labels)
            with tf.name_scope('accuracy'):
                self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))
        tf.summary.scalar('accuracy', self.accuracy)

        """This is some tricks to push our matplotlib graph inside tensorboard"""
        # with tf.variable_scope('Matplotlib_Input'):
        # Matplotlib will give us the image as a string ...
        #    self.matplotlib_img = tf.placeholder(dtype=tf.string.real_dtype, shape=[])
        # ... encoded in the PNG format ...
        #    my_img = tf.image.decode_png(self.matplotlib_img, 4)
        # ... that we transform into an image summary
        #    self.img_summary = tf.summary.image(
        #        'matplotlib_graph'
        #        , tf.expand_dims(my_img, 0)
        #    )

        """ Initialize the session """
        self.init_op = tf.global_variables_initializer()

        """create summary op"""
        self.merged = tf.summary.merge_all()

        """ Create Saver object"""
        self.saver = tf.train.Saver(
            var_list={"{}".format(v): v for v in [tf.model_variables()]},
            write_version=tf.train.SaverDef.V2,
            sharded=True,
            keep_checkpoint_every_n_hours=1.0
        )

        """ Create Supervisor Object"""
        """
        self.bossMan = tf.train.Supervisor(is_chief=True,
                                           logdir=self.options.logDir,
                                           checkpoint_basename='alpha.griffin',
                                            init_op =  self.init_op,
                                           summary_op=self.merged,
                                           saver=self.saver,
                                           global_step=self.global_step,
                                           save_model_secs=60)
        """
        print("We are passing this test.")

    ###################################################################
    """These are all impelemented in the above build function"""
    ###################################################################
    """
    def build_plotter(self, sess, input_images,):
        #setup matplotlib output for tensorboard
        inputs = np.array([ [(i - 1000) / 100] for i in input_images ])
        y_true_res, y_res = sess.run([y_true, y], feed_dict={ x: inputs
        })
        # We plot it using matplotlib
        # (This is some matplotlib wizardry to get an image as a string,
        # read the matplotlib documentation for more information)
        plt.figure(1)
        plt.subplot(211)
        plt.plot(inputs, y_true_res.flatten())
        plt.subplot(212)
        plt.plot(inputs, y_res)
        imgdata = io.BytesIO()
        plt.savefig(imgdata, format='png')
        imgdata.seek(0)
        # We push our graph into TensorBoard
        plot_img_summary = sess.run(img_summary, feed_dict={
            img_strbuf_plh: imgdata.getvalue()
        })
        sw.add_summary(plot_img_summary, i + 1)
        plt.clf()


    #depricated for use in tf.Supervisor
    def save_graph(self, session, path=None):
        #Manually save the graph
        saver = self.saver
        if path is None:
            path = self.options.save_path + 'StupidAbritraryFileName'
        saver.save(sess=session, save_path=path)
    """

    def BUILD_CONV_LAYERS(self):
        layers = self.options.conv_layers
        self.conv_layers_nameslist = []
        self.conv_layers_list = []
        self.conv_layers_wlist = []
        self.conv_layers_blist = []
        start_shape = self.x_image
        reducing_shape = 0
        last_num_f = 0
        if self.options.verbose: print("Building Conv Layers");
        for layer in range(layers):
            f_size = self.options.f_size
            num_f = 16 * (layer + 1)
            if layer == 0:
                img = start_shape
                channel = self.dataset.num_channels
            elif layer > 0:
                img = reducing_shape
                channel = last_num_f
                if self.options.verbose: print("LAST NUMBER OF FILERS = INPUT CHANNELS =  %s" % channel)

            last_num_f = num_f
            if self.options.verbose: print("NEW NUMBER OF Channels = %s" % channel)
            reducing_shape, w, b = self.new_conv_layer(input=img,
                                                       filter_size=f_size,
                                                       chan=channel,
                                                       num_filters=num_f)
            layer_name = "convLayer_%s" % layer
            with tf.name_scope(layer_name):
                with tf.name_scope("weights"):
                    tf.summary.histogram("weights", w)
                with tf.name_scope("biases"):
                    tf.summary.histogram('biases', b)
                #with tf.name_scope("logits"):
                #    tf.summary.histogram('pre_activations', reducing_shape)
            self.conv_layers_nameslist.append(layer_name)
            self.conv_layers_list.append(reducing_shape)
            self.conv_layers_wlist.append(w)
            self.conv_layers_blist.append(b)
            self.x_image = reducing_shape
            if self.options.verbose: print("done with layer: %s" % layer)
            if self.options.verbose: print("#: Finished building %s:\n%s\n:##:\n" % (layer_name, self.x_image))

        if self.options.verbose: print("Finished Building %s Conv Layers" % layers);
        return self.conv_layers_nameslist, self.conv_layers_list, self.conv_layers_wlist

    def BUILD_FC_LAYER(self, layers):
        self.fc_layers_nameslist = []
        self.fc_layers_list = []
        self.fc_layers_wlist = []
        self.fc_layers_blist = []
        if self.options.verbose: print("# input features size = %s" % self.features)
        # first time thru options
        input = self.features
        output = self.options.fc_size
        use_reLu = True
        use_Drop = True
        if self.options.verbose: print("Building Fully Connected Layers");
        for layer in range(layers):
            if layers == 0:  ## this is right ... just seems wrong becuase # of convs up... # of input fc goes down
                layer_shape = layer.get_shape()
                num_features = layer_shape[1:4].num_elements()
                self.features = num_features
            if layer > 0:  # if not first time through
                input = output
                output = int(self.options.fc_size / (layer + 1))

            if layer == layers - 1:  # if last time through
                output = self.dataset.num_classes
                use_reLu = False  # dont use on the last time thru
                use_Drop = False

            if self.options.verbose: print(" input layers: %s" % input)
            if self.options.verbose: print(" output layers: %s" % output)
            self.x_image, w, b = self.new_fc_layer(input=self.x_image,
                                                   num_inputs=input,
                                                   num_outputs=output,
                                                   use_relu=use_reLu,
                                                   use_drop=use_Drop)
            layer_name = "fullyLayer_%s" % layer
            with tf.name_scope(layer_name):
                with tf.name_scope("weights"):
                    tf.summary.histogram("weights", w)
                with tf.name_scope("biases"):
                    tf.summary.histogram('biases', b)
                # with tf.name_scope("logits"):
                    # tf.summary.histogram('pre_activations', self.x_image)
            self.fc_layers_nameslist.append(layer_name)
            self.fc_layers_list.append(self.x_image)
            self.fc_layers_wlist.append(w)
            self.fc_layers_blist.append(b)
            if self.options.verbose: print("building %s:\n%s" % (layer_name, self.x_image))
        if self.options.verbose: print("Finished Building %s Fully Connected Layers" % layers);
        return self.fc_layers_nameslist, self.fc_layers_list

    def new_weights(self, shape):
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05), name="weight")

    def new_biases(self, length):
        return tf.Variable(tf.constant(0.05, shape=[length]), name="bias")

    def new_conv_layer(self, input, filter_size, chan, num_filters, use_pooling=True):
        if self.options.verbose: print("#:\tStarting new conv Layer!...")
        X_shape = [filter_size, filter_size, chan, num_filters]
        weights = self.new_weights(shape=X_shape)
        if self.options.verbose: print("#: weights shape = %s" % X_shape)
        biases = self.new_biases(length=num_filters)

        """ THis is the MAGIC again... """
        layer = tf.nn.conv2d(input=input,  # This is the output of the last layer
                             filter=weights,  # this is a thing
                             strides=[1, 1, 1, 1],  # 1111 is NOT pooled MAX work
                             padding='SAME')  # input output transformation
        layer += biases  # Add biases
        if use_pooling:  # this skips pixels... saves time but skips things obviously
            layer = tf.nn.max_pool(value=layer,  # take the weights and bias together as an input
                                   ksize=[1, 2, 2, 1],  # stuff
                                   strides=[1, 2, 2, 1],  # 2 x 2 stride... could increase... check
                                   padding='SAME')  # i feel like this should already be in variable, but w/e
        layer = tf.nn.relu(layer)  # rectified linear Unit ... like a boss
        if self.options.verbose: print("Finished Building a conv Layer:\n\t%s" % layer)
        return layer, weights, biases

    def flatten_layer(self, layer):
        layer_shape = layer.get_shape()  # ASSERT layer_shape == [num_images, img_height, img_width, num_channels]
        num_features = layer_shape[1:4].num_elements()  # like a boss...
        layer_flat = tf.reshape(layer, [-1, num_features])  # yep...
        if self.options.verbose: print(layer_flat)
        print("## DummyScript.com")
        return layer_flat, num_features

    def new_fc_layer(self, input, num_inputs, num_outputs, use_relu=True, use_drop=False):
        weights = self.new_weights(shape=[num_inputs, num_outputs])  # set weights
        biases = self.new_biases(length=num_outputs)  # set number of OUTPUTS like give me top k or whatever...
        layer = tf.matmul(input, weights) + biases  # this is a #BIGMATH func
        if use_relu:
            layer = tf.nn.relu(layer)
        if use_drop:
            layer = tf.nn.dropout(layer, self.keep_prob)
        return layer, weights, biases

    ###################################################################
    """These are New ideas maybe not impelmented yet..."""

    ###################################################################
    # Our UA function
    def univAprox(self, x, hidden_dim=50):
        # The simple case is f: R -> R
        input_dim = 1
        output_dim = 1

        with tf.variable_scope('UniversalApproximator'):
            ua_w = tf.get_variable(
                name='ua_w',
                shape=[input_dim, hidden_dim],
                initializer=tf.random_normal_initializer(stddev=.1))
            ua_b = tf.get_variable(
                name='ua_b',
                shape=[hidden_dim],
                initializer=tf.constant_initializer(0.))
            z = tf.matmul(x, ua_w) + ua_b
            a = tf.nn.relu(z)  # we now have our hidden_dim activations

            ua_v = tf.get_variable(
                name='ua_v',
                shape=[hidden_dim, output_dim],
                initializer=tf.random_normal_initializer(stddev=.1))
            z = tf.matmul(a, ua_v)

        return z

    ###################################################################
    """this is Deprication Island... kept for no good reason"""
    ###################################################################
    """
    def feed_single(self, layer, image=None):
        if image is not None: img = image;
        else: img = self.test_IMAGE
        feed_dict = {self.Input_Tensor_Images: [img]}
        values = self.session.run(layer, feed_dict=feed_dict)
        return values, img

    def prob_dictionary(self, test=True, x_batch=None, y_true_batch=None, keep=1.0):
        in_tensor = self.x_image
        in_tensor_label = self.Input_Tensor_Labels
        keep_prob = self.keep_prob

        if not test:
            dataset_dictionary = {in_tensor:x_batch,
                                  in_tensor_label:y_true_batch,
                                  keep_prob:keep}
        else:
            dataset_dictionary = { in_tensor: self.test_batch[0],
                                  in_tensor_label:self.test_batch[1],
                                  keep_prob:keep }
        return dataset_dictionary

    def feed_dictionary(self, test=True, x_batch=None, y_true_batch=None):
        dataset = self.dataset
        #return { INPUT_TENSOR: INPUT_IMG, INPUT_TENSOR_LABEL:input_label, inuput_true_: Test_cls}
        in_tensor = self.x_image
        in_tensor_label = self.Input_Tensor_Labels
        in_true = self.Input_True_Labels
        if test is not True:
            dataset_dictionary = {in_tensor: x_batch,
                                  in_tensor_label: y_true_batch}
        else:
            dataset_dictionary = {in_tensor: self.test_batch[0],
                                  in_tensor_label: dataset.test_labels,
                                  in_true: dataset.test_cls}
        return dataset_dictionary

    def BATCH_VERIFY(self, input_tensor, labels, cls_true):
        batch_size = self.options.classify_batch_size
        num_images = len(input_tensor)
        cls_pred = np.zeros(shape=num_images, dtype=np.int)
        i = 0
        while i < num_images:
            j = min(i + batch_size, num_images) # j is remade frest every loop...
            feed_dict = {self.Input_Tensor_Images: input_tensor[i:j], self.Input_Tensor_Labels: labels[i:j]}
            cls_pred[i:j] = self.session.run(self.y_pred_cls, feed_dict=feed_dict)
            i = j
        correct = (cls_true == cls_pred)
        return correct, cls_pred
    """
    """
    TODO:
    def build_out_distrubited_graph(self):
        cluster = ""
        worker = ""
        server = ""

        # Calculate the learning rate schedule.
        num_batches_per_epoch = (cifar10.NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN /
                                 FLAGS.batch_size)

        decay_steps = int(num_batches_per_epoch * cifar10.NUM_EPOCHS_PER_DECAY)

        # Decay the learning rate exponentially based on the number of steps.
        lr = tf.train.exponential_decay(cifar10.INITIAL_LEARNING_RATE,
                                        global_step,
                                        decay_steps,
                                        cifar10.LEARNING_RATE_DECAY_FACTOR,
                                        staircase=True)

        gradient_cluster = []
        with tf.variable_scope(tf.get_variable_scope()):
            self.build_default_values()
        grads = average_gradients(tower_grads)
    """