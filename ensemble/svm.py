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
    print '...getting classifier'
    clf = svm.SVC()
    clf.fit(train_set[0],train_set[1])
    return clf

def test(clf,test_set):
    print '...testing classifier'
    predict_y=clf.predict(test_set[0])
    print test_set[0]
    print predict_y
    true=0
    false=0
    for i in range(0,len(predict_y)):
        if predict_y[i]==test_set[1][i]:
            true+=1
        else:
            false+=1
    return true,false

def main():
    data=load_data('./gender_matrix.data')
    clf=get_classifier(data[0])
    #clf=cPickle.load(open('./clf','rb'))
    cPickle.dump(clf,open('./clf','wb'))
    result=test(clf,data[1])
    print result

if __name__=='__main__':
    main()
