import tensorflow as tf
import time
from datetime import timedelta
#from sklearn.metrics import confusion_matrix
from tqdm import tqdm as tqdm
#from tqdm import tqdm_notebook as tqdm
#import numpy as np

class Process_Network(object):
    def __init__(self, network=None, ipy=None):
        self.werk_done = 0
        self.ipy = ipy   
        self.network = network
        if network is not None:
            self.options = network.options
            self.model = network.model
            self.verbose = self.options.verbose
            if ipy is not None:
                self.ipy = ipy(model=self.model)
            if self.verbose:
                from pprint import pprint
                pprint (vars(self.model))
        self.progress = tqdm
        
    ## SHOULD RETURN A LIST OF AVAILABLE MODELS SAVED IN THE TANK!
    
    def BE_DONE(self):
        self.network.session.close() 
        
    #The Real work of the thing... you could run this and be done.
    def optimize(self, acc=False):
        x_batch, y_true_batch = self.model.trainer.next_batch(self.options.batch_size);
        #x_batch, y_true_batch = self.model.get_batch();
        if len(x_batch) is len(y_true_batch):
            self.feed_train = self.network.prob_dictionary(test=False, x_batch=x_batch, y_true_batch=y_true_batch);
            if not acc: self.network.session.run(self.network.optimizer, feed_dict=self.feed_train)
            else: self.network.get_lost(x_batch,y_true_batch)
    
    
    # Silent October
    def long_haul(self, iters=1):
        for i in self.progress(range(iters)):
            self.werk_done += 1 # tick the clock
            self.network.optimize() #do the work
            if i % 25 == 0:
                self.optimize(acc=True)
        return self.werk_done
     
    #Gives back the ACC with a .1 trailing dec... good stuff
    def print_acc(self):
        #acc = self.network.session.run(self.network.accuracy, feed_dict=self.network.feed_test)
        acc = self.network.get_lost()
        if self.options.verbose: print("\rLoss on test-set: {0:.5%}".format(acc));
        return acc
        
        
        
        
        
        
    #returning log for IPY.simple_plot this doesnt work
    def get_logits(self):
        x = self.network.session.run(tf.matmul(self.network.Input_Tensor_Images, self.network.weights) + self.network.biases)
        return x    
    
    # RETURNING w for IPY.plot_weights 
    def get_weights(self):
        x = self.network.session.run(self.network.weights)
        return x
        
    # RETURNING ConfusionMatrix and NumClasses for IPY.plot_confused 
    def get_confused(self): pass
    """
    def get_confused(self):
        #get num_classes
        num_classes = self.model.num_classes
        # Get the true classifications for the test-set.
        cls_true = self.model.test_cls
        # Get the predicted classifications for the test-set.
        cls_pred = self.network.session.run(self.network.y_pred_cls, feed_dict=self.network.feed_test)
        cm = confusion_matrix(y_true=cls_true, y_pred=cls_pred)
        if self.options.verbose: print(cm);
        return cm, num_classes
    """
    # RETURNING IMAGES, CLS_TRUE, CLS_PRED for IPY.SIMPLE_PLOT
    def get_example_errors(self):
        self.print_acc()
        correct, cls_pred = self.network.session.run([self.network.correct_prediction, self.network.y_pred_cls],
                                                     feed_dict=self.network.feed_test)
        incorrect = (correct == False)
        images = self.model.images_test[incorrect]
        cls_pred = cls_pred[incorrect]
        cls_true = self.model.cls_true[incorrect]
        n = min(9, len(images))       
        return images[0:n], cls_true[0:n], cls_pred[0:n]
    
    # This is A Verbose Output of All Available Sources
    def show_Verbose(self):
       ## GET SOME DATAS
       cm, num_classes = self.get_confused()
       img, cls_t,cls_p = self.get_example_errors()
       ## Bring in IPY
       self.ipy.plot_confused(cm,num_classes)
       self.ipy.simple_plot(images=img, cls_true=cls_t, cls_pred=cls_p)
    
    def print_samples(self):
        x = self.model.train_images[0:9]
        y = self.model.train_labels[0:9]
        index = 0
        for i in x:
            print("img {} label = {}".format(i,y[index]))
            index += 1
       
    def train_step(self, Dict): pass
        
            
    # For LEARNING(EDUCATIONAL) pourpose, use Long Haul for faster work.
    def process_verbose(self, iters=1):
        start_time = time.time() 
        for i in range(iters):     # THIS IS THE "OPTIMIZER" FUNCTION     
            self.werk_done += 1    # tick the clock
            x_batch, y_true_batch = self.model.trainer.next_batch(self.options.batch_size);
            self.feed_train = self.network.feed_dictionary(test=False, x_batch=x_batch, y_true_batch=y_true_batch);
            self.network.session.run(self.network.optimizer, feed_dict=self.feed_train)
            if i % 10 == 0:       # if lap hits 100 do a test and dog out if you start sucking!
                acc = self.network.session.run(self.network.accuracy, feed_dict=self.feed_train)                   ## TRAINING ACCURACY   
                acc_test = self.network.session.run(self.network.accuracy, feed_dict=self.network.feed_test)       ## TESTING ACCURACY   
                msg = "Optimization Iteration: {0:>6}, Training Accuracy: {1:>6.1%}, Testing Accuracy: {2:>6.1%}"  ## be clean about it 
                print(msg.format(self.werk_done, acc,acc_test))
        self.show_Verbose()                # Verboseity of this Process
        end_time = time.time()             # AND STOP THE CLOCK...
        time_dif = end_time - start_time   # do the math
        time_msg = "Time usage: " + str(timedelta(seconds=int(round(time_dif))))   # boom and done.
        print(time_msg, ", Iters Complete: %s" % self.werk_done)
        
        