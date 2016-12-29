# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA

import numpy as np

def get_MRR(sim_matrix):
    mmr_score = 0
    percent = 500 / float(sim_matrix.shape[0])
    for i in range(sim_matrix.shape[0]):
        mask = np.random.choice([False, True], sim_matrix[0].shape[0]-1, p=[1-percent, percent])
        query_sim = sim_matrix[i][i]
        arr = np.delete(np.array(sim_matrix[i]), i, 0)[mask]
        mmr_score += 1.0 / (len(np.where(arr > query_sim)[0]) + 1)

    return mmr_score / sim_matrix.shape[0]


def get_top_at_score(sim_matrix, selelction_size):
    top_score = 0
    percent = 500 / float(sim_matrix.shape[0])
    for i in range(sim_matrix.shape[0]):
        mask = np.random.choice([False, True], sim_matrix[0].shape[0]-1, p=[1-percent, percent])
        query_sim = sim_matrix[i][i]
        arr = np.delete(np.array(sim_matrix[i]), i, 0)[mask]
        if (arr.shape[0] - len(np.where(arr < query_sim)[0])) < selelction_size:
            top_score += 1.0

    return top_score / float(sim_matrix.shape[0])


def print_max(qa_pairs_strings, sim_matrix, nb_samples):
    possibilities = list(range(sim_matrix.shape[0]))
    samples = np.random.choice(possibilities, nb_samples)
    for s in samples:
        query = qa_pairs_strings[s][0]
        #top3_indexes = np.copy(sim_matrix[s]).argsort()[-3:][::-1]
        top_ans = qa_pairs_strings[np.argmax(sim_matrix[s])][1]
        true_ans = qa_pairs_strings[s][1]
        print('Question:', query)
        #for i in range(3): print(i+1, qa_pairs_strings[top3_indexes[i]][1])
        print('answer', top_ans)
        print('True_ans:', true_ans)
        print(sim_matrix[s][s], sim_matrix[s][np.argmax(sim_matrix[s])])
        print()


def get_ranking_distribution(sim_matrix, percent):
    rank_dist = [0] * 100
    for i in range(sim_matrix.shape[0]):
        mask = np.random.choice([False, True], sim_matrix[0].shape[0]-1, p=[1-percent, percent])
        query_sim = sim_matrix[i][i]
        arr = np.delete(np.array(sim_matrix[i]), i, 0)[mask]
        rank_dist[int(100*len(np.where(arr < query_sim)[0]) / (percent*sim_matrix.shape[0]))] += 1
        # Does not make any sence

    return rank_dist



def evaulate(qa_pairs, qa_pairs_text, sim_matrix, methods):
    print("Evaluating data", "len:", len(qa_pairs))

    for m in methods:
        if m[0] == 'MMR':
            print(" Calculating MMR for", "500", "of data")
            print(" ", get_MRR(sim_matrix), '\n')
        elif m[0] == 'Top':
            print(" Calculating  Top @", m[1])
            print(" ", get_top_at_score(sim_matrix, int(m[1])), '\n')
        elif m[0] == 'Print_ans':
            print(" Printing answers. #", m[1])
            print_max(qa_pairs_text, sim_matrix, int(m[1]))
        elif m[0] == 'MMR_dist':
            print(" Calculating MMR rank dist for", m[1], "of data")
            rank_dist = get_ranking_distribution(sim_matrix, 1.0)
            for r in rank_dist:
                print(r)
            print("done")


