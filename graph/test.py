import pickle
def get_progressive_bar(total_count):
    from progressive.bar import Bar
    bar=Bar(max_value=total_count,fallback=True)
    bar.cursor.clear_lines(2)
    bar.cursor.save()
    return bar


def update_user_id():
    GRAPH_DATA_DIR='/mnt/data1/weibo_graph/'
    id_map_file=open(GRAPH_DATA_DIR+'id_map.txt')
    uids=dict()
    total_count=107628903
    finish_count=0
    #bar=get_progressive_bar(total_count=total_count)
    for line in id_map_file:
        line=line.replace('\n','').split(' ')
        uids[line[0]]=line[1]
        finish_count+=1
        #bar.cursor.restore()
        #bar.draw(value=finish_count)
    #uids=set(uids)
    from pymongo import Connection
    users=Connection().user_profilling.users
    count=0
    finish_count=0
    u=set()
    for user in users.find({},{'uid':True}):
        finish_count+=1
        uid=user['uid']
        u.add(uid)
        try:
            int_id=uids[uid]
        except Exception as e:
            continue
        users.update({'_id':user['_id']},{'$set':{'int_id':int_id}})
        #bar.cursor.restore()
        #bar.draw(value=finish_count)
    uids=set(uids.keys())
    together=uids & u
    print len(together)
    print len(uids)
    print len(u)
    #pickle.dump(together,open('co-occurrence.data','wb'))


if __name__=='__main__':
    update_user_id()
