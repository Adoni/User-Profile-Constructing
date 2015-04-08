import cPickle
result=cPickle.load(open('./result.data'))
print len(result)
def get_precision(category):
    total=0
    true=0
    for r in result:
        if r[0]==category:
            total+=1
        else:
            continue
        if r[1]==r[0]:
            true+=1
    return 1.0*true/total

def get_recall(category):
    total=0
    true=0
    for r in result:
        if r[1]==category:
            total+=1
        else:
            continue
        if r[1]==r[0]:
            true+=1
    return 1.0*true/total

if __name__=='__main__':
    print get_precision(1)
    print get_recall(1)
