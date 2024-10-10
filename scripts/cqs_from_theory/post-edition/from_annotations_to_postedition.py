import json
import csv
import sys
import re
from pathlib import Path
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))


def join_annotations(data):
    #already_there = []
    joint_data = []
    for dataset in ['ann1', 'ann2','four_datasets','ex_vc', 'ex_vc_four', 'missing_variables']: #['missing_variables_annotation - missing3'] needs +1 in construct_output ids
        for line in data[dataset]:
            joint_data.append(line)

    return joint_data

def construct_output(dataset, by_intervention, data):
    for key, value in by_intervention.items():
        if 'answering' in value['comment'].keys():
            value['VISUAL_INTERVENTION'] = value['id'].split('_')[0]+': "'+value['INTERVENTION'] + '"\n < this message is answering to > \n' + value['comment']['answering'] + ': "' + value['comment']['with_message']+'"'
        elif dataset == 'EO_PC':
            value['VISUAL_INTERVENTION'] = value['INTERVENTION']
        else:
            value['VISUAL_INTERVENTION'] = value['id'].split('_')[0]+': "'+value['INTERVENTION']+'"'
        for arg in value['FULL_ARGS']:
            arg['instantiated_premises'] = arg['premises']
            arg['instantiated_cqs'] = arg['cqs']
            arg['comment'] = ''
            found_match = False
            for annotation in data:
                if annotation[0] == arg['id']: # todo: this should be [1] if the annotations were in the new format. all the indexes should be addapted
                    found_match=True
                    if annotation[6] in ['does not fit', 'lack of context']:
                        arg['comment'] = annotation[6]
                        arg['instantiated_premises'] = ''
                        arg['instantiated_cqs'] = ''
                    else:

                        modified = []
                        for p in arg['instantiated_premises']:
                            ch_p = p.replace(annotation[4], annotation[5])
                            modified.append(ch_p)
                        arg['instantiated_premises'] = modified

                        cqs_modified = []
                        for p in arg['instantiated_cqs']:
                            if annotation[4] == '<subjecta>' and annotation[5] == 'you' and 'answering' in value['comment'].keys():
                                anot = value['comment']['answering']
                            else:
                                anot = annotation[5]
                            ch_p = p.replace(annotation[4], anot)
                            cqs_modified.append(ch_p)
                        arg['instantiated_cqs'] = cqs_modified
            # exit()
            for sentence in arg['instantiated_premises']+arg['instantiated_cqs']:
                if re.findall(r'<[a-zA-Z0-9\_]*>', sentence):
                    #print(arg)
                    #print('Issue in', arg['id'], arg['scheme'], sentence)
                    arg['comment'] = 'does not fit'
                    arg['instantiated_premises'] = ''
                    arg['instantiated_cqs'] = ''
    return by_intervention


def main():
    dataset = sys.argv[1]
    with open('data/by_intervention/'+dataset+'.json') as f:
        by_intervention = json.load(f)
    #print(by_intervention.keys())
    # LOAD BOTH ANNOTATION DATASETS
    data = {}
    for d in ['ann2', 'ann1', 'ex_vc', 'ex_vc_four', 'four_datasets', 'missing_variables']: #['missing_variables_annotation - missing3'] needs +1 in construct_output ids
        data[d] = []
        with open('data/annotated/variables/'+d+'.csv') as f:
            r = csv.reader(f)
            next(r)
            for line in r:
                if d != 'missing_variables':
                    data[d].append(line)
                else:
                    data[d].append(line[1:]) # this dataset includes the intervention id in the first colum

    # JOIN THE TWO ANNOTATIONS, IN IAA KEEP ANN2 AND REMOVE THE ONES THAT DO NOT FIT
    all_joint_data = join_annotations(data)

    out = construct_output(dataset, by_intervention, all_joint_data)

    # save the dataset as is, and save a csv for post-edition
    with open('data/by_intervention/instantiated_'+dataset+'.json', 'w') as o:
        json.dump(out, o, indent=5)

    with open('data/to_annotate/postedition/'+dataset+'.csv', 'w') as o:
        w=csv.writer(o)
        w.writerow(['id_intervention', 'intervention', 'arg_id', 'cq_id', 'cq', 'postedition', 'label'])
        for key, value in out.items():
            for arg in value['FULL_ARGS']:
                for i,cq in enumerate(arg['instantiated_cqs']):
                        w.writerow([value['id'], value['VISUAL_INTERVENTION'], arg['id'], i, cq])


if __name__ == "__main__":
        main()