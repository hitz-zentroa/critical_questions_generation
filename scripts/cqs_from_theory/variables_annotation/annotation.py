import sys
from pathlib import Path
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

import re
import csv
import random
import json

random.seed(2017)

def save_dataset(file_name, data, keys, col_names):

    instances = []
    for key, value in data.items():
        if key in keys:
            for line in value:
                line.append(file_name)
                instances.append(line)

    with open('data/to_annotate/variables/' + file_name + '.csv', 'w') as o:
        w = csv.writer(o)
        w.writerow(col_names)
        w.writerows(instances)

def main():
    dataset = sys.argv[1]

    with open('data/by_intervention/'+dataset+'.json') as f:
        data=json.load(f)

    l = list(data.items())
    random.shuffle(l)
    data_shuffled = dict(l)

    out_by_entry = {}
    repeated_key=[]
    for key,intervention in data_shuffled.items():
        out = []
        for arg in intervention['FULL_ARGS']:

            for p in arg['premises']:
                variables = re.findall(r'<[a-zA-Z0-9\_]*>', p)
                set_variables = []
                for v in variables:
                    if v not in set_variables:
                        set_variables.append(v)

                for v in set_variables:
                    if '_A_' not in arg['id']:
                        out.append([key, arg['id'], arg['scheme'], arg['propositions'][0] + '\nRELATED TO\n' + arg['propositions'][1], '\n'.join(arg['premises']), v, '', '', intervention['INTERVENTION'], '', ''])
                    else:
                        out.append([key, arg['id'], arg['scheme'],
                                    arg['propositions'][0] + '\nIS ANSWERING TO SOMEONE ELSE\'S SENTENCE: \n\"' + arg['propositions'][1]+'\"',
                                    '\n'.join(arg['premises']), v, '', '', intervention['INTERVENTION'], '', ''])

        out_by_entry[key] = out

    print(len(out_by_entry)) # I somehow loose 7 examples in us2016 and 13 in moral maze
    col_names = ['INTER_ID','ARG_ID', 'SCHEMA', 'PROPOSITIONS', 'PREMISES', 'VARIABLE', 'ANNOTATION', 'INVALID', 'CONTEXT', 'USED_CONTEXT?',
            'NOTES', 'ORIGIN']

    save_dataset(dataset, out_by_entry, list(out_by_entry.keys()), col_names)



if __name__ == "__main__":
    main()