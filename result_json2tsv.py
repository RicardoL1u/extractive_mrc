import json
json_result = json.load(open('ckpt/roberta_large_warmup_0.1/predict_nbest_predictions.json'))

tsv = [line.strip().split('\t') for line in open('template_result.txt')]

for data in tsv:
    data[1] = json_result[data[0]][0]['text']
    data.append(data[2])
    data[2] = str(json_result[data[0]][0]['start'])

final = ['\t'.join(data)+'\n' for data in tsv]

with open('roberta_large.txt','w') as f:
    f.writelines(final)
