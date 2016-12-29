# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA

# Converts the Tele data-sets into the same data structure as the insuranceQA data-set.
# Resulting pickles: train, test, answers, vocabulary


import pickle, random
import numpy as np

input_path = '/home/havikbot/PycharmProjects/data/'
output_path = '/home/havikbot/PycharmProjects/data/watson_tele_final/'

inputFilesTelenorFinal = ['tele_final/telenornorge_final.txt']
inputFilesTeliaFinal =['tele_final/telianorge_final.txt']

inputFilesALLFinal = ['tele_final/telenornorge_final.txt',
                          'tele_final/telianorge_final.txt',
                          'tele_final/chess.no_final.txt',
                          'tele_final/djuicenorge_final.txt']

s_strip_length = 150 #default were 50
s_exclude_lengths = [60, 120]
testing_split = 0.97




def load_data_and_generate_data():
    print('loading data')
    words_dict = dict()
    vocab_by_index = dict()
    questions1 = []
    data_set = []
    ans = []
    answer_dict = dict()

    for path in inputFilesTeliaFinal:
        print("  loading: ", path)
        file = open(input_path + "/" + path, "r")
        dataelemts = file.readlines()
        random.shuffle(dataelemts)
        for line in dataelemts:
            qa_pair = [line.strip().split(";")[1].strip(), line.strip().split(";")[2].strip()]
            if qa_pair[0] != None and qa_pair[1] != None and len(qa_pair[0]) > 4 and len(qa_pair[1]) > 4:
                if len(qa_pair[0].split(' ')) < s_exclude_lengths[0] and len(qa_pair[1].split(' ')) < s_exclude_lengths[1]:
                    for s in range(len(qa_pair)):
                        words = qa_pair[s].split(' ')
                        new_sentence = ''
                        for w in range(len(words)):
                            words_dict[words[w].strip()] = 1
                            if w < s_strip_length:
                                new_sentence = new_sentence + words[w] + ' '

                        qa_pair[s] = new_sentence.strip()
                    questions1.append(qa_pair[0])
                    ans.append(qa_pair[1])


    c = 1
    for key in words_dict:
        vocab_by_index[c] = key
        words_dict[key] = c
        c += 1

    for a in range(len(ans)):
        words = ans[a].split(' ')
        answer_word_list = []
        for word in words:
            answer_word_list.append(words_dict[word.strip()])
        answer_dict[a] = answer_word_list

        quest_words = questions1[a].split(' ')
        quest_words_list = []
        for word in quest_words:
            quest_words_list.append(words_dict[word.strip()])
        data_set.append({'question': quest_words_list, 'answers': [a]})

    train_list = data_set[:21000]
    test_list = data_set[21500 : 23500]
    test_list2 = []

    c = 0
    for qa in test_list:
        q = qa['question']
        a = qa['answers'][0]
        possibilities = list(range(21500 , 23500))
        possibilities.remove(a)
        negatives = np.random.choice(possibilities, 499)
        test_list2.append({'question': q, 'good': [a], 'bad': list(negatives)})
        c += 1
        if(c % 100 == 0) : print(c)

    print("training_size", len(train_list))
    print("testing_size", len(test_list))


    with open(output_path+'train', 'wb') as handle1:
        pickle.dump(train_list, handle1)
    with open(output_path + 'test', 'wb') as handle2:
        pickle.dump(test_list2, handle2)
    with open(output_path + 'vocabulary', 'wb') as handle3:
        pickle.dump(vocab_by_index, handle3)
    with open(output_path + 'answers', 'wb') as handle4:
        pickle.dump(answer_dict, handle4)


load_data_and_generate_data()
