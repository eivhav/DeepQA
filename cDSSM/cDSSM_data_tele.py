# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA


import os, pickle

class cDSSM_dataClass:

    inputPathHome = '/home/havikbot/PycharmProjects/data/'
    inputPathSamuel = '/home/shomea/h/havikbot/PycharmProjects/data/'
    inputPath = inputPathHome

    inputFilesTelenorRaw = ['tele_final/telenornorge_final_raw.txt']
    inputFilesTelenorFinal = ['tele_final/telenornorge_final.txt']
    inputFilesTeliaFinal =['tele_final/telianorge_final.txt']

    inputFilesALLFinal = ['tele_final/telenornorge_final.txt',
                          'tele_final/telianorge_final.txt',
                          'tele_final/chess.no_final.txt',
                          'tele_final/djuicenorge_final.txt']


    alphaBet = ['|','a', 'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'E', 'O', 'A']
    numbers = ['|','0','1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['|','.', ',', ':', '!', '@', '%', '&','/', '(' ,')', '=' , '?', '+' , '-', '"' ]

    q_maxLength = 60       #default were 50
    answ_maxLength = 120    #default were 100
    nb_posts_edited = 0

    new_max_length = 120

    tri_letters = dict()
    avail_tri_letter = dict()
    used_tri_letters = dict()
    used_count = 0

    data = []
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



    def limit_tri_letters(self, dataelemnts):
        for line in dataelemnts:
            if len(line) > 3 :
                qa = line.strip().split(";")[1] + line.strip().split(";")[2]
                for w in qa.strip().split(' '):
                    new_word = '|'+w.strip()+'|'
                    for i in range(len(new_word)-2):
                        perm = new_word[i].strip() + new_word[i+1].strip() + new_word[i+2].strip()
                        if perm not in self.avail_tri_letter: self.avail_tri_letter[perm] = 0

                        self.avail_tri_letter[perm] += 1

        keys = list(self.avail_tri_letter.keys())
        for i in range(len(keys)):
            if self.avail_tri_letter[keys[i]] == 1:
                self.avail_tri_letter.pop(keys[i])



    def get_vector_rep(self, line, limit):
        words = line.strip().split(' ')
        vectors = []
        nb_ellible_words = 0

        for w in words:
            word_vector = []
            elligbleWord = True
            w = w.replace(' ', '')
            if w.strip() not in self.all_words: self.all_words[w.strip()] = [None, 0]
            self.all_words[w.strip()][1] += 1

            new_word = '|'+w.strip()+'|'
            for i in range(len(new_word)-2):
                perm = new_word[i].strip() + new_word[i+1].strip() + new_word[i+2].strip()
                if perm in self.tri_letters:
                    if len(self.avail_tri_letter) > 1 and perm in self.avail_tri_letter:
                        if perm not in self.used_tri_letters:
                            self.used_tri_letters[perm] = [len(self.used_tri_letters), 0]

                        self.used_tri_letters[perm][1] += 1
                        word_vector.append(self.used_tri_letters[perm][0])
                        #word_vector.append(self.tri_letters[perm])

                else:
                    elligbleWord = False
                    #print(perm)
                    nb_ellible_words += 1
                    break

            if(elligbleWord):
                 vectors.append(word_vector)

        if(nb_ellible_words > 4):
            return None

        if (len(words) >= limit or len(vectors) >= limit):
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

    def load_data(self, in_files, dataset_tag):
        print('loading data')

        QA_pairs = []
        total = 0

        if os.path.isfile(self.inputPath + 'cDSSM_pickles/'+'qapairs_'+dataset_tag+'.pickle') is True:
            QA_pairs = pickle.load(open(self.inputPath  +'cDSSM_pickles/'+'qapairs_'+dataset_tag+'.pickle', 'rb'))
            self.used_tri_letters = pickle.load(open(self.inputPath  +'cDSSM_pickles/'+ 'used_tri_letters'+dataset_tag+'.pickle', 'rb'))
            self.all_words = pickle.load(open(self.inputPath  + 'cDSSM_pickles/'+'all_words'+dataset_tag+'.pickle', 'rb'))
            self.qa_pairs_text = pickle.load(open(self.inputPath  +'cDSSM_pickles/'+ 'all_text_lines'+dataset_tag+'.pickle', 'rb'))
            print("loaded pickles for ", self.inputPath + dataset_tag)
        else:
            for path in in_files:
                print("  loading: ", path)
                file = open(self.inputPath + path, "r")
                dataelemts = file.readlines()
                self.limit_tri_letters(dataelemts)
                total += len(dataelemts)
                for line in dataelemts:
                    if(len(line) > 3):
                        # time = line.strip().split(";")[0]
                        question = line.strip().split(";")[1]
                        answer = line.strip().split(";")[2]
                        # owner = line.strip().split(";")[3]
                        # QA_strings.append([time, question, answer, owner])
                        qa_pair = [self.get_vector_rep(question, self.q_maxLength),
                                   self.get_vector_rep(answer, self.answ_maxLength)]
                        if (qa_pair[0] != None and qa_pair[1] != None and len(qa_pair[0]) > 3 and len(qa_pair[1]) > 4):
                            QA_pairs.append([qa_pair, [question, answer]])

                file.close()

            import random
            random.shuffle(QA_pairs)
            pickle.dump(QA_pairs, open(self.inputPath + 'cDSSM_pickles/'+'qapairs_'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.used_tri_letters, open(self.inputPath  + 'cDSSM_pickles/'+'used_tri_letters'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.all_words, open(self.inputPath  + 'cDSSM_pickles/'+'all_words'+dataset_tag+'.pickle', 'wb'))
            pickle.dump(self.qa_pairs_text, open(self.inputPath + 'cDSSM_pickles/'+'all_text_lines' + dataset_tag + '.pickle', 'wb'))


        print("Dataset_stats :" "Total: " + str(total) + "  to long: " + str(total - len(QA_pairs)) + "  remaining: "+ str(len(QA_pairs)))
        print("numb trigrams used:" + str(len(self.used_tri_letters)) , "in used dict: " + str(len(self.used_tri_letters)))
        self.get_summary(self.used_tri_letters, "used tri letters")
        self.get_summary(self.all_words, "all words")
        print("#words", len(self.all_words))

        """
        for qa in QA_pairs:
            for i in range(len(qa)):
                if len(qa[i]) > self.new_max_length:
                    qa[i] = qa[i][0:self.new_max_length]

        """

        for p in QA_pairs:
            self.data.append(p[0])
            self.qa_pairs_text.append(p[1])


    def __init__(self):
        self.build_tri_letters_all()
        self.load_data(self.inputFilesALLFinal, 'inputFilesALLFinal')



