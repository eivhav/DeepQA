# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA

main_file_path = '/home/havikbot/Downloads/'

voca_filepath = main_file_path + "vocabulary.txt"
q_train_path = main_file_path + 'InsuranceQA.question.anslabel.token.1500.pool.solr.train.encoded.txt'
q_valid_path = main_file_path + 'InsuranceQA.question.anslabel.token.1500.pool.solr.valid.encoded.txt'
answers_path = main_file_path + 'InsuranceQA.label2answer.token.encoded.txt'


def getPermutations(word):
    word = '{' + word.strip() +'}'
    permutations = []
    for i in range(len(word)-2):
        conc = word[i].lower() + word[i+1].lower() + word[i+2].lower()
        permutations.append(conc)

    return permutations


voca_file= open(voca_filepath).readlines()
trigrams = dict()
vocabulary = dict()
vocabulary_real = dict()
index = 0

for line in voca_file:
    perms = getPermutations(line.split('\t')[-1])
    for p in perms:
        if not p in trigrams:
            trigrams[p] = index
            index += 1

    indexes = []
    for p in perms:
        indexes.append(trigrams[p])

    word_id = int(line.split('\t')[0].strip().split("_")[-1])
    vocabulary[word_id] = indexes
    vocabulary_real[word_id] = line.split('\t')[-1]


questions_lines = open(q_train_path).readlines()
# questions_lines = open(q_valid_path).readlines()
answers_lines= open(answers_path).readlines()

answers = dict()
longestReply = 0

for line in answers_lines:
    words = line.split("\t")[1].replace("idx_", "").split(" ")
    if len(words) > longestReply:
        longestReply = len(words)
    ans = ""
    for num in words:
          ans = ans + " " + vocabulary_real[int(num.strip())].strip()

    answers[int(line.split("\t")[0].strip())] = [ans, 0]


def preprocess_text(text):
    t = text.lower().replace('{' , '').replace('[' , '').replace('}' , '').replace(']', '').replace('_', '').replace("'", '')
    t = t.replace('``', '').replace('-', ' ').replace('@', '').replace('/', '').replace(':', '').replace('=', '').replace('+', '')
    t = t.replace('(', '').replace(')', '').replace(';', '').replace('`', '').replace('~', '')
    return t.replace('   ', ' ').replace('  ', ' ')


qa_lines = []
avg_lengths = [0, 0]
for line in questions_lines:
    elements = line.split("\t")
    question = ""
    words = elements[1].replace("idx_", "").split(" ")
    for num in words:
          question = question + " " + vocabulary_real[int(num.strip())].strip()

    poss_ans = elements[2].strip()
    ans = ""

    if len(poss_ans.split(" ")) > 0 :
        for pa in poss_ans.split(" "):
            ans = ans + answers[int(pa.strip())][0] + "\n" + "  -"
            answers[int(pa.strip())][1] += 1
            qa_lines.append('00-00;' + preprocess_text(question.strip()) + ';' + preprocess_text(answers[int(pa.strip())][0].strip()) + ';no_name')
            avg_lengths[0] += len(qa_lines[-1].split(';')[1].split(' '))
            avg_lengths[1] += len(qa_lines[-1].split(';')[2].split(' '))
    else:
        ans = answers[int(elements[2].strip())][0]
        answers[int(pa.strip())][1] += 1

print(avg_lengths[0] / len(qa_lines), avg_lengths[1] / len(qa_lines))

c = 0
data_type = 'train'
file = open(main_file_path+'InsQA_' + data_type + '_preped_v1.txt', 'w+')
for line in qa_lines:
    file.write(line + '\n')
    c += 1
file.close()
print("wrote", c, "lines to file")


twos = 0
trees = 0
fours = 0

for ans in answers.items():
    if(ans[1][1] == 2):
        twos += 1
    elif(ans[1][1] == 3):
        trees += 1
    elif(ans[1][1] > 3):
        fours += 1

print("longestReply", longestReply)
print("#questions", len(questions_lines))
print("#answers  ", len(answers_lines))
print("   twos", twos)
print("   trees", trees)
print("   fours", fours)

