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


def get_nodes(file_name):
    nodes=[]
    for line in open(file_name):
        nodes.append(int(line.replace('\n','')))
    return nodes


def save_zero_jump_nodes():
    from pymongo import Connection
    users=Connection().user_profilling.users
    int_ids=[]
    for user in users.find({},{"int_id":1}):
        try:
            int_id=int(user['int_id'])
            int_ids.append(int_id)
        except:
            continue
    int_ids=sorted(int_ids)
    zero_file=open('./nodes/0.data','w')
    for int_id in int_ids:
        zero_file.write(str(int_id)+'\n')


def save_new_nodes(previous_nodes_files,new_nodes_file):
    previous_nodes=[]
    for f in previous_nodes_files:
        previous_nodes+=get_nodes('./nodes/'+str(f)+'.data')
    previous_nodes=sorted(previous_nodes)
    MAXI=len(previous_nodes)
    i=0
    file_name='/mnt/data1/weibo_graph/weibo_socialgraph.txt'
    new_nodes=[]
    bad_nodes=[]
    print previous_nodes[i]
    for line in open(file_name):
        if i>=MAXI:
            break
        line_num=int(line[0:line.find(' ')])
        if line_num%1000000==0:
            print line_num
        if line_num==previous_nodes[i]:
            line=line.replace('\n','').split(' ')
            neibors=[]
            for neibor in line:
                try:
                    neibors.append(int(neibor))
                except Exception as e:
                    print e
                    continue
            i+=1
            for node in line[2:]:
                if node in previous_nodes:
                    continue
                new_nodes.append(node)
            continue
        if line_num>previous_nodes[i]:
            bad_nodes.append(previous_nodes[i])
            while i<MAXI and line_num>previous_nodes[i]:
                i+=1
    new_nodes=sorted(new_nodes)
    new_nodes_file=open('./nodes/'+str(new_nodes_file)+'.data','w')
    for node in new_nodes:
        new_nodes_file.write(str(node)+'\n')
    bad_nodes_file=open('./nodes/'+str(new_nodes_file)+'.data','w')
    for node in bad_nodes:
        bad_nodes_file.write(str(node)+'\n')


def test():
    file_name='/mnt/data1/weibo_graph/weibo_socialgraph.txt'
    i=0
    for l in open(file_name):
        ln=int(l[0:l.find(' ')])
        if not i==int(ln):
            print i
            print ln
            print l
            i=ln
        i+=1
if __name__=='__main__':
    #test()
    save_new_nodes([0],1)
    save_new_nodes([0,1],2)
