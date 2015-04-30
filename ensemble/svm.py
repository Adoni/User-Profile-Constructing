from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle
import numpy

def load_data(dataset):
    print '...loading data from '+dataset
    a=pickle.load(open(dataset,'rb'))
    print len(a)
    train_set, valid_set, test_set=pickle.load(open(dataset,'rb'))
    train_set_x,train_set_y=train_set
    valid_set_x,valid_set_y=valid_set
    test_set_x,test_set_y=test_set
    data=[(train_set_x,train_set_y),(valid_set_x,valid_set_y),(test_set_x,test_set_y)]
    return data

def get_classifier(train_set, clf):
    print '...getting classifier'
    clf.fit(train_set[0],train_set[1])
    return clf

def test(clf,test_set):
    print '...testing classifier'
    predict_y=clf.predict(test_set[0])
    true=0
    false=0
    for i in range(0,len(predict_y)):
        if predict_y[i]==test_set[1][i]:
            true+=1
        else:
            false+=1
    return true*1.0/(true+false)

def main():
    data=load_data('/mnt/data1/adoni/gender_name.data')
    #data=pickle.load(open('./ensemble_x','rb'))
    clfs={}
    clfs['SVC']=SVC(probability=True)
    clfs['LogisticRegression']=LogisticRegression()
    clfs['RandomForestClassifier']=RandomForestClassifier(n_estimators=10)
    clfs['GaussianNB']=GaussianNB()
    clfs['LinearSVC']=LinearSVC()
    clfs['DecisionTreeClassifier']=DecisionTreeClassifier()
    #clfs['KNeighborsClassifier']=KNeighborsClassifier()
    for clf_name in clfs:
        clf=get_classifier(data[0], clfs[clf_name])
        #clf=pickle.load(open('./clf','rb'))
        pickle.dump(clf,open('./models/name_'+clf_name+'.model','wb'))
        result0=test(clf,data[0])
        result1=test(clf,data[1])
        print clf_name
        print result1
        print '=========='

def ensemble():
    data=load_data('/mnt/data1/adoni/gender_matrix_name_bag_of_word.data')
    clfs=[]
    clfs.append(pickle.load(open('./DecisionTreeClassifier','rb')))
    clfs.append(pickle.load(open('./GaussianNB','rb')))
    #clfs.append(pickle.load(open('./KNeighborsClassifier','rb')))
    clfs.append(pickle.load(open('./LinearSVC','rb')))
    clfs.append(pickle.load(open('./LogisticRegression','rb')))
    clfs.append(pickle.load(open('./RandomForestClassifier','rb')))
    #clfs.append(pickle.load(open('./SVC','rb')))
    print '...load clfs done'
    train_x=[]
    train_y=data[1][1]
    test_x=[]
    test_y=data[2][1]
    for clf in clfs:
        print clf
        predict_y=clf.predict(data[1][0])
        train_x.append(predict_y)
        predict_y=clf.predict(data[2][0])
        test_x.append(predict_y)
    train_x=numpy.array(train_x)
    train_x=numpy.transpose(train_x)
    test_x=numpy.array(test_x)
    test_x=numpy.transpose(test_x)
    pickle.dump(((train_x,train_y),(test_x,test_y)),open('ensemble','w'))

if __name__=='__main__':
    main()
    #ensemble()
