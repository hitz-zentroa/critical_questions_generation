import json
import glob
import os
import re
from label_studio_sdk import Client
import sys
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

def main():
    dataset = sys.argv[1]
    project_id = int(sys.argv[2]) # 16

    already_anotated = get_list_of_already_annotated(project_id)

    ls = Client(url=yaml_config['label_studio']['port'], api_key=yaml_config['label_studio']['token'])

    with open("data/llm_generation/splitted_cqs_" + dataset +'.json') as f:
        data=json.load(f)

    for line in data:
        if line['data']['id'] not in already_anotated:
            project = ls.get_project(id=project_id)
            project.import_tasks(line)

if __name__ == "__main__":
        main()