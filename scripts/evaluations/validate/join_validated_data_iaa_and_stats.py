import csv
import json
from collections import Counter

def load_csv(path):
    with open(path) as f:
        r = csv.reader(f)
        out = []
        next(r)
        for line in r:
            out.append(line)
    return out

def load_4_datasets():
    not_matching = load_csv('data/validated/not_matching.csv')
    not_matching_RC = load_csv('data/validated/not_matching_RC.csv')
    matching = load_csv('data/validated/matching.csv')
    matching_RC = load_csv('data/validated/matching_RC.csv')
    return matching, matching_RC, not_matching, not_matching_RC

def substitute_theory_cqs_by_postedited_and_get_id():
    post_edition_US = load_csv('data/post_edition/US2016_manual_postedition.csv')
    post_edition_moral = load_csv('data/post_edition/moral_maze_schemes_manual_postedition.csv')
    post_edition = post_edition_US + post_edition_moral
    structured_args = []
    with open('data/finals/US2016.jsonl') as f:
        for line in f:
            structured_args.append(json.loads(line))
    with open('data/finals/moral_maze_schemes.jsonl') as f:
        for line in f:
            structured_args.append(json.loads(line))
    #print(len(structured_args)) # 370
    # crea la key 'postedited_cqs'
    for entry in structured_args:
        for argument in entry['FULL_ARGS']:
            argument['postedited_cqs'] = []

    for entry in structured_args: # por cada entrada estructurada
        for line in post_edition: # por cada pregunta posteditada
            if entry['id'] == line[0]: # si tiene el id de la entrada estructurada
                for argument in entry['FULL_ARGS']: # mira todos los argumentos que contiene
                    for cq in argument['cqs']: # por cada cq de cada argumento
                        if cq == line[3]: # si copincide con la no posteditada
                            argument['postedited_cqs'].append(line[4]) # todo: supongo que mas tarde edité algunas cqs y solo 73 coinciden

    # todo: keep just the fields that we need
    out_dataset = []
    #print(structured_args[59]['FULL_ARGS'][0].keys())
    count_no_potedits = 0
    count_discarded = 0
    for entry in structured_args:
        new_entry = {'id': entry['id'], 'intervention': entry['INTERVENTION'], 'args_original_ids': entry['ARGS'], 'arguments': {}}
        if not entry['FULL_ARGS']:
            out_dataset.append(new_entry)
        else:
            for i,arg in enumerate(entry['FULL_ARGS']):
                new_entry['arguments'][entry['id']+'_'+str(i)] = {'scheme': arg['scheme'], 'premises': arg['premises'],
                                             'cqs_raw': arg['read_cqs'], 'instantiated_cqs': arg['cqs'],
                                               'cqs_postedited': arg['postedited_cqs'], 'llm_cqs':[], 'discarded':None}
                if arg['comment'] == 'does not fit':
                    new_entry['arguments'][entry['id'] + '_' + str(i)]['discarded'] = 'yes'
                    count_discarded +=1
                count_no_potedits += 1
            out_dataset.append(new_entry)

    print('postedits missing', count_no_potedits) # todo: this should be 0, I probably changed theory_cqs after the postedition and now they dont match
    print('discarded args in first round', count_discarded)
    #print(len(out_dataset))
    return out_dataset





def main():

    with open('data/postedited/selection.jsonl') as f:
        original_data = []
        for line in f:
            original_data.append(json.loads(line))

    ids_selection = []
    for line in original_data:
        ids_selection.append(line['id'])

    matching, matching_RC, not_matching, not_matching_RC = load_4_datasets()

    # TODO: get the relation stats because the relation stats script is fucked up
    # do this by getting al the cqs ids and making them unique
    cq_associated_to_args_NO_cq = []
    cqs_associated_to_args_and_cq = []
    args_with_cqs = []
    for line in not_matching:
        args_with_cqs.append(line[0])
        cq_associated_to_args_NO_cq.append(line[2])
    for line in not_matching_RC:
        args_with_cqs.append(line[0])
        cq_associated_to_args_NO_cq.append(line[2]+'X')
    for line in matching:
        args_with_cqs.append(line[0])
        cqs_associated_to_args_and_cq.append(line[2])
    for line in matching_RC:
        args_with_cqs.append(line[0])
        cqs_associated_to_args_and_cq.append(line[2]+'X')
    print('\n\nRELATION STATS:')
    print(len(not_matching), len(not_matching_RC), len(matching), len(matching_RC), len(not_matching)+ len(not_matching_RC)+ len(matching)+ len(matching_RC))
    print('LLM-CQS associated to an Argument and NO theory-CQ', len(list(set(cq_associated_to_args_NO_cq))))
    print('LLM-CQS associated to an Argument and theory-CQ', len(list(set(cqs_associated_to_args_and_cq))))
    print('LLM-CQS with association', len(list(set(cqs_associated_to_args_and_cq+cq_associated_to_args_NO_cq))))
    #print('Args with at least 1 llm-cq', len(list(set(args_with_cqs)))) # this is not right

    # TODO: join the 2 not matching datasets and get the proportion of yes/no (remove wrongs)
    print('\n\nFINAL DATASET STATS:')
    validity_label = []
    type_label = []
    count_amount = 0

    for line in not_matching+not_matching_RC:
        validity_label.append(line[5])
        if line[5] != 'no':
            type_label.append(line[7])
            count_amount += 1

    print(Counter(validity_label))

    match = matching + matching_RC
    for line in match:
        type_label.append(line[7])
        count_amount += 1

    #print('type of llm cqs')
    #print(Counter(type_label))
    #print(count_amount)

    # TODO: output a iaa dataset for Jaione (do not repeat arguments or questions and include context)

    # iaa_sample = []
    # already_there = [[],[]]
    #
    # for line in not_matching:
    #     if line[0] not in already_there[0] and line[2] not in already_there[1] and line[9] != 'wrong':
    #         context = []
    #         for entry in original_data:
    #             if entry['id'] == '_'.join(line[2].split('_')[:-1]):
    #                 context = entry['INTERVENTION']
    #         if not context: # this should not happen
    #             print('_'.join(line[2].split('_')[:-1]))
    #
    #         iaa_sample.append([line[0], line[1], line[2], line[3], line[4], '', context])
    #         already_there[0].append(line[0])
    #         already_there[1].append(line[2])
    # print(len(iaa_sample))
    # with open('LLMs_vs_theory/relation_and_validity/iaa_inference.csv', 'w') as o:
    #     w = csv.writer(o)
    #     w.writerows(iaa_sample)

    # iaa = load_csv('LLMs_vs_theory/relation_and_validity/validated_data/iaa_inference - iaa_inference(1).csv')
    # iaa_labels = []
    # reference_labels = []
    # same = 0
    # not_same = 0
    # for line in iaa:
    #     for reference in not_matching:
    #         if line[0] == reference[0] and line[2] == reference[2]:
    #             if reference[5]:
    #                 iaa_labels.append(line[5])
    #                 reference_labels.append(reference[5])
    #                 if line[5] == reference[5]:
    #                     same += 1
    #                 else:
    #                     #print(line[3])
    #                     #print(line[4], line[5], reference[5])
    #                     not_same += 1
    #
    # print(same/len(iaa_labels), not_same)
    # print(len(iaa_labels))
    # print(reference_labels)


    # TODO: I am missing the type stats for theory-CQs with no matching LLM-CQ,
    #  this can easily be calculated SUM(n_argument_scheme_X*num_theory_cqs_type_Y_in_X)



    # TODO: BUILD FINAL DATASET
    # todo: get just our interventions
    all_entries_dataset = substitute_theory_cqs_by_postedited_and_get_id()
    our_entries_dataset = []
    for line in all_entries_dataset:
        if line['id'] in ids_selection:
            our_entries_dataset.append(line)

    # TODO: join both 4 datasets keeping only the yes questions,

    #exceptions = ['CLINTON_244_1', 'TRUMP_129_2', 'CLINTON_1_1', 'TRUMP_240_1', 'TRUMP_174_1'] # these are the intervention ids with 3 elements

    for entry in our_entries_dataset:
        for line in not_matching+not_matching_RC: # we are only adding the arguments that had a matching LLM-CQ, what about the rest???
            intervention_id = line[0][:-2] #todo: these works as long as we don't have more than 10 arguments in an intervention
            #if line[0][:-2] in exceptions: # aquí l'he liat posant ids de intervention de 2 i de 3 caracters
            #    intervention_id = '_'.join(line[0].split('_')[:3])
            #else:
            #    intervention_id = '_'.join(line[0].split('_')[:2])

            if intervention_id == entry['id'] and line[5] == 'yes':
                argument_id = line[0]
                question_id = 'Q_'+line[2]
                llm_cq = {'id': question_id, 'cq': line[4], 'type': line[7], 'matching_to':''} # todo: ids from questions should be the original ones, cq ids are bulshit
                if argument_id not in entry['arguments'].keys(): #arguments_already_there:
                    print(argument_id) # this should not happen
                    #entry['arguments'][argument_id] = {'scheme': line[1], 'premises':line[3], 'llm_cqs':[llm_cq]}
                else:
                    entry['arguments'][argument_id]['llm_cqs'].append(llm_cq)

        for line in match:
            intervention_id = line[0][:-2]
            # if line[0][:-2] in exceptions: # aquí l'he liat posant ids de intervention de 2 i de 3 caracters
            #     intervention_id = '_'.join(line[0].split('_')[:3])
            # else:
            #     intervention_id = '_'.join(line[0].split('_')[:2])

            if intervention_id == entry['id']:
                argument_id =  line[0]
                question_id = 'Q_M_' + line[2] # todo: ids from llm questions should be the original ones, which show the origin, cq ids are bulshit
                llm_cq = {'id': question_id, 'cq': line[5], 'type': line[7], 'matching_to': line[4]}
                if argument_id not in entry['arguments'].keys():
                    #print(argument_id) # this should be none
                    pass
                else:
                    entry['arguments'][argument_id]['llm_cqs'].append(llm_cq)

    # todo: get stats of the whole dataset

    theory_cq_types = load_csv('LLMs_vs_theory/relation_and_validity/validated_data/theory_cqs_types.csv')

    count_theory_types = []
    all_args_theory = []
    count_args_with_llms = 0
    count_llm_cqs = 0
    count_theory_cqs = 0
    count_postedit_cqs = 0
    count_instantiated = 0
    count_llm_types = []
    average_llm_cqs_per_argument = []
    theory_to_llm_matches = 0
    theory_matched_cqs = []
    discarded_args_2_round = ['TRUMP_15_0', 'CLINTON_36_2', 'TRUMP_240_1_2', 'CF_62_0', # stupid arguments
                              'CLINTON_136_3']  # repeated argument
    count_unique_cqs_per_intervention = []
    count_unique_llm_cqs = []
    count_matching_cqs_types = []
    for line in our_entries_dataset:  # in the 21 interventions
        all_cqs = []
        for key, arg in line['arguments'].items():  # go to every argument

            #if arg['discarded'] == 'yes':
            #    print(arg)
            if key in discarded_args_2_round:
                arg['discarded'] = 'yes'
            if not arg['premises']:
                arg['discarded'] = 'yes'

            if not arg['discarded']:
                all_args_theory.append(key)
                for theory_cq in arg['cqs_raw']:
                    count_theory_cqs += 1
                    for type in theory_cq_types:
                        if theory_cq == type[2]:
                            count_theory_types.append(type[3])
                all_cqs.extend(arg['cqs_raw'])

                for llm_cq in arg['llm_cqs']:
                    count_llm_types.append(llm_cq['type'])
                    count_unique_llm_cqs.append(llm_cq['cq'])
                    if llm_cq['matching_to']:
                        theory_to_llm_matches+=1
                        theory_matched_cqs.extend(llm_cq['matching_to'])
                        count_matching_cqs_types.append(llm_cq['type'])
                    all_cqs.append(llm_cq['cq'])

                average_llm_cqs_per_argument.append(len(arg['llm_cqs']))

                if len(arg['llm_cqs']) > 0:
                    count_args_with_llms += 1
                #elif not arg['discarded'] and len(arg['llm_cqs']) == 0:
                #    print(key, arg['premises'])
            #else:
            #    print(key, arg['premises'])

                count_postedit_cqs += len(arg['cqs_postedited'])
                count_instantiated += len(arg['instantiated_cqs'])
        count_unique_cqs_per_intervention.append(len(list(set(all_cqs))))

    print('all unique cqs per intervention',sum(count_unique_cqs_per_intervention)/len(count_unique_cqs_per_intervention), len(count_unique_cqs_per_intervention))
    print('llm cqs total', len(count_unique_llm_cqs))
    print('unique valid llm cqs in the end', len(list(set(count_unique_llm_cqs))))



    print('total llm cqs', sum(average_llm_cqs_per_argument), 'average num of llm cqs per argument', sum(average_llm_cqs_per_argument)/len(list(set(all_args_theory))))
    print('total theory cqs', count_theory_cqs)
    print('total instantiated cqs', count_instantiated)
    print('total postedited cqs', count_postedit_cqs)
    print('types of theory cqs')
    print(Counter(count_theory_types))
    for type, num in Counter(count_theory_types).items():
        print(type, '&', num,'&', round(num/count_theory_cqs*100, 2), '& ')
    #print('types of llm cqs')
    for type, num in Counter(count_llm_types).items():
        print(type,'&', num,'&', round(num/sum(average_llm_cqs_per_argument)*100, 2), '\\\\')
    print('matching cqs')
    for type, num in Counter(count_matching_cqs_types).items():
        #print(type, num)
        print(type,'&', num)#,'&', round(num/sum(average_llm_cqs_per_argument)*100, 2), '\\\\')
    #print(all_args_theory)
    print('total args', len(list(set(all_args_theory))))
    print('total args with llm', count_args_with_llms)
    print('llm to theory matches', theory_to_llm_matches)
    print('theory to llm matches', len(list(set(theory_matched_cqs))))


    for line in our_entries_dataset:
        if line['id'] == 'MT_45':
            print(line['arguments']['MT_45_0']['instantiated_cqs'])
            print(line['arguments']['MT_45_1']['instantiated_cqs'])
            intervention_printed = line['intervention'].split('\n')
            for sentence in intervention_printed:
                print(sentence+'. ')
            for key, arg in line['arguments'].items():
                #print(arg)
                for cq in arg['instantiated_cqs']:
                    print(' & '+cq+' \\\\')
                for cq in arg['llm_cqs']:
                    print(' & '+cq['cq']+' \\\\')

    # todo: given that I forgot to keep an id in the arguments, now I can't match them, premises have changed, I should match them manually


    # todo: load the postedition csvs and match the theory CQs to its postedited versions (in another function)
    # now we have a dataset with raw, instantiated, and postedited
    # cqs_raw = 0
    # cqs_instantiated = 0
    # cqs_postedited = 0
    # for line in our_entries_dataset:
    #     for arg in line['arguments']:
    #         cqs_raw += len(arg['cqs_raw'])
    #         cqs_instantiated += len(arg['instantiated_cqs'])
    #         cqs_postedited += len(arg['cqs_postedited'])
    #
    # print(cqs_raw, cqs_instantiated, cqs_postedited)




if __name__ == "__main__":
    main()
