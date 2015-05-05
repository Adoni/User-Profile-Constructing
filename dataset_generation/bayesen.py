import pickle


def get_tf():
    from helper import get_progressive_bar
    from pymongo import Connection
    users=Connection().user_profilling.users
    lastnames=[name.replace('\n','').decode('utf8') for name in open('./lastname')]
    bar=get_progressive_bar(users.count())
    finish_count=0
    tf=dict()
    for user in users.find():
        name=user['screen_name']
        finish_count+=1
        for n in name:
            if n[0] not in lastnames or len(n)>3 and len(n)<2:
                continue
            if user['information']['gender']=='m':
                gender=1
            else:
                gender=0
            for w in n[1:]:
                if w not in tf:
                    tf[w]=[0,0]
                tf[w][gender]+=1
        bar.cursor.restore()
        bar.draw(value=finish_count)
    return tf


def test():
    from matplotlib import pyplot as plt
    x_m=[]
    y_m=[]
    x_f=[]
    y_f=[]
    from helper import get_progressive_bar
    from pymongo import Connection
    users=Connection().user_profilling.users
    lastnames=[name.replace('\n','').decode('utf8') for name in open('./lastname')]
    bar=get_progressive_bar(users.count())
    finish_count=0
    tf=pickle.load(open('./tf.data'))
    for user in users.find():
        name=user['screen_name']
        finish_count+=1
        if finish_count>5000:
            break
        for n in name:
            if n[0] not in lastnames or len(n)>3 and len(n)<3:
                continue
            try:
                x=1.0*tf[n[1]][0]/sum(tf[n[1]])
                y=1.0*tf[n[2]][0]/sum(tf[n[2]])
            except:
                continue
            if user['information']['gender']=='m':
                x_m.append(x)
                y_m.append(y)
            else:
                x_f.append(x)
                y_f.append(y)
        bar.cursor.restore()
        bar.draw(value=finish_count)
    plt.plot(x_m,y_m,'r*')
    plt.plot(x_f,y_f,'g.')
    plt.show()


if __name__=='__main__':
    test()
