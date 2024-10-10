import json
import csv
import sys

def main():
    dataset = sys.argv[1]

    with open('data/by_intervention/instantiated_' + dataset + '.json') as f:
        theory_data=json.load(f)

    pos_edited = []
    with open('data/annotated/postedition/' + dataset + '.csv') as f:
        r = csv.reader(f)
        for line in r:
            pos_edited.append(line)

    count_cqs = 0
    for key, intervention in theory_data.items():
        cqs = []
        for line in pos_edited:
            if key == line[0] and line[6] != 'wrong':
                cqs.append(line[5])

        if cqs:
            cqs = list(set(cqs))
            count_cqs += len(cqs)
            if 'went_to' in intervention['comment'].keys():
                theory_data[intervention['comment']['went_to']]['theory_cqs'].extend(cqs)
                intervention['theory_cqs'] = []
            else:
                intervention['theory_cqs'] = cqs
        else:
            intervention['theory_cqs'] = []

    print(count_cqs)
    with open('data/theory_cqs_by_intervention/' + dataset + '.json', 'w') as o:
        json.dump(theory_data, o, indent=5)


if __name__ == "__main__":
    main()
