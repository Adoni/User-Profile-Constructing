import cPickle
import numpy
import theano
from theano import tensor as T
from matplotlib import pyplot as plt

def load_data(dataset):
    print '... loading data'
    f=open(dataset,'rb')
    train_set, valid_set, test_set = cPickle.load(f)
    f.close()

    def shared_dataset(data_xy, borrow=True):
        data_x,data_y=data_xy
        data_x=data_x[:,:400]
        return data_x,data_y

    test_set_x, test_set_y = shared_dataset(test_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    train_set_x, train_set_y = shared_dataset(train_set)

    rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    return rval


def get_classifier(params_file):
    params=cPickle.load(open(params_file,'rb'))
    x=T.dmatrix()
    W1=params[0]
    b1=params[1]
    W2=params[2]
    b2=params[3]
    hidden=T.tanh(T.dot(x,W1)+b1)
    p_y_given_x = T.nnet.softmax(T.dot(hidden,W2) + b2)
    y_pred = T.argmax(p_y_given_x, axis=1)
    classifier=theano.function([x],y_pred)
    return classifier

def test():
    datasets = load_data('./gender_matrix_with_time.data')
    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    test_set_x, test_set_y = datasets[2]
    classifier=get_classifier('./params.bin')
    y=test_set_y
    yy=classifier(test_set_x)
    true=0
    false=0
    result=[]
    for i in range(0,len(y)):
        result.append((int(y[i]),yy[i]))
        print y[i],yy[i]
        if int(y[i])==yy[i]:
            true+=1
        else:
            false+=1
    print 'Accuracy: '+str(100.0*true/(true+false))+"%"
    cPickle.dump(result, open('result.data','wb'))

if __name__=='__main__':
    test()
