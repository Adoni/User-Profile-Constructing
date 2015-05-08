#coding:utf8
import urllib2
import numpy
import json
import pickle

access_token = '2.00L9khmFlxpd6C91aec9ef010s3KCc'
word_vector_size=500
time_vector_size=24

correct_sources=[' '.join(l.decode('utf8').split(' ')[:-1]) for l in open('./source.txt')]
def is_not_good_status(status):
    source=status['source']
    if source==None:
        return True
    if u'O网页链接' in ''.join(status['text']):
        return True
    if source in correct_sources:
        return False
    if source.endswith(u'手机'):
        return False
    return True

def get_vectors(file_name):
    print 'Getting vectors...'
    f=open(file_name)
    vectors=dict()
    for line in f:
        line=line
        line=line.split(' ')
        try:
            line.remove('\n')
        except Exception as e:
            pass
        key=line[0]
        vector=[0]*(len(line)-1)
        for i in range(1,len(line)):
            vector[i-1]=float(line[i])
        vectors[key]=numpy.array(vector)
    print 'Done'
    return vectors

def dump_vectors():
    word_vectors=get_vectors('./word_vectors.data')
    print 'dump'
    pickle.dump(word_vectors,open('parameters.bin','wb'))
    print 'dump done'

def get_progressive_bar(total_count):
    from progressive.bar import Bar
    bar=Bar(max_value=total_count,fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    return bar

def parse_user(line):
    #print type(line)
    #line=line.decode('utf8')
    line=line[:-1].split('\t')
    user=dict()
    user['gender']=line[0]
    user['screen_name']=line[1]
    user['statuses']=[]
    for i in range(2,len(line)):
        status=line[i].split(' FROM: ')
        status={'text':status[0].split(' '), 'source':status[1]}
        user['statuses'].append(status)
    return user

def get_text_vector_for_cnn(text,word_count):
    if len(text)<words_count:
        return None
    text=text[0:words_count]
    text_vector=numpy.array(text)#numpy.max(text_vector,axis=0)
    text_vector=text_vector.reshape((text_vector.shape[0]*text_vector.shape[1]))
    return text_vector
def get_text_vector_for_nn(text, window_size=1):
    text2=[]
    for i in range(0,len(text)-window_size+1):
        text2.append(text[i]+text[i+1])
    text_vector=numpy.array(text2)
    text_vector=numpy.max(text_vector,axis=0)
    return text_vector

def output_age_matrix_from_bag_of_words():
    from pymongo import Connection
    words={}
    f=open('./word.feature').readlines()
    for i in range(0,len(f)):
        words[f[i].decode('utf8')[0:-1]]=i
    all_data_x=[]
    all_data_y=[]
    index=0
    #进度条相关参数
    users=Connection().user_image.users
    total_count=users.count()
    bar=get_progressive_bar(total_count)
    finish_count=0
    #for line in open('./users.data'):
    for user in users.find():
        #user=parse_user(line)
        correct_status=0
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            else:
                correct_status+=1
        if correct_status<50:
            continue
        length=[]
        text=numpy.zeros((len(words)))
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            for word in status['text']:
                if word not in words:
                    continue
                text[words[word]]+=1.0
        if not text.any():
            continue
        text_vector=text
        if user['information']['gender']=='m':
            all_data_y.append(1)
        else:
            all_data_y.append(0)
        all_data_x.append(text_vector)
        index+=1
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
    all_data_x=numpy.array(all_data_x)
    b=numpy.max(all_data_x,axis=0)
    c=numpy.min(all_data_x,axis=0)
    pickle.dump((b,c),open('./normal','wb'))
    for i in range(0,all_data_x.shape[1]):
        if b[i]==c[i]:
            all_data_x[:,i]=numpy.zeros(all_data_x.shape[0])
            continue
        all_data_x[:,i]=(all_data_x[:,i]-c[i])/(b[i]-c[i])
    all_data_y=numpy.array(all_data_y)
    all_data_y=numpy.array(all_data_y)
    train_set_x=all_data_x[0:index*3/4]
    train_set_y=all_data_y[0:index*3/4]
    train_set=(train_set_x,train_set_y)
    valid_set_x=all_data_x[index*3/4:index*7/8]
    valid_set_y=all_data_y[index*3/4:index*7/8]
    valid_set=(valid_set_x,valid_set_y)
    test_set_x=all_data_x[index*7/8:]
    test_set_y=all_data_y[index*7/8:]
    test_set=(test_set_x,test_set_y)
    pickle.dump((train_set,valid_set,test_set),open('/mnt/data1/adoni/gender_matrix_bag_of_words.data','wb'))

def output_age_matrix():
    from pymongo import Connection
    users=Connection().user_profilling.users
    word_vectors=get_vectors('/mnt/data1/adoni/word_vectors.bin')
    word_count=600
    all_data_x=[]
    all_data_y=[]
    index=0
    #进度条相关参数
    total_count=20000
    bar=get_progressive_bar(total_count)
    finish_count=0
    for user in users.find():
        correct_status=0
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            else:
                correct_status+=1
        if correct_status<50:
            continue
        length=[]
        text=[]
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            for word in status['text']:
                try:
                    text.append(word_vectors[word])
                except Exception as e:
                    continue
        text_vector=get_text_vector_for_nn(text,window_size=2)
        if text_vector is None:
            continue
        if user['information']['gender']=='m':
            all_data_y.append(1)
        else:
            all_data_y.append(0)
        all_data_x.append(text_vector)
        index+=1
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
    all_data_x=numpy.array(all_data_x)
    b=numpy.max(all_data_x,axis=0)
    c=numpy.min(all_data_x,axis=0)
    pickle.dump((b,c),open('./normal','wb'))
    for i in all_data_x.shape[1]:
        all_data_x[:,i]=(all_data_x[:,i]-c[i])/(b[i]-c[i])
    all_data_y=numpy.array(all_data_y)
    train_set_x=all_data_x[0:index*3/4]
    train_set_y=all_data_y[0:index*3/4]
    train_set=(train_set_x,train_set_y)
    valid_set_x=all_data_x[index*3/4:index*7/8]
    valid_set_y=all_data_y[index*3/4:index*7/8]
    valid_set=(valid_set_x,valid_set_y)
    test_set_x=all_data_x[index*7/8:]
    test_set_y=all_data_y[index*7/8:]
    test_set=(test_set_x,test_set_y)
    pickle.dump((train_set,valid_set,test_set),open('/mnt/data1/adoni/gender_matrix_word_vector.data','wb'))

def get_str_description(description):
    d=[]
    for dd in description:
        #d=d+dd
        d.append(''.join(dd))
    d=' '.join(d)
    return d

def dump_train_valid_test(x,y,file_name):
    print 'dump'
    if not len(x)==len(y):
        raise Exception('The size of x is not equel with that of y')
    all_data_x=[]
    all_data_y=[]
    for i in range(0,len(x)):
        if numpy.any(x[i]):
            all_data_x.append(x[i])
            all_data_y.append(y[i])
    if not len(all_data_x)==len(all_data_y):
        raise Exception('The size of x is not equel with that of y')
    all_data_x=numpy.array(all_data_x)
    all_data_y=numpy.array(all_data_y)
    b=numpy.max(all_data_x,axis=0)
    c=numpy.min(all_data_x,axis=0)
    pickle.dump((b,c),open('./normal','wb'))
    for i in range(0,all_data_x.shape[1]):
        if b[i]==c[i]:
            all_data_x[i]=0
        else:
            all_data_x[:,i]=(all_data_x[:,i]-c[i])/(b[i]-c[i])
    index=len(all_data_y)
    print index
    train_set_x=all_data_x[0:index*3/4]
    train_set_y=all_data_y[0:index*3/4]
    train_set=(train_set_x,train_set_y)
    valid_set_x=all_data_x[index*3/4:index*7/8]
    valid_set_y=all_data_y[index*3/4:index*7/8]
    valid_set=(valid_set_x,valid_set_y)
    test_set_x=all_data_x[index*7/8:]
    test_set_y=all_data_y[index*7/8:]
    test_set=(test_set_x,test_set_y)
    pickle.dump((train_set,valid_set,test_set),open('/mnt/data1/adoni/'+file_name,'wb'))

def output_description_matrix():
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(min_df=1)
    from pymongo import Connection
    users=Connection().user_profilling.users
    bar=get_progressive_bar(users.count())
    corpus=[]
    finish_count=0
    y=[]
    for user in users.find():
        if 'descriptions' not in user['information']:
            continue
        description=user['information']['descriptions']
        corpus.append(get_str_description(description))
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
        if user['information']['gender']=='m':
            y.append(1)
        else:
            y.append(0)
    x = vectorizer.fit_transform(corpus)
    all_data_x=x.toarray()
    all_data_y=numpy.array(y)
    dump_train_valid_test(all_data_x,all_data_y,'gender_description.data')

def output_name_matrix():
    from sklearn.feature_extraction.text import CountVectorizer
    lastnames=[name.replace('\n','').decode('utf8') for name in open('./lastname')]
    vectorizer = CountVectorizer(analyzer='char_wb',ngram_range=(1,3),min_df=1)
    from pymongo import Connection
    users=Connection().user_profilling.users
    bar=get_progressive_bar(users.count())
    corpus=[]
    finish_count=0
    y=[]
    for user in users.find():
        #if finish_count>1000:
        #    break
        name=user['screen_name']
        normal_name=[]
        for n in name:
            if n[0] in lastnames:
                normal_name.append(n[1:])
            else:
                continue
                #normal_name.append(n)
        corpus.append(' '.join(normal_name))
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
        if user['information']['gender']=='m':
            y.append(1)
        else:
            y.append(0)
    x = vectorizer.fit_transform(corpus)
    fe=vectorizer.get_feature_names()
    for f in fe:
        print f.encode('utf8')
    all_data_x=x.toarray()
    all_data_y=numpy.array(y)
    dump_train_valid_test(all_data_x,all_data_y,'gender_name.data')


def output_name_matrix_of_two_words():
    from helper import get_progressive_bar
    from pymongo import Connection
    users=Connection().user_profilling.users
    lastnames=[name.replace('\n','').decode('utf8') for name in open('./lastname')]
    bar=get_progressive_bar(users.count())
    finish_count=0
    tf=pickle.load(open('./tf.data'))
    x=[]
    y=[]
    for user in users.find():
        name=user['screen_name']
        finish_count+=1
        if finish_count>5000:
            break
        for n in name:
            if n[0] not in lastnames or len(n)>3 and len(n)<3:
                continue
            try:
                x0=1.0*tf[n[1]][0]/sum(tf[n[1]])
                x1=1.0*tf[n[2]][0]/sum(tf[n[2]])
            except:
                continue
            if user['information']['gender']=='m':
                y.append(1)
            else:
                y.append(0)
            x.append([x0,x1])
        bar.cursor.restore()
        bar.draw(value=finish_count)
    dump_train_valid_test(x,y,'gender_name_simple.data')


def output_graph_matrix():
    from pymongo import Connection
    users=Connection().user_profilling.users
    graph=Connection().user_profilling.graph_embedding
    print graph.count()
    bar=get_progressive_bar(users.count())
    x=[]
    y=[]
    finish_count=0
    for user in users.find({'int_id':{'$exists':True}},{'information':1,'int_id':1}):
        finish_count+=1
        print finish_count
        #bar.cursor.restore()
        #bar.draw(value=finish_count)
        user_embedding=graph.find_one({'_id':user['int_id']})
        if user_embedding is None:
            print user_embedding
            continue
        gender=user['information']['gender']
        if gender=='f':
            y.append(0)
        else:
            y.append(1)
        x.append(user_embedding['embedding'])
    dump_train_valid_test(x,y,'gender_graph.data')

if __name__=='__main__':
    print '=================Helper================='
    #output_age_matrix_from_bag_of_words()
    #output_age_matrix()
    #output_description_matrix()
    #output_name_matrix()
    #output_name_matrix_of_two_words()
    output_graph_matrix()
