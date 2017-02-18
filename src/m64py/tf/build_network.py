#!/usr/bin/python
#
# Copyright (C) 2016 Alpha Griffin
# fixme : add load and save functionality
# fixme : add in automatic tensorboard output
# fixme : output as much as possible to the options!
# Copyright (C) 2017 Alpha Griffin

"""  THIS HELPER WILL DEAL WITH THE NEW TENSORFLOW MODELS  """

import tensorflow as tf
from PIL import Image
import numpy as np
## the MNIST-10 BREAKOUT is the EXPECTED !NECESSARY! datalinks... will be clearer when i can be

## New adjustments will be made to accomedate the Tkart dataset!

class Build_Adv_Network(object):
    def __init__(self, options = None, model = None, init = True):
        self.model = model
        self.dataset = self.model
        self.options = options
        if self.options is None:
            self.options = self.model.options  
        self.step_size = int(self.dataset._num_examples / self.options.batch_size)
    
        ## HERE WE GO!!
        if init: self.init_new_graph();
        else:
            self.init_load_graph();
        # IF NOT Pull up an old one
    
    #def if model = none then show a list of available models in bank    
    def save_graph(self):
        saver = tf.train.Saver()
        save_path = self.options.save_path + '_best_validation_1_'
        saver.save(sess=self.session, save_path=save_path)
        
    def load_graph(self, graph=None):
        if graph is None: graph = '_best_validation_1_'
        saver = tf.train.Saver()
        save_path = self.options.save_path + graph
        saver.restore(sess=self.session, save_path=save_path)
        
    def prepare_image(self, img):
        #print("DEBUGS  1 {}".format(img))
        pil_image = Image.open(img)# open img
        x = pil_image.resize((200, 66), Image.ANTIALIAS) # resizes image in-place
        numpy_img = np.array(x)         # convert to numpy 
        #grey_numpy_image = self.make_BW(numpy_img)
        return numpy_img
        
    def que_graph(self, Image):
        try: vec = self.prepare_image(Image)
        except: vec = Image
        joystick = self.y.eval(feed_dict={self.x: [vec], self.keep_prob: 1.0})[0]
        output = [
                int(joystick[0] * 80),
                int(joystick[1] * 80),
                int(round(joystick[2])),
                int(round(joystick[3])),
                int(round(joystick[4])),
            ]
            
        for i in joystick:
            print("joystick: {}".format(i))
        print(output)
        return output
        
    def init_load_graph(self):
        self.session = tf.InteractiveSession()
        self.load_graph(self.session)
        
    def init_new_graph(self):
        self.session = tf.InteractiveSession()                
        self.build_default_values()        
        
        if self.options.verbose: print("New Network is prepared for processing!");
        
    def build_default_values(self):
        #self.session = tf.InteractiveSession()                           # Put a quarter in the TF machine
        
        """ Do Basic Steps """
        self.Input_Tensor_Images = tf.placeholder(tf.float32, [None, self.dataset.height, self.dataset.width, self.dataset.num_channels])
        self.Input_Tensor_Labels = tf.placeholder(tf.float32, [None, self.dataset.num_classes])
        self.Input_True_Labels   = tf.argmax(self.Input_Tensor_Labels, dimension=1) # dynamic instead of static... duh...
        self.x_image             = self.Input_Tensor_Images # current default layer
        self.keep_prob           = tf.placeholder(tf.float32) # new feature goes with the dropout option
        
        """ Do Advanced Steps """
        self.convlayerNames, self.Conv_layers, self.Conv_weights     = self.BUILD_CONV_LAYERS() ## BUILD LAYERS
        self.x_image, self.features                                  = self.flatten_layer(self.x_image) ## SWITCH TO FC LAYERS
        self.fclayerNames, self.fc_layers                            = self.BUILD_FC_LAYER(self.options.fc_layers) # build FC LAYERS
        train_vars                                                   = tf.trainable_variables()
        
        """ Create Placeholders """        
        self.Output_True_Layer = tf.nn.softmax(self.x_image)
        self.Output_True_Labels = tf.argmax(self.Output_True_Layer, dimension=1)
        
        """ Variables """
        self.cross_entropy  = tf.nn.softmax_cross_entropy_with_logits(logits=self.x_image, labels=self.Input_Tensor_Labels) 
        self.testing        = tf.square(tf.sub(self.Input_Tensor_Labels, self.x_image))
        self.cost           = tf.reduce_mean(self.testing)
        training_vars       = tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * self.options.L2NormConst
        self.loss           = self.cost + training_vars
        self.optimizer      = tf.train.AdamOptimizer(learning_rate=self.options.learning_rate).minimize(self.loss)
        
        """ PlaceHolders """
        self.correct_prediction = tf.equal(self.Output_True_Labels, self.Input_True_Labels)
        self.accuracy           = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))
        
        """ Initialize the session """
        self.session.run(tf.global_variables_initializer())   # Turn it on
        
        #self.long_haul()
        
    def long_haul(self):
        index = 0
        #step_size = int(self.dataset._num_examples / self.options.batch_size)
        for epoch in range(self.options.epochs):
            for i in range(63):
                batch = self.dataset.next_batch(self.options.batch_size)
                if len(batch[0]) is len(batch[1]):
                    self.optimize(batch,0.8)
            
                    if i % 100 == 0:
                      loss_value = self.get_lost(batch[0],batch[1])
                      print("epoch: {0} step: {1} loss: {2:.3}".format(epoch, index, loss_value))
                index += 1
        
    def optimize(self,batch, keep_prob):
        self.session.run(self.optimizer, feed_dict={self.Input_Tensor_Images: batch[0], self.Input_Tensor_Labels: batch[1], self.keep_prob: keep_prob})
        return True
        #train_step.run(feed_dict={self.x: batch[0], self.Y: batch[1], self.keep_prob: 0.8}) #! Hardcoded value
        
    def get_lost(self, x, y):
        loss_value = self.loss.eval(session=self.session,feed_dict={self.Input_Tensor_Images: x, self.Input_Tensor_Labels: y, self.keep_prob: 1.0})        
        return loss_value #! hardcoded value
        
    def BUILD_CONV_LAYERS(self):
        layers = self.options.conv_layers
        self.conv_layers_nameslist = []
        self.conv_layers_list = []
        self.conv_layers_wlist = []
        start_shape = self.x_image
        reducing_shape = 0
        last_num_f = 0
        if self.options.verbose: print("Building Conv Layers");
        for layer in range(layers):
            f_size = self.options.f_size
            num_f = 16 * (layer+1)
            if layer == 0:
                img = start_shape
                channel = self.dataset.num_channels
            elif layer > 0:
                img = reducing_shape
                channel = last_num_f
                print("LAST NUMBER OF FILERS = INPUT CHANNELS =  %s" % channel)
                
            last_num_f = num_f
            print("NEW NUMBER OF Channels = %s" % channel)
            reducing_shape, w = self.new_conv_layer(input       = img,
                                                    filter_size = f_size,
                                                    chan        = channel,
                                                    num_filters = num_f)
            layer_name = "convLayer_%s" % layer
            self.conv_layers_nameslist.append(layer_name)
            self.conv_layers_list.append(reducing_shape)
            self.conv_layers_wlist.append(w)
            self.x_image = reducing_shape
            print("done with layer: %s"%layer)
            #print("#: Finished building %s:\n%s\n:##:\n" % (layer_name, self.LAYER))
            
        #if self.options.verbose: print("Finished Building %s Conv Layers" % layers);
        return self.conv_layers_nameslist, self.conv_layers_list, self.conv_layers_wlist
    
    def BUILD_FC_LAYER(self, layers):
        self.fc_layers_nameslist = []
        self.fc_layers_list = []
        print("# input features size = %s" % self.features)
        #first time thru options
        input = self.features
        output = self.options.fc_size
        use_reLu  = True
        use_Drop = True
        if self.options.verbose: print("Building Fully Connected Layers");
        for layer in range(layers):
            if layers == 0:  ## this is right ... just seems wrong becuase # of convs up... # of input fc goes down
                layer_shape = layer.get_shape()  
                num_features = layer_shape[1:4].num_elements()
                self.features = num_features
            if layer > 0:         # if not first time through 
                input = output
                output = int(self.options.fc_size / (layer+1))
                           
            if layer == layers-1: # if last time through
                output = self.dataset.num_classes     
                use_reLu  = False # dont use on the last time thru
                use_Drop = False
                        
            print(" input layers: %s" % input)
            print(" output layers: %s" % output)
            self.x_image = self.new_fc_layer(input        = self.x_image,
                                           num_inputs   = input,
                                           num_outputs  = output,
                                           use_relu     = use_reLu,
                                           use_drop     = use_Drop)
            layer_name = "fullyLayer_%s" % layer
            self.fc_layers_nameslist.append(layer_name)
            self.fc_layers_list.append(self.x_image)
            print("building %s:\n%s" % (layer_name, self.x_image))
        if self.options.verbose: print("Finished Building %s Fully Connected Layers" % layers);
        return self.fc_layers_nameslist, self.fc_layers_list
    

    def new_weights(self, shape):
        x = shape
        print(x)
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

    def new_biases(self, length):
        return tf.Variable(tf.constant(0.05, shape=[length]))
       
    def new_conv_layer(self, input, filter_size, chan, num_filters, use_pooling=True):
        #print("#:\tStarting new conv Layer!...")                
        X_shape = [filter_size, filter_size, chan, num_filters]
        weights = self.new_weights(shape  = X_shape)
        #print("#: weights shape = %s" % X_shape)        
        biases = self.new_biases(length   = num_filters)
        
        """ THis is the MAGIC again... """
        layer = tf.nn.conv2d(input=input,                   # This is the output of the last layer
                             filter=weights,                # this is a thing
                             strides=[1, 1, 1, 1],          # 1111 is NOT pooled MAX work
                             padding='SAME')                # input output transformation
        layer += biases                                     # Add biases
        if use_pooling:                                     # this skips pixels... saves time but skips things obviously
            layer = tf.nn.max_pool(value = layer,           # take the weights and bias together as an input
                                   ksize = [1, 2, 2, 1],    # stuff
                                   strides = [1, 2, 2, 1],  # 2 x 2 stride... could increase... check
                                   padding='SAME')          # i feel like this should already be in variable, but w/e               
        layer = tf.nn.relu(layer)                           # rectified linear Unit ... like a boss
        #print("Finished Building a conv Layer:\n\t%s" % layer)        
        return layer, weights
           
    def flatten_layer(self, layer):
        layer_shape = layer.get_shape()                    # ASSERT layer_shape == [num_images, img_height, img_width, num_channels]
        num_features = layer_shape[1:4].num_elements()     # like a boss...
        layer_flat = tf.reshape(layer, [-1, num_features]) # yep...
        print(layer_flat)
        print("## This step is being overlooked ... but appears i think to be working... stuff...")
        return layer_flat, num_features
        
    def new_fc_layer(self, input, num_inputs, num_outputs, use_relu=True,use_drop=False):
        weights = self.new_weights(shape=[num_inputs, num_outputs])        # set weights 
        biases = self.new_biases(length=num_outputs)                       # set number of OUTPUTS like give me top k or whatever...  
        layer = tf.matmul(input, weights) + biases                         # this is a #BIGMATH func
        if use_relu:
            layer = tf.nn.relu(layer)
        if use_drop:
            layer = tf.nn.dropout(layer,self.keep_prob)
        return layer
    
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
            dataset_dictionary = { in_tensor:x_batch,
                                  in_tensor_label:y_true_batch,
                                  keep_prob:keep }                                  
        else:           
            dataset_dictionary = { in_tensor: self.test_batch[0],
                                  in_tensor_label:self.test_batch[1],
                                  keep_prob:keep }
        return dataset_dictionary
        
    def feed_dictionary(self, test=True, x_batch=None, y_true_batch=None):
        dataset = self.model
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
        
        
class Build_Mupen64_Network(object):
    def __init__(self, options = None, dataset = None, init = True):
        self.dataset = dataset
        self.options = options
        if self.options is None:
            self.options = self.model.options           
        ## HERE WE GO!!
        self.their_thing()
        if init: self.init_new_graph()
        else:
            self.init_load_graph()
        
    def weight_variable(self, shape):
        x = shape
        print(x)
        return tf.Variable(tf.truncated_normal(shape, stddev=0.05))

    #def bias_variable(shape):
    #  initial = tf.constant(0.1, shape=shape)
    #  return tf.Variable(initial)
  
    def bias_variable(self, length):
        return tf.Variable(tf.constant(0.05, shape=length))
        
    def conv2d(self, x, W, stride):
        return tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='VALID')
        
        
    def BUILD_CONV_LAYERS(self, layers):
        self.conv_layers_nameslist = []
        self.conv_layers_list = []
        self.conv_layers_wlist = []
        start_shape = self.x_image
        reducing_shape = 0
        last_num_f = 0
        if self.options.verbose: print("Building Conv Layers");
        for layer in range(layers):
            f_size = self.options.f_size
            num_f = 16 * (layer+1)
            if layer == 0:
                img = start_shape
                channel = self.dataset.num_channels
            elif layer > 0:
                img = reducing_shape
                channel = last_num_f
                print("LAST NUMBER OF FILERS = INPUT CHANNELS =  %s" % channel)
                
            last_num_f = num_f
            print("NEW NUMBER OF Channels = %s" % channel)
            reducing_shape, w = self.new_conv_layer(input       = img,
                                                    filter_size = f_size,
                                                    chan        = channel,
                                                    num_filters = num_f)
            layer_name = "convLayer_%s" % layer
            self.conv_layers_nameslist.append(layer_name)
            self.conv_layers_list.append(reducing_shape)
            self.conv_layers_wlist.append(w)
            self.LAYER = reducing_shape
            print("done with layer: %s"%layer)
            #print("#: Finished building %s:\n%s\n:##:\n" % (layer_name, self.LAYER))
            
        #if self.options.verbose: print("Finished Building %s Conv Layers" % layers);
        return self.conv_layers_nameslist, self.conv_layers_list, self.conv_layers_wlist
    
    def BUILD_FC_LAYER(self, layers):
        self.fc_layers_nameslist = []
        self.fc_layers_list = []
        print("# input features size = %s" % self.features)
        #first time thru options
        input = self.features
        output = self.options.fc_size
        use_reLu  = True
        use_Drop = True
        if self.options.verbose: print("Building Fully Connected Layers");
        for layer in range(layers):
            if layers == 0:  ## this is right ... just seems wrong becuase # of convs up... # of input fc goes down
                layer_shape = layer.get_shape()  
                num_features = layer_shape[1:4].num_elements()
                self.features = num_features
            if layer > 0:         # if not first time through 
                input = output
                output = int(self.options.fc_size / (layer+1))
                           
            if layer == layers-1: # if last time through
                output = self.dataset.num_classes     
                use_reLu  = False # dont use on the last time thru
                use_Drop = False
                        
            print(" input layers: %s" % input)
            print(" output layers: %s" % output)
            self.LAYER = self.new_fc_layer(input        = self.LAYER,
                                           num_inputs   = input,
                                           num_outputs  = output,
                                           use_relu     = use_reLu,
                                           use_drop     = use_Drop)
            layer_name = "fullyLayer_%s" % layer
            self.fc_layers_nameslist.append(layer_name)
            self.fc_layers_list.append(self.LAYER)
            print("building %s:\n%s" % (layer_name, self.LAYER))
        if self.options.verbose: print("Finished Building %s Fully Connected Layers" % layers);
        return self.fc_layers_nameslist, self.fc_layers_list
        
    def new_conv_layer(self, input, filter_size, chan, num_filters, use_pooling=True):
        #print("#:\tStarting new conv Layer!...")                
        X_shape = [filter_size, filter_size, chan, num_filters]
        weights = self.new_weights(shape  = X_shape)
        #print("#: weights shape = %s" % X_shape)        
        biases = self.new_biases(length   = num_filters)
        
        """ THis is the MAGIC again... """
        layer = tf.nn.conv2d(input=input,                   # This is the output of the last layer
                             filter=weights,                # this is a thing
                             strides=[1, 1, 1, 1],          # 1111 is NOT pooled MAX work
                             padding='SAME')                # input output transformation
        layer += biases                                     # Add biases
        if use_pooling:                                     # this skips pixels... saves time but skips things obviously
            layer = tf.nn.max_pool(value = layer,           # take the weights and bias together as an input
                                   ksize = [1, 2, 2, 1],    # stuff
                                   strides = [1, 2, 2, 1],  # 2 x 2 stride... could increase... check
                                   padding='SAME')          # i feel like this should already be in variable, but w/e               
        layer = tf.nn.relu(layer)                           # rectified linear Unit ... like a boss
        #print("Finished Building a conv Layer:\n\t%s" % layer)        
        return layer, weights
           
    def flatten_layer(self, layer):
        layer_shape = layer.get_shape()                    # ASSERT layer_shape == [num_images, img_height, img_width, num_channels]
        num_features = layer_shape[1:4].num_elements()     # like a boss...
        layer_flat = tf.reshape(layer, [-1, num_features]) # yep...
        print("## This step is being overlooked ... but appears i think to be working... stuff...")
        return layer_flat, num_features
        
    def new_fc_layer(self, input, num_inputs, num_outputs, use_relu=True,use_drop=False):
        weights = self.new_weights(shape=[num_inputs, num_outputs])        # set weights 
        biases = self.new_biases(length=num_outputs)                       # set number of OUTPUTS like give me top k or whatever...  
        layer = tf.matmul(input, weights) + biases                         # this is a #BIGMATH func
        if use_relu:
            layer = tf.nn.relu(layer)
        if use_drop:
            layer = tf.nn.dropout(layer,self.keep_prob)
        return layer
        
    def my_thing(self):
        self.convlayerNames, self.Conv_layers, self.Conv_weights   = self.BUILD_CONV_LAYERS(self.options.conv_layers) ## BUILD LAYERS
        self.x_image, self.features                                  = self.flatten_layer(self.LAYER) ## SWITCH TO FC LAYERS
        self.fclayerNames, self.fc_layers                          = self.BUILD_FC_LAYER(self.options.fc_layers) # build FC LAYERS
        
    def their_thing(self):
        self.x = tf.placeholder(tf.float32, shape=[None, self.dataset.height, self.dataset.width, 3])
        y_ = tf.placeholder(tf.float32, shape=[None, self.dataset.num_classes])
        self.Y = y_
        x_image = self.x
        
        #first convolutional layer
        W_conv1 = self.weight_variable([5, 5, 3, 24])
        b_conv1 = self.bias_variable([24])
        
        h_conv1 = tf.nn.relu(self.conv2d(x_image, W_conv1, 2) + b_conv1)
        
        #second convolutional layer
        W_conv2 = self.weight_variable([5, 5, 24, 36])
        b_conv2 = self.bias_variable([36])
        
        h_conv2 = tf.nn.relu(self.conv2d(h_conv1, W_conv2, 2) + b_conv2)
        
        #third convolutional layer
        W_conv3 = self.weight_variable([5, 5, 36, 48])
        b_conv3 = self.bias_variable([48])
        
        h_conv3 = tf.nn.relu(self.conv2d(h_conv2, W_conv3, 2) + b_conv3)
        
        #fourth convolutional layer
        W_conv4 = self.weight_variable([3, 3, 48, 64])
        b_conv4 = self.bias_variable([64])
        
        h_conv4 = tf.nn.relu(self.conv2d(h_conv3, W_conv4, 1) + b_conv4)
        
        #fifth convolutional layer
        W_conv5 = self.weight_variable([3, 3, 64, 64])
        b_conv5 = self.bias_variable([64])
        
        h_conv5 = tf.nn.relu(self.conv2d(h_conv4, W_conv5, 1) + b_conv5)
        
        #FCL 1
        W_fc1 = self.weight_variable([1152, 1164])
        b_fc1 = self.bias_variable([1164])
        
        h_conv5_flat = tf.reshape(h_conv5, [-1, 1152])
        h_fc1 = tf.nn.relu(tf.matmul(h_conv5_flat, W_fc1) + b_fc1)
        
        keep_prob = tf.placeholder(tf.float32)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
        
        #FCL 2
        W_fc2 = self.weight_variable([1164, 100])
        b_fc2 = self.bias_variable([100])
        
        h_fc2 = tf.nn.relu(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
        
        h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)
        
        #FCL 3
        W_fc3 = self.weight_variable([100, 50])
        b_fc3 = self.bias_variable([50])
        
        h_fc3 = tf.nn.relu(tf.matmul(h_fc2_drop, W_fc3) + b_fc3)
        
        h_fc3_drop = tf.nn.dropout(h_fc3, keep_prob)
        
        #FCL 4
        W_fc4 = self.weight_variable([50, 10])
        b_fc4 = self.bias_variable([10])
        
        h_fc4 = tf.nn.relu(tf.matmul(h_fc3_drop, W_fc4) + b_fc4)
        
        h_fc4_drop = tf.nn.dropout(h_fc4, keep_prob)
        self.keep_prob = keep_prob
        #Output
        W_fc5 = self.weight_variable([10, self.dataset.num_classes])
        b_fc5 = self.bias_variable([self.dataset.num_classes])
        
        y = tf.matmul(h_fc4_drop, W_fc5) + b_fc5
        self.y = y
    
    def save_graph(self, session):
        saver = tf.train.Saver()
        save_path = self.options.save_path + '_best_validation_1_'
        saver.save(sess=session, save_path=save_path)
        
    def load_graph(self, session):
        saver = tf.train.Saver()
        save_path = self.options.save_path + '_best_validation_1_'
        saver.restore(sess=session, save_path=save_path)
        
    def prepare_image(self, img):
        #print("DEBUGS  1 {}".format(img))
        pil_image = Image.open(img)# open img
        x = pil_image.resize((200, 66), Image.ANTIALIAS) # resizes image in-place
        numpy_img = np.array(x)         # convert to numpy 
        #grey_numpy_image = self.make_BW(numpy_img)
        return numpy_img
        
    def que_graph(self, Image):
        try: vec = self.prepare_image(Image)
        except: vec = Image
        joystick = self.y.eval(feed_dict={self.x: [vec], self.keep_prob: 1.0})[0]
        output = [
                int(joystick[0] * 80),
                int(joystick[1] * 80),
                int(round(joystick[2])),
                int(round(joystick[3])),
                int(round(joystick[4])),
            ]
            
        for i in joystick:
            print("joystick: {}".format(i))
        print(output)
        return output
        
    def init_load_graph(self):
        self.session = tf.InteractiveSession()
        self.load_graph(self.session)
        
    def init_new_graph(self):
        sess = tf.InteractiveSession()
        train_vars = tf.trainable_variables()
        
        loss = tf.reduce_mean(tf.square(tf.sub(self.Y, self.y))) +\
        			tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) *\
        			self.options.L2NormConst
        
        
        train_step = tf.train.AdamOptimizer(1e-5).minimize(loss)
        
        sess.run(tf.global_variables_initializer())
        
        # Training loop variables
        epochs = self.options.epochs
        batch_size = self.options.batch_size
        num_samples = self.dataset._num_examples
        step_size = int(self.dataset._num_examples / self.options.batch_size) # this was hardcoded in other examples
        
        for epoch in range(epochs):
            for i in range(step_size):
                batch = self.dataset.next_batch(batch_size)
                if len(batch[0]) is len(batch[1]):
                    train_step.run(feed_dict={self.x: batch[0], self.Y: batch[1], self.keep_prob: 0.8}) #! Hardcoded value
            
                    if i%25 == 0:
                      loss_value = loss.eval(feed_dict={self.x:batch[0], self.Y: batch[1], self.keep_prob: 1.0})  #! hardcoded value
                      print("epoch: {} step: {} loss: {}".format(epoch, epoch * batch_size + i, loss_value))
                      
        self.save_graph(sess)
        sess.close()
        