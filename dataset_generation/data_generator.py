#coding:utf8
import urllib2
import numpy
import json
import cPickle

access_token = '2.00L9khmFlxpd6C91aec9ef010s3KCc'
word_vector_size=500
time_vector_size=24

correct_sources=[' '.join(l.split(' ')[:-1]) for l in open('./source.txt')]
def is_not_good_status(status):
    source=status['source']
    if source==None:
        return True
    if 'O网页链接' in ''.join(status['text']):
        return True
    if source in correct_sources:
        return False
    if source.endswith('手机'):
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

def output_age_matrix():
    from progressive.bar import Bar
    #word_vectors=cPickle.load(open('./parameters_200.bin','rb'))
    word_vectors=get_vectors('./word_vectors2.data')
    words_count=600
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
        #根据合法status数量过滤
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
                    #print type(word)
                    #print word
                    #print e
                    continue
            if len(text)>words_count:
                break
        if len(text)<words_count:
            continue
        text=text[0:words_count]
        text_vector=numpy.array(text)#numpy.max(text_vector,axis=0)
        #text_vector=numpy.max(text,axis=0)
        text_vector=text_vector.reshape((text_vector.shape[0]*text_vector.shape[1]))
        # time_vector=numpy.sum(time_vector,axis=0)
        #data.append(get_age_class(age))
        if user['gender']=='m':
            all_data_y.append(1)
        else:
            all_data_y.append(0)
        # data=data+list(text_vector_mean)+list(time_vector)+list(numpy.max(image_vector,axis=0))+[numpy.max(length),numpy.min(length),numpy.mean(length),len(length)]
        #data=data+list(time_vector)+[numpy.max(length),numpy.min(length),numpy.mean(length),len(length)]
        #data=data+list(text_vector)
        all_data_x.append(text_vector)
        #all_data.append(data)
        index+=1
        finish_count+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
        #if finish_count>500:
        #    break
    all_data_x=numpy.array(all_data_x)
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

def gen_emoticon_vectors():
    f=open('./emoticon_vectors.bin','w')
    all_emoticons=[]
    db=Connection()
    user_image=db.user_image
    users=user_image.users
    for user in users.find():
        for status in user['statuses']:
            emoticons=status['emoticons']
            for e in emoticons:
                if e in all_emoticons:
                    continue
                all_emoticons.append(e)
    print len(all_emoticons)

def gen_time_vectors():
    f=open('./time_vectors.bin','w')
    for i in range(0,24):
        v=['0']*24
        v[i]='1'
        f.write(str(i)+' ')
        f.write(' '.join(v)+'\n')
    f.close()

def pkl2svm():
    data=cPickle.load(open('./gender_matrix.data','rb'))
    train,valid,test=data
    f=open('./train','w')
    x=train[0]
    y=train[1]
    for i in range(0,y.shape[0]):
        f.write(str(int(y[i])))
        for j in range(0,600):
            f.write(' '+str(j)+':'+str(x[i][j]))
        f.write('\n')
    f=open('./test','w')
    x=test[0]
    y=test[1]
    for i in range(0,y.shape[0]):
        f.write(str(int(y[i])))
        for j in range(0,524):
            f.write(' '+str(j)+':'+str(x[i][j]))
        f.write('\n')

def age_matrix_2_gender_matrix():
    data=cPickle.load(open('./age_matrix.data','rb'))
    train_set,valid_set,test_set=data
    train_set=(train_set[0][:,1:],train_set[0][:,:1].reshape(train_set[0].shape[0]))
    valid_set=(valid_set[0][:,1:],valid_set[0][:,:1].reshape(valid_set[0].shape[0]))
    test_set=(test_set[0][:,1:],test_set[0][:,:1].reshape(test_set[0].shape[0]))
    cPickle.dump((train_set,valid_set,test_set),open('gender_matrix.data','wb'))


if __name__=='__main__':
    print '=================Helper================='
    #dump_vectors()
    #output_uids_without_age()
    #plot_age_distribute()
    #gen_emoticon_vectors()
    output_age_matrix()
    #get_word_vectors()
    #show_data()
    #find_friend_rate()
    #get_parameters()
    #save_vectors('../global/word_vectors.bin')
    #check_users()
    #pkl2svm()
    #plot_test()
    #age_matrix_2_gender_matrix()
