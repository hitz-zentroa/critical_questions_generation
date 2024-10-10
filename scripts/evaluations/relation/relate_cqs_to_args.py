
import os
import glob
import re
import json
from label_studio_sdk import Client
import yaml

with open('scripts/utils/config.yaml', 'r') as file:
    yaml_config = yaml.safe_load(file)

def get_list_of_already_annotated(project):
    # if the task is already there, do not upload it again
    list_of_files = glob.glob(r"/home/bcalvo/.local/share/label-studio/export/project-"+str(project)+"*.json")
    latest_files = sorted(list_of_files, key=os.path.getctime, reverse=True)[:2]
    for file in latest_files:
        if not re.match(r"^.*info.*$", file):
            latest_file = file
    # print(latest_file)
    with open(latest_file) as f:
        annotations = json.load(f)
    already_uploaded_annotations = []
    for an in annotations:
        already_uploaded_annotations.append(
            an['data']['id'])  # TODO: if the task has not been annotated it gets uploaded again
    return already_uploaded_annotations

def load_annotations(data, group = False):

    list_of_paired_results = []
    for line in data:

        if line['annotations']:
            anot = line['annotations'][0]['result'][0]['value'].keys()
            if 'choices' in anot:
                if group:
                    if line['annotations'][0]['result'][0]['value']['choices'][0] in ['Incorrect: Non-critical']:
                        list_of_paired_results.append([line['data']['id'], line['data']['intervention'], line['data']['cq'], line['annotations'][0]['result'][0]['value']['choices'][0]])
                    else:
                        list_of_paired_results.append([line['data']['id'], line['data']['intervention'], line['data']['cq'],
                                                       'Incorrect'])
                else:
                    list_of_paired_results.append([line['data']['id'], line['data']['intervention'], line['data']['cq'],
                                              line['annotations'][0]['result'][0]['value']['choices'][0]])


    sort_the_the_list = sorted(list_of_paired_results)
    keep_the_ids = [i[0] for i in sort_the_the_list]

    return sort_the_the_list, keep_the_ids

def main():

    # get the file with the annotations
    project = 16
    list_of_files = glob.glob(r"/home/bcalvo/.local/share/label-studio/export/project-" + str(project) + "*.json")
    latest_files = sorted(list_of_files, key=os.path.getctime, reverse=True)[:2]
    for file in latest_files:
        if not re.match(r"^.*info.*$", file):
            latest_file = file
    # print(latest_file)
    with open(latest_file) as f:
        annotations = json.load(f)


    ungrouped, u_ids = load_annotations(annotations)
    print(len(u_ids))

    theory_data={}
    for dataset in ['moral_maze_schemes', 'US2016']:
        with open('data/by_intervention/postedited_'+dataset+'.json') as f:
            t=json.load(f)
            for key, value in t.items():
                theory_data[key] = value
                theory_data[key]['source'] = dataset

    project_out=15
    ls = Client(url=yaml_config['label_studio']['port'], api_key=yaml_config['label_studio']['token'])
    already_uploaded_annotations = get_list_of_already_annotated(project_out)

    for key,line in theory_data.items():

        llms_list = []
        found_one=False
        for ann in ungrouped:
            ann_id = '_'.join(a for a in ann[0].split('_')[0:-5])
            if ann_id == line['id']+'_'+line['source']:
                if ann[3] == "Correct":
                    found_one=True
                    llms_list.append((ann[0],ann[2])) # keep the original ids of the llm cqs

        if found_one:
            for arg in line['FULL_ARGS']:
                for i,cq in enumerate(arg['postedited_cqs']):
                    theory_cq_id = key+'_ARG_'+arg['id']+'_'+str(i) # the theory cqs do not have ids yet, so I can create them
                    out_json = {"data": {"id": theory_cq_id, "premises": '\n'.join(arg['instantiated_premises']), "cq": cq, "items": []}}

                    for question in llms_list:
                        out_json["data"]["items"].append({"body": question[1], "id": theory_cq_id+"_LLM_"+question[0]})

                    print(out_json)

                    if out_json['data']['id'] not in already_uploaded_annotations:
                        project = ls.get_project(id=project_out)
                        project.import_tasks(out_json)




if __name__ == "__main__":
        main()