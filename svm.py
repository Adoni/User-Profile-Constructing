from sklearn import svm
import cPickle

def load_data(dataset):
    print '...loading data from '+dataset
    train_set, valid_set, test_set=cPickle.load(open(dataset))
    train_set_x,train_set_y=train_set
    test_set_x,test_set_y=test_set
    data=[(train_set_x,train_set_y),(test_set_x,test_set_y)]
    return data

def get_classifier(train_set):
    clf = svm.SVR()
    clf.fit(train_set[0],train_set[1])
    return clf

def test(clf,test_set):
    predict_y=clf.predict(test_set[0])
    true=0
    false=0
    for i in range(0,len(predict_y)):
        if predict_y[i]==test_set[1][i]:
            true+=1
        else:
            false+=1
    return true,false

def main():
    data_set=load_data('./gender_matrix_for_nn.data')
    clf=get_classifier(data[0])
    result=test(clf,data[2])
    print result

if __name__=='__main__':
    main()
