from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle

def load_data(dataset):
    print '...loading data from '+dataset
    train_set, valid_set, test_set=pickle.load(open(dataset))
    train_set_x,train_set_y=train_set
    test_set_x,test_set_y=test_set
    data=[(train_set_x,train_set_y),(test_set_x,test_set_y)]
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
    data=load_data('/mnt/data1/adoni/gender_matrix.data')
    clfs={}
    clfs['SVC']=SVC()
    clfs['LogisticRegression']=LogisticRegression()
    clfs.append(RandomForestClassifier(n_estimators=10))
    clfs.append(GaussianNB())
    clfs.append(LinearSVC())
    clfs.append(DecisionTreeClassifier())
    clfs.append(KNeighborsClassifier())
    for clf in clfs:
        clf=get_classifier(data[0], clf)
        #clf=pickle.load(open('./clf','rb'))
        pickle.dump(clf,open('./clf','wb'))
        result=test(clf,data[1])
        print clf
        print result
        print '=========='

if __name__=='__main__':
    main()
