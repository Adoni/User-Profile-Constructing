#coding:utf8
from matplotlib import pyplot as plt
from pymongo import Connection
from dateutil import parser
import urllib2
import numpy
import json
import cPickle

access_token = '2.00L9khmFlxpd6C91aec9ef010s3KCc'
word_vector_size=500
time_vector_size=24

correct_sources=[' '.join(l.split(' ')[:-1]).decode('utf8') for l in open('./source.txt')]
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

def plot_age_distribute():
    user_ages=get_user_ages()
    ages=[0]*5
    total=0
    db=Connection()
    user_image=db.user_image
    users_with_age=user_image.user_age
    count=0
    for user in users_with_age.find():
        uid=user['information']['uid']
        if len(user['statuses'])<50:
            continue
        age=user_ages[uid]
        if age<5 or age>=100:
             continue
        count+=1
        ages[get_age_class(age)]+=1.0
        total+=1.0

    print count
    for i in range(0,5):
        ages[i]/=total
    #plt.plot(range(0,4),ages,'*-')
    explode = (0.1, 0.1, 0.1, 0.1, 0.1)
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    plt.pie(
            ages,
            labels=[
                u'00后',
                u'90后',
                u'80后',
                u'70后',
                u'',
                ],
            autopct='%1.1f%%',
            #shadow=True,
            startangle=90,
            explode=explode,
            colors=colors
            )
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def output_uids_without_age():
    f=open('./candidates_with_ages.data')
    fout=open('./age_uids.data','w')
    for l in f:
        l=l.replace('\n','').replace('\r','')
        try:
            age=int(l.split('\t')[1])
            if age>=100:
                continue
            if age<5:
                continue
            fout.write(l.split('\t')[0]+'\n')
        except:
            continue

def get_vectors(file_name):
    print 'Getting vectors...'
    f=open(file_name)
    vectors=dict()
    for line in f:
        line=line.decode('utf8')
        line=line.split(' ')
        try:
            line.remove('\n')
        except Exception as e:
            print e
        key=line[0]
        vector=[0]*(len(line)-1)
        for i in range(1,len(line)):
            vector[i-1]=float(line[i])
        vectors[key]=numpy.array(vector)
    print 'Done'
    return vectors

def get_hour(str_time):
    str_time=str_time.replace(u'日','')
    str_time=str_time.replace(u'月','-')
    str_time=str_time.replace(u'今天 ','')
    t=parser.parse(str_time)
    h=t.hour
    return str(h)

def dump_vectors():
    word_vectors=get_vectors('../global/word_vectors.data')
    cPickle.dump(word_vectors,open('parameters.bin','wb'))

def get_text_convolution(text):
    text_convolution=[]
    for t in text:
        text_convolution+=t
    return text_convolution

def output_age_matrix():
    from progressive.bar import Bar
    #ages=get_user_ages()
    db=Connection()
    user_image=db.user_image
    users=user_image.users#_age
    #word_vectors=get_vectors('../global/word_vectors.bin')
    #word_vectors=cPickle.load(open('./parameters_200.bin','rb'))
    time_vectors=get_vectors('../global/time_vectors.bin')
    all_data_x=[]
    all_data_y=[]
    index=0
    window_size=2
    word_vector_size=200
    text_vector_size=window_size*word_vector_size
    time_vector_size=24
    image_vector_size=word_vector_size
    #进度条相关参数
    total_count=users.count()
    bar=Bar(max_value=total_count,fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    finish_count=0
    for user in users.find({'got_image_descriptions':True}):
        #age=ages[uid]
        #根据用户年龄过滤
        #if age>=100 or age<=5:
        #    continue
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
        # text_vector=[numpy.zeros(text_vector_size)]
        # time_vector=[numpy.zeros(time_vector_size)]
        # image_vector=[numpy.zeros(image_vector_size)]
        # for description in user['information']['descriptions']:
        #     for word in description:
        #         try:
        #             image_vector.append(word_vectors[word])
        #         except:
        #             continue
        # if len(image_vector)==1:
        #     continue
        text=[]
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            for word in status['text']:
                try:
                    text.append(word_vectors[word])
                except Exception as e:
                    continue
            if len(text)>100:
                continue
            #sentence_vector=[]
            #for word in status['text']:
            #    try:
            #        sentence_vector.append(list(word_vectors[word]))
            #    except:
            #        continue
            #for i in range(0,len(sentence_vector)-window_size):
            #    text.append(get_text_convolution(sentence_vector[i:i+window_size]))
            # created_at=status['time']
            # try:
            #     hour=get_hour(created_at)
            #     time_vector.append(time_vectors[hour])
            # except Exception as e:
            #     continue
            #     pass
            # length.append(len(status['text']))
        # text_vector_mean=numpy.mean(text_vector,axis=0)
        # if len(text)<50:
        #     continue
        text=text[0:100]
        text_vector=numpy.array(text)#numpy.max(text_vector,axis=0)
        #text_vector=numpy.max(text,axis=0)
        text_vector=text_vector.reshape((text_vector.shape[0]*text_vector.shape[1]))
        # time_vector=numpy.sum(time_vector,axis=0)
        #data.append(get_age_class(age))
        if user['information']['gender']=='m':
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
    cPickle.dump((train_set,valid_set,test_set),open('gender_matrix_with_time.data','wb'))

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

def show_data():
    db=Connection()
    user_image=db.user_image
    users_with_age=user_image.user_age
    for user in users_with_age.find(limit=10):
        print '==============='
        print user['information']['screen_name']
        for status in user['statuses']:
            print ''.join(status['text'])

def get_user_ages():
    f=open('./candidates_with_ages.data')
    ages=dict()
    for line in f:
        line=line.replace('\n','').split('\t')
        try:
            age=int(line[1])
            ages[line[0]]=age
        except Exception as e:
            print e
            print line
            continue
    return ages

def get_html(url):
    try:
        return urllib2.urlopen(url).read()
    except Exception as e:
        print e
        return ''

def get_all_fridend(uid):
    base_url='https://api.weibo.com/2/friendships/friends/bilateral.json?'
    base_url='https://api.weibo.com/2/friendships/friends.json?'
    complete_url=base_url+'access_token='+access_token+'&uid='+str(uid)+'&count=100'
    html=get_html(complete_url)
    if(html=='' or 'error' in html):
        print('error')
        print(complete_url)
        return None
    html=html
    try:
        json_data=json.loads(html)
    except:
        print html
        return None
    return json_data['users']

def check_users():
    db=Connection()
    user_image=db.user_image
    users=user_image.users
    for user in users.find():
        print '=========='
        print user['information']['screen_name']
        print user['information']['verified']
        word_count=0
        for status in user['statuses']:
            if is_not_good_status(status):
                continue
            if len(status['text'])>100:
                continue
            #print ''.join(status['text'])
            word_count+=len(status['text'])
            #print len(status['text'])
            #print status['source']
        print word_count

def find_friend_rate():
    ages=get_user_ages()
    X=[]
    Y=[]
    i=0
    for uid in ages:
        i+=1
        print i
        if i>100:
            break
        age=ages[uid]
        friends=get_all_fridend(uid)
        if friends==None:
            continue
        m=0
        f=0
        for friend in friends:
            if friend['gender']=='m':
                m+=1
            else:
                f+=1
        X.append(ages[uid])
        Y.append(1.0*(m+1)/(f+1))
    plt.scatter(X,Y)
    plt.show()

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
    dump_vectors()
    #output_uids_without_age()
    #plot_age_distribute()
    #gen_emoticon_vectors()
    #output_age_matrix()
    #get_word_vectors()
    #show_data()
    #find_friend_rate()
    #get_parameters()
    #save_vectors('../global/word_vectors.bin')
    #check_users()
    #pkl2svm()
    #plot_test()
    #age_matrix_2_gender_matrix()
