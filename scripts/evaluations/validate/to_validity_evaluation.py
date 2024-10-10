

import os
import glob
import re
import json
import csv


def main():

    project = 15
    list_of_files = glob.glob(r"/home/bcalvo/.local/share/label-studio/export/project-" + str(project) + "*.json")
    latest_files = sorted(list_of_files, key=os.path.getctime, reverse=True)[:2]
    for file in latest_files:
        if not re.match(r"^.*info.*$", file):
            latest_file = file
    with open(latest_file) as f:
        annotations = json.load(f)

    llms_cqs_related_to_theory_cqs = []
    llms_cqs_related_to_argument = []
    for line in annotations:
        if line['annotations'][0]['result']:
            llms_cqs_related_to_theory_cqs.extend([i.split('_LLM_')[1] for i in line['annotations'][0]['result'][0]['value']['ranker']['same']])
            llms_cqs_related_to_argument.extend([i.split('_LLM_')[1] for i in line['annotations'][0]['result'][0]['value']['ranker']['same']])
            llms_cqs_related_to_argument.extend([i.split('_LLM_')[1] for i in line['annotations'][0]['result'][0]['value']['ranker']['not_same']])

    print(len(llms_cqs_related_to_theory_cqs))
    unique_related_to_theory = list(set(llms_cqs_related_to_theory_cqs))
    unique_related_argument = list(set(llms_cqs_related_to_argument))

    print(len(unique_related_to_theory), len(unique_related_argument))

    out = []
    for line in unique_related_argument:
        if line not in unique_related_to_theory:
            out.append(line)

    print(len(out)) # todo: what are these?

    # find in annotations which arguments are these 121 and output a csv with PREMISES, LLM CQ
    already_added = []
    to_csv = []
    same_questions = []
    for line in annotations:
        if line['annotations'][0]['result']:
            #print(line)

            theory_cq_id = line['data']['id'].split('_ARG_')[1]
            arg_id = '_'.join(theory_cq_id.split('_')[0:2])

            # output the llm cqs which were related to an argument but not the same of any of the theory cqs
            for item in line['annotations'][0]['result'][0]['value']['ranker']['not_same']:
                llm_cq_id = item.split('_LLM_')[1]
                if llm_cq_id in out and (arg_id, llm_cq_id) not in already_added: # troba quines son
                    # print(item)
                    # print(line['data']['items'])
                    already_added.append((arg_id, llm_cq_id))
                    for cq in line['data']['items']: # troba quina es textualment
                        if cq['id'].split('_LLM_')[1] == llm_cq_id:
                            to_csv.append([arg_id, llm_cq_id, line['data']['premises'], cq['body']])

            # outpt the llm cqs which were the same as a theory cq, keep the id of the related theory cq
            for item in line['annotations'][0]['result'][0]['value']['ranker']['same']:
                llm_cq_id = item.split('_LLM_')[1]
                for cq in line['data']['items']:
                    if cq['id'].split('_LLM_')[1] == llm_cq_id:
                        same_questions.append(
                            [arg_id, theory_cq_id, llm_cq_id, line['data']['premises'], line['data']['cq'], cq['body']])


    print(len(to_csv), len(out))
    print(to_csv)
    print(same_questions)

    # with open('LLMs_vs_theory/relation_and_validity/look_at_examples_2.csv', 'w') as o:
    #     w = csv.writer(o)
    #     w.writerow(['arg_id', 'llm_cq_id', 'premises', 'llm_cq'])
    #     w.writerows(to_csv)
    #
    # print(len(same_questions))
    #
    # with open('LLMs_vs_theory/relation_and_validity/check_same_questions_2.csv', 'w') as o:
    #     w = csv.writer(o)
    #     w.writerow(['arg_id', 'scheme', 'llm_cq_id', 'premises', 'thoery_cq', 'llm_cq'])
    #     w.writerows(same_questions)



if __name__ == "__main__":
        main()