#coding:utf8
import urllib2
import numpy
import json
import cPickle

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
    cPickle.dump(word_vectors,open('parameters.bin','wb'))
    print 'dump done'

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
    from progressive.bar import Bar
    from pymongo import Connection
    words=[w[0:-1].decode('utf8') for w in open('./word.feature')]
    all_data_x=[]
    all_data_y=[]
    index=0
    #进度条相关参数
    users=Connection().user_image.users
    total_count=users.count()
    bar=Bar(max_value=total_count,fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
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
                text[words.index(word)]+=1.0
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
    print b
    print c
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
    cPickle.dump((train_set,valid_set,test_set),open('gender_matrix.data','wb'))


def output_age_matrix():
    from progressive.bar import Bar
    word_vectors=get_vectors('./word_vectors2.data')
    word_count=600
    all_data_x=[]
    all_data_y=[]
    index=0
    #进度条相关参数
    total_count=20000
    bar=Bar(max_value=total_count,fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    finish_count=0
    for line in open('./users.data'):
        user=parse_user(line)
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
        if user['gender']=='m':
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
    cPickle.dump((train_set,valid_set,test_set),open('gender_matrix.data','wb'))

if __name__=='__main__':
    print '=================Helper================='
    output_age_matrix_from_bag_of_words()
