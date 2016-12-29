# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA

import csv
import re

tri_letters = dict()
alphabet = ['|','a', 'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','E','O','A']
numbers = ['|','0','1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['|','.', ',', ':', '!', '@', '%', '&','/', '(' ,')', '=' , '?', '+' , '-', '"' ]
sep_symbols = ['.', ',', '!', '=', '?', ':', '+']
non_sep_symbols = ['@', '%', '&','/', '(' ,')', '-', '"']
illegal_symbols = ['~', '|', ';', '`', '*', '^', '<', '>']

#replacements:
# {, [ = (
# ], } = )
# \ = /
# _ = -
# ' = "
# ; = :


def build_tri_letters():
    pos = 0
    for a in alphaBet:
        for b in alphaBet[1:]:
            for c in alphaBet:
                tri_letter = a+b+c
                tri_letters[tri_letter] = pos
                pos += 1
                print(tri_letter, tri_letters[tri_letter])

    for n1 in numbers:
        for n2 in numbers[1:]:
            for n3 in numbers:
                tri_letter = n1+n2+n3
                tri_letters[tri_letter] = pos
                pos += 1
                print(tri_letter, tri_letters[tri_letter])

    for s1 in symbols:
        for s2 in symbols[1:]:
            for s3 in symbols:
                tri_letter = s1+s2+s3
                tri_letters[tri_letter] = pos
                pos += 1
                print(tri_letter, tri_letters[tri_letter])
#delimiter=' '

def readFile(filePath, companyID, postFix):
    posts = [[]]
    file = open(filePath+'/'+companyID+postFix)
    lines = file.readlines()
    for line in lines:
        if(len(line) > 2):
            content = line.strip().split(";")
            posts.append(content)

    print(companyID, len(posts))

    return posts

def remove_emojis(line):

    myre = re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+',
    re.UNICODE)

    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

    return myre.sub('', line)

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)


def sperate_words(line):
    newLine = line.lower().replace('{' , '(').replace('[' , '(').replace('}' , ')').replace(']' , ')').replace('_', '-').replace("'", '"')

    for i in range(len(alphaBet)):
        for j in range(len(symbols)):
            sub = alphaBet[i] + symbols[j]
            newLine = newLine.replace(sub, alphabet[i] +" " +symbols[j])
            sub2 = symbols[j] +alphabet[i]
            newLine = newLine.replace(sub2, symbols[j] + " " + alphaBet[i])
        for j in range(len(numbers)):
            sub = alphaBet[i] +  numbers[j]
            newLine = newLine.replace(sub, alphabet[i] +" " +numbers[j])
            sub2 = numbers[j] +alphabet[i]
            newLine = newLine.replace(sub2, numbers[j] + " " + alphaBet[i])

    for i in range(len(numbers)):
        for j in range(len(symbols)):
            sub = numbers[i] + symbols[j]
            newLine = newLine.replace(sub, numbers[i] +" " +symbols[j])
            sub2 = symbols[j] +numbers[i]
            newLine = newLine.replace(sub2, symbols[j] + " " + numbers[i])


    newLine = remove_emojis(newLine)

    return newLine


def seperate_words_2(line):
    newLine = removeNonAscii(line)
    newLine = remove_emojis(newLine)
    newLine = newLine.replace('{' , '(').replace('[' , '(').replace('}' , ')').replace(']' , ')').replace('_', '-').replace("'", '"')
    for ill in illegal_symbols:
        newLine.replace(ill, ' ')

    alpha_numbers = alphabet + numbers
    for i in range(len(alpha_numbers)):
        for j in range(len(sep_symbols)):
            sub = alpha_numbers[i] + sep_symbols[j]
            newLine = newLine.replace(sub, alpha_numbers[i] +" " +sep_symbols[j])
            sub2 = sep_symbols[j] + alpha_numbers[i]
            newLine = newLine.replace(sub2, sep_symbols[j] + " " + alpha_numbers[i])

        for j in range(len(non_sep_symbols)):
            sub = alpha_numbers[i] + non_sep_symbols[j]
            newLine = newLine.replace(sub, alpha_numbers[i] + " ")
            sub2 = non_sep_symbols[j] +alpha_numbers[i]
            newLine = newLine.replace(sub2, " "+alpha_numbers[i])

    newLine = newLine.replace("   ", " ")
    newLine = newLine.replace("  ", " ")
    newLine = newLine.replace("  ", " ")
    newLine = newLine.replace("  ", " ")
    return newLine




def removeCompanyName(msg, companyNames):

    newMsg = ""+msg
    for cNames in companyNames:
        newMsg = newMsg.replace(cNames.lower(), "companyx")

    return newMsg



def removePrivateName(msg, privateName):
    newMesg1 = msg[0:30]
    newMesg2 = msg[30:]
    names = privateName.strip().split(" ")
    c = 0
    for i in range(len(names)):
        if(len(names[i]) > 1):
            if i == 0:
                newMesg1 = newMesg1.replace(names[i].lower(), 'fname')
            elif(i == (len(names)-1)):
                    newMesg1 = newMesg1.replace(names[i].lower(), 'lname')
            else:
                newMesg1 = newMesg1.replace(names[i].lower(), 'mname')

    return newMesg1+newMesg2

def remove_web_links(sen):
    return_sentence = ""
    sentence = sen.replace("http", " http").replace("  ", " ")
    for s in sentence.split(" "):
        if s.lower().strip()[0:4] == 'http':
            return_sentence += 'weblink' + ' '
        else:
            return_sentence += s.strip() + ' '

    return return_sentence




def preProcessPosts(posts, companyNames):

    output = []
    for i in range(len(posts)):
        if(len(posts[i]) > 3):
            post_msg = remove_web_links(posts[i][1].lower()).replace("æ", "E").replace("ø", "O").replace("å", "A")
            post_reply = remove_web_links(posts[i][2].lower()).replace("æ", "E").replace("ø", "O").replace("å", "A")
            msg2 = removeCompanyName(seperate_words_2(post_msg), companyNames)
            reply2 = removeCompanyName(removePrivateName(seperate_words_2(post_reply), posts[i][3]), companyNames)
            line = posts[i][0] +";" + msg2 +";"+ reply2 + ";" + posts[i][3]
            if len(output) == 0:
                output.append(line)

            elif line != output[-1]:
                output.append(line)

        else:
            print(posts[i])

        if i % 1000 == 0:
            print(i)

    return output


def remove_numb_times(pairs, nb_times):
    word_count = dict()
    r_list = []
    for sentences in pairs:
        pair = [sentences.split(';')[1].split(" "), sentences.split(';')[2].split(" ")]
        for i in range(2):
            for w in pair[i]:
                if w not in word_count:
                    word_count[w] = 0
                word_count[w] += 1

    for sentences in pairs:
        pair = [sentences.split(';')[1].split(" "), sentences.split(';')[2].split(" ")]
        r_pair = ["",""]
        for i in range(2):
            for w in pair[i]:
                if word_count[w] > nb_times:
                    r_pair[i] += w + " "
                else:
                    r_pair[i] += 'rmx' + " "
        r_list.append(sentences.split(';')[0] +';'+ r_pair[0] +';'+ r_pair[1]+';'+ sentences.split(';')[3])

    print(len(word_count))
    for w in word_count.keys():
        if word_count[w] > nb_times:
            print(w)

    return r_list


com_number = 0
companyIDs = ["telenornorge" , "telianorge", "talkmore.no"  , "chess.no", "onecallmobil", "djuicenorge"]
companyID = companyIDs[com_number]
companyNames = [['Telenor Norge', 'Telenor.no', 'Telenor'] ,
                ['Telia Norge', 'Telia.no', 'Telia', 'Netcom Norge', 'Netcom'],
                ['Talkmore', 'Talkmore.no', 'Talkmore Norge'],
                ['Chess', 'Chess.no', 'Chess Norge'],
                ['OneCall', 'OneCall.no', 'OneCall Norge'],
                ['Djuice', 'Djuice.no', 'Djuice Norge']]



posts = readFile('/home/havikbot/PycharmProjects/data/tele_final/raw/',companyID,'_facebook_visitor_posts.txt')
output = preProcessPosts(posts, companyNames[com_number])
output = remove_numb_times(output, 1)

fileOut = open('/home/havikbot/PycharmProjects/data/tele_final/'+companyID+ '_final_rem1.txt', 'w+')
for line in output:
    fileOut.write(line + '\n')
fileOut.close()



def make_ascii(self):
    file = open(self.inputPath + 'all_onewords_removed.txt', 'r+')
    file_out = open(self.inputPath + 'all_onewords_removed2.txt', 'w+')
    dataelemts = file.readlines()
    for line in dataelemts:
        file_out.write(line.strip().replace("æ", "E").replace("ø", "O").replace("å", "A") + '\n')
    file.close()
    print("conversion complete")









