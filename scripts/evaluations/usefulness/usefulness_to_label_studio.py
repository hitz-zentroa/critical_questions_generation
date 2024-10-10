import json
import glob
import os
import re
from label_studio_sdk import Client
import yaml
import random

import sys
from pathlib import Path
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from utils.load_data import id_selection_p1

with open('scripts/utils/config.yaml', 'r') as file:
    yaml_config = yaml.safe_load(file)

def main():
    bloc = sys.argv[1]

    ls = Client(url=yaml_config['label_studio']['port'], api_key=yaml_config['label_studio']['token'])

    # the data in the annotation trial
    trial_selection = id_selection_p1()
    print('interventions in trial:', len(trial_selection))

    models = ['llama-3-big'] # 'llama-2', 

    datasets = ['moral_maze_schemes', 'US2016', 'us2016reddit', 'rrd']#, 'EO_PC']

    data = []
    intervention_id_to_visual = {}
    print('dataset', 'count_interventions', 'count_theory_cqs', 'count_llm_cqs', 'ratio_theory_cqs', 'ratio_llm_cqs')
    for dataset in datasets:
        count_llm_cqs = 0
        for model in models:
            with open("data/llm_generation/"+model+"/splitted_cqs_" + dataset +'.json') as f:
                llm_cqs = json.load(f)
                for line in llm_cqs:
                    if 'Llama-3-70B' in line['data']['id']:
                        count_llm_cqs += 1
                        data.append(line)

        with open("data/theory_cqs_by_intervention/"+dataset+'.json') as f:
            theory_data = json.load(f)

        count_theory_cqs = 0
        count_interventions = 0
        for key, line in theory_data.items():
            intervention_id_to_visual[key] = line['VISUAL_INTERVENTION']
            if 'theory_cqs' in line.keys():
                if line['theory_cqs']:
                    count_interventions += 1
                for i, cq in enumerate(line['theory_cqs']):
                    data.append({'data': {'id': line['id']+'_T_'+'_'+str(i),
                                            'intervention': line['VISUAL_INTERVENTION'], # changed this now
                                                'cq': cq,
                                        'intervention_id': line['id']}})
                    count_theory_cqs += 1
        print(dataset, count_interventions, count_theory_cqs, count_llm_cqs, round(count_theory_cqs/count_interventions, 2), round(count_llm_cqs/count_interventions, 2))

    # change all the interventions of llm_cqs for the visual_interventions in theory_cqs
    for line in data:
        line['data']['intervention'] = intervention_id_to_visual[line['data']['intervention_id']]

    # UPLOADING PART --> by blocs
                
    print('all cqs:', len(data))
    #exit()

    random.shuffle(data) # desordenamos los datos pero mantenemos el intervention_id para ordenarlos luego
    sorted_data = sorted(data, key=lambda x: x['data']['intervention_id'])

    # divide in 6 blocs, upload by bloc to the 6 different projects
    remaining = []
    for line in sorted_data:
        if line['data']['intervention_id'] in trial_selection:
            #project = ls.get_project(id=11)
            #project.import_tasks(line)
            pass
        else:
            remaining.append(line)

    print('cqs without trial interventions:', len(remaining))
    exit()

    anns = ['1','2']
    for a in anns:
        project_id = yaml_config['divisions']['bloc_'+bloc]['ann_'+a]['project_id']
        for line in remaining[yaml_config['divisions']['bloc_'+bloc]['ann_'+a]['from']:yaml_config['divisions']['bloc_'+bloc]['ann_'+a]['to']]:
            if line['data']['intervention_id'] not in trial_selection:
                project = ls.get_project(id=project_id)
                project.import_tasks(line)
            
    #with open('data/to_annotate/usefulness/sorted_data.json', 'w') as o:
    #    json.dump(sorted_data, o, indent=5)

if __name__ == "__main__":
        main()