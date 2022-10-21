import json
with open('refine_dataset.json','r',encoding='utf-8')as f:
    data=json.load(f)['data']
ans={}
rat={}
label_0={}
with open('mrc_rationale_xbase_attention_20221014_2.txt','r',encoding='utf-8') as f:
    for line in f:
        t_1=line.find('\t')
        id_=int(line[:t_1])
        line=line[t_1+1:]
        t_2=line.find('\t')
        answer=line[:t_2]
        answer=answer.replace('#','')
        ans[id_]=answer
        line=line[t_2+1:-1]
        t_3=line.find('\t')
        label_0_index=int(line[:t_3])
        label_0[id_]=label_0_index
        line=line[t_3+1:]
        rat[id_]=line
ans_vote=[]
for term in data:
    answer=[]
    for item in term:
        if '[CLS]' in ans[item['id']] and '[SEP]' in ans[item['id']]:
            index_sep=ans[item['id']].index('[SEP]')
            ans[item['id']]=ans[item['id']][index_sep+5:]
            print(ans[item['id']])
        answer.append(ans[item['id']])
    set_a=set(answer)
    dict_a={}
    for i in set_a:
        dict_a[i]=answer.count(i)
    list_b=list(dict_a.items())
    list_c=sorted(list_b,key=lambda x:x[1],reverse=True)
    tmp=[]
    for i in list_c:
        if i[1]==list_c[0][1]:
            tmp.append(i[0])
        else:
            break
    if '' in tmp:
        tmp.remove('')
    if '[CLS]' in tmp:
        tmp.remove('[CLS]')
    if '[SEP]' in tmp:
        tmp.remove('[SEP]')
    tmp=sorted(tmp,key=lambda x:len(x),reverse=False)
    ans_vote.append(tmp)

i=0
for term in data:
    answer=ans_vote[i]
    if answer==[]:
        i+=1
        continue
    for item in term:
        ans[item['id']]=answer[0]
    i+=1
signal=['，','。','：','？','！',' ']
i=0
for term in data:
    answer=ans_vote[i]
    if answer==[]:
        i+=1
        continue
    flag=0
    for item in term:
        if item['context'][label_0[item['id']]]==answer[0][0]:
            flag=1
            break
    if flag!=0:
        label_item=item
        label_index=label_0[item['id']]
    else:
        for item in term:
            if answer[0] in item['context'].lower():
                label_item=item
                label_index=item['context'].lower().find(answer[0])
                flag=1
                break
    front=label_item['context'][:label_index]
    behind=label_item['context'][label_index+len(answer[0]):]
    front_1=[]
    for sig in signal:
        if sig in front:
            front_1.append(front.rfind(sig))
    if front_1!=[]:
        head=max(front_1)+1
    else:
        head=0
    behind_1=[]
    for sig in signal:
        if sig in behind:
            behind_1.append(behind.find(sig))
    if behind_1!=[]:
        tail=min(behind_1)
    else:
        tail=len(behind)
    analysis=front[head:]+answer[0]+behind[:tail]
    for item in term:
        rationale_token=[]
        for j in analysis:
            if j in item['context']:
                token=item['context'].find(j)
                rationale_token.append(str(token))
        token_str=','.join(rationale_token)
        rat[item['id']]=token_str
    i+=1
new_result={}
new_result['data']=[]
for term in data:
    for item in term:
        item['rationale']=rat[item['id']].split(',')
        item['rationale_token']=[item['context'][int(i)] for i in item['rationale']]
        item['sent_token']=[]
    new_result['data'].append(term)
with open('new_result_.json','w',encoding='utf-8') as f:
    json.dump(new_result,f,ensure_ascii=False,indent=4)
with open('new_result_.txt','w',encoding='utf-8') as f:
    for id_,answer in ans.items():
        str_=str(id_)+'\t'+str(answer)+'\t'+rat[id_]+'\n'
        f.write(str_)