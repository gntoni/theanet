#!/usr/bin/env python

"""

This code implements som useful functions.

    - load_data

"""

import os
import sys
import cPickle
import numpy as np
import theano
import theano.tensor as T

from os.path import isfile,isdir,join


def load_data(dataset, make_shared = True):
    ''' Loads the dataset

    :type dataset: string
    :param dataset: the path to the dataset file (if pickle file) or folder (containing numpy files)
    '''

    if isfile(dataset):
        data_dir, data_file = os.path.split(dataset)
        if data_dir == "" and not os.path.isfile(dataset):
            sys.exit("Dataset file not found")
    
        else:
            print '... loading data'
            f = open(dataset, 'rb')
            train_set, valid_set, test_set = cPickle.load(f)
            f.close()
    elif isdir(dataset):
        train_set = (np.load(join(dataset,'train_set_x.npy')).astype('float32'),
                     np.load(join(dataset,'train_set_y.npy')).astype('int32')
        )
        valid_set = (np.load(join(dataset,'valid_set_x.npy')).astype('float32'),
                     np.load(join(dataset,'valid_set_y.npy')).astype('int32')
        )
        test_set  = (np.load(join(dataset,'test_set_x.npy')).astype('float32'),
                     np.load(join(dataset,'test_set_y.npy')).astype('int32')
        )                        
    else:
        sys.exit('Dataset path not recognized')
    #train_set, valid_set, test_set format: tuple(input, target)
    #input is an numpy.ndarray of 3 dimensions (default: (nExamples,4,3600))
    #first dimension corresponds to each of the four images RGBD
    #for each image there is a 2D array (a matrix)
    #witch row's correspond to an example. target is a
    #numpy.ndarray of 1 dimensions (vector)) that have the same length as
    #the number of rows in the input. It should give the target
    #target to the example with the same index in the input.

    def shared_dataset(data_xy, borrow=True):
        """ Function that loads the dataset into shared variables

        The reason we store our dataset in shared variables is to allow
        Theano to copy it into the GPU memory (when code is run on GPU).
        Since copying data into the GPU is slow, copying a minibatch everytime
        is needed (the default behaviour if the data is not in a shared
        variable) would lead to a large decrease in performance.
        """
        data_x, data_y = data_xy
        shared_x = theano.shared(np.asarray(data_x,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        shared_y = theano.shared(np.asarray(data_y,
                                               dtype=theano.config.floatX),
                                 borrow=borrow)
        # When storing data on the GPU it has to be stored as floats
        # therefore we will store the labels as ``floatX`` as well
        # (``shared_y`` does exactly that). But during our computations
        # we need them as ints (we use labels as index, and if they are
        # floats it doesn't make sense) therefore instead of returning
        # ``shared_y`` we will have to cast it to int. This little hack
        # lets ous get around this issue
        return shared_x, T.cast(shared_y, 'int32')

    if make_shared:
        test_set_x, test_set_y = shared_dataset(test_set)
        valid_set_x, valid_set_y = shared_dataset(valid_set)
        train_set_x, train_set_y = shared_dataset(train_set)
    else:
        test_set_x, test_set_y = test_set
        valid_set_x, valid_set_y = valid_set
        train_set_x, train_set_y = train_set

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval
