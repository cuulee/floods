import tensorflow as tf

slim = tf.contrib.slim


def schema35(net, scale= 1.0, scope=None, reuse=None, activationFunc=tf.nn.relu):
    with tf.variable_scope(scope, 'Schema35', [net], reuse=reuse):
        with tf.variable_scope('Branch_1'):
            branch1 = slim.conv2d(net,32,1, scope='Conv2d_B1a_1x1')
        with tf.variable_scope('Branch_2'):
            branch2 = slim.conv2d(net,32,1, scope='Conv2d_B1a_1x1')
            branch2 = slim.conv2d(branch2, 32, [3,3], scope='Conv2d_B1b_3x3')
        with tf.variable_scope('Branch_3'):
            branch3 = slim.conv2d(net, 32, 1, scope='Conv2d_B1a_1x1')
            branch3 = slim.conv2d(branch3, 48, 3, scope='Conv2d_B1b_3x3')
            branch3 = slim.conv2d(branch3, 63, 3, scope='Conv2d_B1c_3x3')
        concat = tf.concat(axis=3, values=[branch1, branch2, branch3])
        linear = slim.conv2d(concat, net.get_shape()[3],1, normalizer_fn=None,
                            activation_fn=None, scope='Conv2d_1x1')
        net += scale * linear
        if activationFunc:
            net = activationFunc(net)
        return net

def schema17(net, scale=1.0, scope = None, reuse=None, activationFunc=tf.nn.relu):
    with tf.variable_scope(scope, 'Schema17', [net], reuse=reuse):
        with tf.variable_scope('Branch_1'):
            branch1 = slim.conv2d(net, 192, 1, scope='Conv2d_B1a_1x1')
        with tf.variable_scope('Branch_2'):
            branch2 = slim.conv2d(net, 128,1, scope='Conv2d_B1a_1x1')
            branch2 = slim.conv2d(branch2, 160,[1,7], scope='Conv2d_B1b_1x7')
            branch2 = slim.conv2d(branch2, 192,[7,1], scope='Conv2d_B1c_7x1')
        concat = tf.concat(axis=3, values=[branch1,branch2])
        linear = slim.conv2d(concat, net.get_shape()[3],1, normalizer_fn=None,
                            activation_fn=None, scope='Conv2d_1x1')
        net += scale* linear
        if activationFunc:
            net = activationFunc(net)
        return net

def schema8(net, scale=1.0, scope=None, reuse=None, activationFunc=tf.nn.relu):
    with tf.variable_scope(scope, 'Schema8', [net], reuse=reuse):
        with tf.variable_scope('Branch_1'):
            branch1 = slim.conv2d(net, 192, 1, scope = 'Conv2d_B1a_1x1')
        with tf.variable_scope('Branch_2'):
            branch2 = slim.conv2d(net, 192, 1, scope = 'Conv2d_B1a_1x1' )
            branch2 = slim.conv2d(branch2, 224, [1,3], scope = 'Conv2d_B1b_1x3' )
            branch2 = slim.conv2d(branch2, 256, [3,1], scope = 'Conv2d_B1c_1x3' )
        concat = tf.concat(axis=3, values=[branch1,branch2])
        linear = slim.conv2d(concat, net.get_shape()[3],1,normalizer_fn=None,
                            activation_fn=None, scope='Conv2d_1x1')
        net += scale * linear
        if activationFunc:
            net = activationFunc(net)
        return net

def inceptResV2(inputs, numClasses = 2, reuse=None, scope='IncepResV2',
                dropKeepProb = 0.8, isTraining = True, createAuxLogit=True):
    endPoints = {}


    with tf.variable_scope(scope, 'Inception', [inputs], reuse=reuse):
        with slim.arg_scope([slim.batch_norm, slim.dropout],
                        is_training=isTraining):
            with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                              stride=1, padding='SAME'):


                ############# STEM BEGIN ##################

                 # 299 x 299 x 3
                net = slim.conv2d(inputs, 32, [3,3], stride=2, padding='VALID',
                                 scope= 'Conv2d_1a_3x3')
                endPoints['Conv2d_1a_3x3'] = net

                # 149 x 149 x 32
                net = slim.conv2d(net,32, 3, padding='VALID',
                                 scope='Conv2d_2a_3x3')
                endPoints['Conv2d_2a_3x3'] = net

                net = slim.conv2d(net,64, [3,3], scope= 'Conv2d_2b_3x3')
                endPoints['Conv2d_2b_3x3'] = net

                # 147 x 147 x 64
                with tf.variable_scope('Concat_3a'):
                    with tf.variable_scope('Branch_1'):
                        branch1 = slim.max_pool2d(net, 3, stride=2, padding='VALID',
                                                  scope='MaxPool_B1a_3x3')

                    with tf.variable_scope('Branch_2'):
                        branch2 = slim.conv2d(net, 96, 3, stride=2, padding='VALID',
                                             scope='Conv2d_B1a_3x3')
                    net = tf.concat(axis=3, values=[branch1, branch2])
                    endPoints['Concat_3a'] = net

                # 73 x 73 x 160
                with tf.variable_scope('Concat_4a'):
                    with tf.variable_scope('Branch_1'):
                        branch1 = slim.conv2d(net, 64, [1,1], scope='Conv2d_B1a_1x1')
                        branch1 = slim.conv2d(branch1, 96, [3,3], padding='VALID',
                                             scope='Conv2d_B2a_3x3')
                    with tf.variable_scope('Branch_2'):
                        branch2 = slim.conv2d(net, 64, [1,1], scope='Conv2d_B1a_1x1')
                        branch2 = slim.conv2d(branch2, 64, [7,1], scope='Conv2d_B1b_7x1')
                        branch2 = slim.conv2d(branch2, 64, [7,1], scope='Conv2d_B1c_1x7')
                        branch2 = slim.conv2d(branch2, 96, [3,3], padding = 'VALID',
                                              scope='Conv2d_B2a_1x7')
                    net = tf.concat(axis=3, values=[branch1, branch2])
                    endPoints['Concat_4a'] = net


                # 71 x 71 x 192
                with tf.variable_scope('Concat_5a'):
                    with tf.variable_scope('Branch_1'):
                        branch1 = slim.conv2d(net, 192, [3,3], stride=2, padding= 'VALID',
                                             scope='Conv2d_B1a_3x3')
                    with tf.variable_scope('Branch_2'):
                        branch2 = slim.max_pool2d(net, [3,3], stride=2, padding ='VALID',
                                                scope='MaxPool_B1a_3x3' )
                    net = tf.concat(axis=3, values=[branch1, branch2])
                    endPoints['Concat_5a'] = net

                #35 x 35 x 384
                ############# STEM END ##################

                ############# INCEPTION-RESNET-A BEGIN ##################
                net = slim.repeat(net, 5, schema35, scale=0.17)
                ############# INCEPTION-RESNET-A END ##################

                ############# REDUCTION-A BEGIN ##################
                ############# 35 x 35 to 17 x 17 #################
                with tf.variable_scope('Concat_6a'):
                    with tf.variable_scope('Branch_1'):
                        branch1 = slim.max_pool2d(net, 3, stride =2, padding='VALID',
                                                 scope='MaxPool_B1a_3x3')
                    with tf.variable_scope('Branch_2'):
                        branch2 = slim.conv2d(net, 384, 3, stride= 2, padding='VALID',
                                            scope='Conv2d_B1a_3x3')
                    with tf.variable_scope('Branch_3'):
                        branch3 = slim.conv2d(net, 256,1, scope='Conv2d_B1a_1x1')
                        branch3 = slim.conv2d(branch3,256, 3, scope='Conv2d_B1b_3x3')
                        branch3 = slim.conv2d(branch3, 384, 3, stride =2, padding='VALID',
                                             scope='Conv2d_B2a_3x3')
                    net = tf.concat(axis=3, values=[branch1,branch2,branch3])
                    endPoints['Concat_6a'] = net
                ############# REDUCTION-A END ##################

                ############# INCEPTION-RESNET-B BEGIN ##################
                net = slim.repeat(net, 10, schema17, scale=0.10)
                ############# INCEPTION-RESNET-B END ##################

                ############# AUX ##################
                with tf.variable_scope('AuxLogits'):
                    aux = slim.avg_pool2d(net,5,stride=3, padding='VALID',scope='Conv2d_1a_3x3')
                    aux = slim.conv2d(aux, 128, 1, scope='Conv2d_1b_1x1')
                    aux = slim.conv2d(aux,768, aux.get_shape()[1:3],padding='VALID',scope='Conv2d_2a_5x5')
                    aux = slim.flatten(aux)
                    aux = slim.fully_connected(aux,numClasses,activation_fn=None,scope='Logits')
                    endPoints['AuxLogits'] = aux


                ############# REDUCTION-B BEGIN ##################
                ############# 17 x 17 to 8 x 8 #################
                with tf.variable_scope('Concat_7a'):
                    with tf.variable_scope('Branch_1'):
                        branch1 = slim.max_pool2d(net, 3, stride=2, padding='VALID',
                                                scope = 'MaxPool2d_B1a_3x3')
                    with tf.variable_scope('Branch_2'):
                        branch2 = slim.conv2d(net, 256, 1, scope= 'Conv2d_B1a_1x1')
                        branch2 = slim.conv2d(branch2, 384, 3, stride = 2, padding='VALID',
                                             scope = 'Conv2d_B2a_3x3')
                    with tf.variable_scope('Branch_3'):
                        branch3 = slim.conv2d(net, 256, 1, scope= 'Conv2d_B1a_1x1')
                        branch3 = slim.conv2d(branch3, 288, 3, stride = 2, padding='VALID',
                                             scope = 'Conv2d_B2a_3x3')
                    with tf.variable_scope('Branch_4'):
                        branch4 = slim.conv2d(net, 256, 1, scope= 'Conv2d_B1a_1x1')
                        branch4 = slim.conv2d(branch4, 288, 3, scope = 'Conv2d_B1b_3x3')
                        branch4 = slim.conv2d(branch4, 320, 3, stride= 2, padding= 'VALID',
                                              scope = 'Conv2d_B2a_3x3')
                    net = tf.concat(axis=3, values=[branch1,branch2,branch3, branch4])
                    endPoints['Concat_7a'] = net
                ############# REDUCTION-B END ##################

                ############# INCEPTION-RESNET-B BEGIN ##################
                net = slim.repeat(net, 5, schema17, scale=0.20)
                ############# INCEPTION-RESNET-B END ##################

                ############# LOGIT BEGIN ##################
                with tf.variable_scope('Logits'):
                    net = slim.avg_pool2d(net, net.get_shape()[1:3], padding = 'VALID',
                                          scope = 'AvgPool_L1a')
                    net = slim.dropout(net, dropKeepProb, is_training=isTraining, scope = 'Dropout_L1b')
                    net = slim.flatten(net)

                    endPoints['PreLogits'] = net
                    logits = slim.fully_connected(net, numClasses, activation_fn=None,
                                                  scope='Logits')
                    endPoints['Logits'] = logits

                    endPoints['Predictions'] = tf.nn.softmax(logits, name = 'Predictions')
                ############# LOGIT END ##################

                return logits , endPoints


def inceptResV2ArgScope(weightDecay=0.00004, batchNorm =True, batchNormDecay =0.9997, batchNormEpsil = 0.001 ):
    with slim.arg_scope([slim.conv2d,slim.fully_connected],
                        weights_regularizer=slim.l2_regularizer(weightDecay),
                        biases_regularizer=slim.l2_regularizer(weightDecay)):


        batchNormPara = {'decay':batchNormDecay,
                         'epsilon': batchNormEpsil,
                        }


    #Sets weightDecy for conv & fully con layer


        with slim.arg_scope([slim.conv2d],
                            activation_fn=tf.nn.relu,
                            normalizer_fn=slim.batch_norm,
                            normalizer_params=batchNormPara) as scope:
            return scope


inceptResV2.defaultImageSize = 299
