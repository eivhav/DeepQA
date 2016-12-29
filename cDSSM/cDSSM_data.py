# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA

import os, pickle

class cDSSM_dataClass:

    inputPathHome = '/home/havikbot/PycharmProjects/data/'
    inputPathSamuel = '/home/shomea/h/havikbot/PycharmProjects/data/'
    inputPath = inputPathHome
    inputFilesInsQAv1 = ['insurance_qa_python/InsQA_train_preped_v1.txt',  #19384 @ ans_max 200
                         'insurance_qa_python/InsQA_valid_preped_v1.txt' ]  # 3029 @ ans_max 200

    alphaBet = ['|','a', 'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'E', 'O', 'A']
    numbers = ['|','0','1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['|','.', ',', ':', '!', '@', '%', '&','/', '(' ,')', '=' , '?', '+' , '-', '"' ]

    q_maxLength = 75       #default were 50
    answ_maxLength = 200     #default were 100
    nb_posts_edited = 0

    new_max_length = 80

    tri_letters = dict()
    used_tri_letters = dict()
    used_count = 0

    data = [ [ [  [] ] ] ]
    all_words = dict()

    qa_pairs_text = []

    def build_tri_letters(self):
        pos = 0
        for a in self.alphaBet:
            for b in self.alphaBet[1:]:
                for c in self.alphaBet:
                    tri_letter = a+b+c
                    self.tri_letters[tri_letter] = pos
                    pos += 1

        for n1 in self.numbers:
            for n2 in self.numbers[1:]:
                for n3 in self.numbers:
                    tri_letter = n1+n2+n3
                    self.tri_letters[tri_letter] = pos
                    pos += 1

        for s1 in self.symbols:
            for s2 in self.symbols[1:]:
                for s3 in self.symbols:
                    tri_letter = s1+s2+s3
                    self.tri_letters[tri_letter] = pos
                    pos += 1

    def build_tri_letters_all(self):
        all_symbols = self.alphaBet + self.numbers[1:] + self.symbols[1:3] + self.symbols[4:5] + self.symbols[6:8] + self.symbols[12:13] +\
                      ['$', '#', '*', '>', '<']
        print(all_symbols)
        pos = 0
        for a in all_symbols:
            for b in all_symbols[1:]:
                for c in all_symbols:
                    tri_letter = a+b+c
                    self.tri_letters[tri_letter] = pos
                    pos += 1

    def get_vector_rep(self, line, limit):
        words = line.strip().split(' ')
        vectors = []
        nb_ellible_words = 0

        for w in words:
            word_vector = []
            elligble_word = True
            w = w.replace(' ', '')
            if w.strip() not in self.all_words: self.all_words[w.strip()] = [None, 0]
            self.all_words[w.strip()][1] += 1

            new_word = '|'+w.strip()+'|'
            for i in range(len(new_word)-2):
                perm = new_word[i].strip() + new_word[i+1].strip() + new_word[i+2].strip()
                if perm in self.tri_letters:
                    if perm not in self.used_tri_letters :
                        self.used_tri_letters[perm] = [len(self.used_tri_letters), 0]

                    self.used_tri_letters[perm][1] += 1
                    word_vector.append(self.used_tri_letters[perm][0])
                else:
                    elligble_word = False
                    nb_ellible_words += 1
                    break

            if elligble_word :
                 vectors.append(word_vector)

        if nb_ellible_words > 4 :
            return None

        if len(words) >= limit or len(vectors) >= limit:
            return None

        return vectors


    def get_summary(self, d, name):
        stats = [0]*20
        for key in d:
            count = d[key][1]
            if count > 20:
                stats[19] += 1
            else:
                stats[count-1] += 1

        print("For", name, stats)


    def remove_onetime_words(self, line):
        out = ""
        words = line.strip().split(" ")
        for w in words:
            if w in self.all_words and self.all_words[w][1] > 1:
                out = out + w.strip() + " "
            else:
                out = out + 'rmx' + " "
        return out


    def write_onetime_to_file(self, QA_strings):
        file = open(self.inputPath + 'all_onewords_removed.txt', 'w+')
        print(self.inputPath + 'all_onewords_removed.txt')
        q_list = self.shuffle_list(QA_strings)
        for qa_pair in q_list:
            if(len(qa_pair) == 4):
                file.write(qa_pair[0].strip()+";"+self.remove_onetime_words(qa_pair[1].strip())+";"+self.remove_onetime_words(qa_pair[2].strip())+";"+qa_pair[3].strip()+"\n")
        print("file written")
        file.close()


    def load_data(self, in_files, dataset_tag):
        print('loading data')

        QA_pairs = []
        total = 0

        if os.path.isfile(self.inputPath + in_files[0] +'qapairs_'+dataset_tag+'.pickle') is True:
            QA_pairs = pickle.load(open(self.inputPath + in_files[0] +'qapairs_'+dataset_tag+'.pickle', 'rb'))
            self.used_tri_letters = pickle.load(open(self.inputPath + in_files[0] + 'used_tri_letters'+dataset_tag+'.pickle', 'rb'))
            self.all_words = pickle.load(open(self.inputPath + in_files[0] + 'all_words'+dataset_tag+'.pickle', 'rb'))
            self.qa_pairs_text = pickle.load(open(self.inputPath + in_files[0] + 'all_text_lines'+dataset_tag+'.pickle', 'rb'))
            print("loaded pickles for ", self.inputPath + dataset_tag)
        else:
            for path in in_files:
                print("  loading: ", path)
                file = open(self.inputPath + path, "r")
                dataelemts = file.readlines()
                total += len(dataelemts)
                for line in dataelemts:
                    # time = line.strip().split(";")[0]
                    question = line.strip().split(";")[1]
                    answer = line.strip().split(";")[2]
                    # owner = line.strip().split(";")[3]
                    # QA_strings.append([time, question, answer, owner])

                    qa_pair = [self.get_vector_rep(question, self.q_maxLength),
                               self.get_vector_rep(answer, self.answ_maxLength)]
                    if (qa_pair[0] != None and qa_pair[1] != None and len(qa_pair[0]) > 3 and len(qa_pair[1]) > 4):
                        QA_pairs.append(qa_pair)
                        self.qa_pairs_text.append([question, answer])

                file.close()

            pickle.dump(QA_pairs, open(self.inputPath + in_files[0] +'qapairs_'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.used_tri_letters, open(self.inputPath + in_files[0] + 'used_tri_letters'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.all_words, open(self.inputPath + in_files[0] + 'all_words'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.qa_pairs_text, open(self.inputPath+ in_files[0] + 'all_text_lines' + dataset_tag + '.pickle', 'wb'))

        print("Dataset_stats :" "Total: " + str(total) + "  to long: " + str(total - len(QA_pairs)) + "  remaining: "+ str(len(QA_pairs)))
        print("numb trigrams used:" + str(len(self.used_tri_letters)) , "in used dict: " + str(len(self.used_tri_letters)))
        self.get_summary(self.used_tri_letters, "used tri letters")
        self.get_summary(self.all_words, "all words")

        for qa in QA_pairs:
            for i in range(len(qa)):
                if len(qa[i]) > self.new_max_length:
                    qa[i] = qa[i][0:self.new_max_length]

        import random
        #random.shuffle(QA_pairs)
        self.data = QA_pairs


    def __init__(self):
        self.build_tri_letters()
        self.load_data(self.inputFilesInsQAv1, 'InsQAv1')
        #self.make_ascii()



