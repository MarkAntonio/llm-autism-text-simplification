# portSentencer - sentenciador de texto puro para o Portugues
#
# Este programa recebe diversos arquivos de entrada em formato
#    textual e gera um arquivo textual com uma sentença por linha.
#
# Opções:
#
# -h help
# -o output file
# -r replace non standart characters
# -l limit the number of characters per sentence
#
# Exemplo de utilização:
#
# portSent -o sents.txt -r -l 2048 text1.txt text2.txt
#
# Busca o texto nos arquivos 'text1.txt' e 'text2.txt',
#   substitui caracteres não usuais,
#   gera sentenças com limite máximo de 2048 carateres e
#   salva as sentenças no arquivo 'sents.txt'
#
# last edit: 01/21/2024
# created by Lucelene Lopes - lucelene@gmail.com

import sys, os

#################################################
### Captura de argumentos da linha de comando
#################################################
def parseOptions(arguments):
    # default options
    output_file, input_files, replace, limit = "", [], False, 0
    i = 1
    while i < len(arguments):
        if (arguments[i][0] == "-"):
            # ajuda (help) - mostra ajuda, nada é executado
            if ((arguments[i][1] == "h") and (len(arguments[i])==2)) or \
               (arguments[i] == "-help"):
                print("Opções:\n-h ajuda\n-o arquivo de saída", \
                      "-r substitui caracteres não padrão", \
                      "-l limite de caracteres por sentença", \
                      " -demais opções ignoradas, por favor execute novamente sem opção de ajuda",
                      "Exemplo de utilização:", \
                      "portSent -o sents.txt -r -l 2048 text1.txt text2.txt", \
                      "Busca o texto nos arquivos 'text1.txt' e 'text2.txt'", \
                      "  substitui caracteres não usuais,", \
                      "  gera sentenças com limite máximo de 2048 carateres e", \
                      "  salva as sentenças no arquivo 'sents.txt'", \
                      sep="\n")
                return None
            # opção de substituição (replace) de caracteres não usuais
            elif ((arguments[i][1] == "r") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-replace"):
                replace = True
                i += 1
            # opção de limite de tamanho de sentença (limit) - 0 para sem limite
            elif ((arguments[i][1] == "l") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-limit"):
                try:
                    limit = eval(arguments[i+1])
                    i += 2
                except:
                    print("limite de caracteres por sentença não informado - assumindo sem limite")
                    i += 1
            # opção de arquivo de saída (um nome de arquivo)
            elif ((arguments[i][1] == "o") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-output"):
                output_file = arguments[i+1]
                i += 2
            # opções inválidas - nada é executado
            else:
                print("Opção {} inválida, demais opções ignoradas, por favor execute novamente".format(arguments[i]))
                return None
        # arquivos de entrada (qualquer número) - só são incluídos se existirem
        else:
            if (os.path.isfile(arguments[i])):
                input_files.append(arguments[i])
                i += 1
            else:
                print("O arquivo {} não foi encontrado (ignorado)".format(arguments[i]))
                i += 1
    return [output_file, input_files, limit, replace]

#################################################
### função stripSents - faz de fato o sentenciamento
#################################################
def stripSents(inputText, outfile, limit, replace):
    def cleanPrint(sent, outfile):
        # do not print empty sentences
        if (sent == "") or (sent == ".") or (sent == ".."):
            return 0
        # remove second . in sentences ending by ..
        elif (len(sent) > 2) and (sent[-3:] != "...") and (sent[-2:] == ".."):
            print(sent[:-1], file=outfile)
            return 1
        # insert . in sentences not ending by punctuation
        elif (sent[-1] not in [".", "!", "?", ":", ";"]) and \
            not ((sent[-1] in ["'", '"']) and (sent[-2] in [".", "!", "?"])):
            print(sent+".", file=outfile)
            return 1
        # remove encompassing quotations " or ' if the quotations do not appear inside the sentence
        elif (sent[0] == sent[1]) and ((sent[0] == "'") or (sent[0] == '"')) and (sent.count(sent[0]) == 2):
            print(sent[1:-1], file=outfile)
            return 1
        # otherwise print it as it is
        else:
            print(sent, file=outfile)
            return 1
    def isAbbrev(chunk, abbrev):
        abbr = False
        for a in abbrev:
            if (chunk == a):
                abbr = True
                break
            else:
                lasts = -len(a)
                if (chunk[lasts:] == a) and (not chunk[lasts-1].isalpha()):
                    abbr = True
                    break
        return abbr
    # the function stripSents main body
    abbrev = []
    infile = open("abbrev.txt", "r")
    for line in infile:
        abbrev.append(line[:-1])
    infile.close()
    if (replace):
        replaceables = [[" ", " "], \
                        ["—", "-"], ["–", "-"], \
                        ['＂', '"'], \
                        ['“', '"'], ['”', '"'], \
                        ['‟', '"'], ['″', '"'], \
                        ['‶', '"'], ['〃', '"'], \
                        ['״', '"'], ['˝', '"'], \
                        ['ʺ', '"'], ['˶', '"'], \
                        ['ˮ', '"'], ['ײ', '"'], \
                        [" ‣", "."], [" >>", "."], [" ○", "."], [" *", "."], \
                        [" | ", ". "], [" .", "."], \
                        ["\n", " "], ["\t", " "]]
    else:
        replaceables = [["\n", " "], ["\t", " "]]
    tmp = inputText.replace("  "," ")
    for r in replaceables:
        tmp = tmp.replace(r[0], r[1])
    while (tmp.find("  ") != -1):
        tmp = tmp.replace("  "," ")
    if (tmp[0] == " "):
        tmp = tmp[1:]
    bagOfChunks = tmp.split(" ")
    s, sent = 0, ""
    if (bagOfChunks[-1] == ""):
        bagOfChunks.pop()
    for i in range(len(bagOfChunks)):
        # if it is the last chunk, it is the end of sentence
        if (i == len(bagOfChunks)-1):
            sent += " " + bagOfChunks[i]
            s += cleanPrint(sent[1:], outfile)
            break
        chunk = bagOfChunks[i]
        # if there is a limit and the chunk is greater than the limit, discard it
        if (limit != 0) and (len(chunk) > limit):
            continue
        # if there is a limit and it is reached, ends the sentence arbitrarily
        elif (limit != 0) and (len(sent) + len(chunk) > limit):
            s += cleanPrint(sent[1:], outfile)
            sent = chunk
        # if the chunk is too short
        elif (len(chunk) < 3) and (len(chunk) != 0):
            sent += " " + chunk
        # if the chunk is empty
        elif (len(chunk) == 0):
            continue
        # ! ? or ... always mark an end of sentence
        elif (chunk[-3:] == "...") or (chunk[-1] == "!") or (chunk[-1] == "?"):
            sent += " " + chunk
            s += cleanPrint(sent[1:], outfile)
            sent = ""
        # a . : or ; followed by a lowercase chunk is not an end of sentence
        elif ((chunk[-1] == ".") or (chunk[-1] == ":") or (chunk[-1] == ";")) and (bagOfChunks[i+1][0].islower()):
            sent += " " + chunk
        # a : or ; not followed by a lowercase chunk is an end of sentence
        elif ((chunk[-1] == ":") or (chunk[-1] == ";")) and (not bagOfChunks[i+1][0].islower()):
            sent += " " + chunk
            s += cleanPrint(sent[1:], outfile)
            sent = ""
        # chunk ends with ! or ? followed by quotations that had appear before an odd number is an end of sentence
        elif (chunk[-2:] in ["!'", '!"', "?'", '?"']):
            sent += " " + chunk
            s += cleanPrint(sent[1:], outfile)
            sent = ""
        elif (chunk[-2:] in [".'", '."']):
            sent += " " + chunk
            abbr = isAbbrev(chunk[:-1], abbrev)
            if not abbr:
                s += cleanPrint(sent[1:], outfile)
                sent = ""
        # a chunk not ending with ! ? ... ; : or . is not an end of sentence
        elif (chunk[-1] != "."):
            sent += " " + chunk
        # chunk ending by . is either a know abbreviation (not an end of sentence), or an end of sentence
        elif (chunk[-1] == "."):
            abbr = isAbbrev(chunk, abbrev)
            if (abbr):
                sent += " " + chunk
            else:
                sent += " " + chunk
                s += cleanPrint(sent[1:], outfile)
                sent = ""
    # return the number of generated sentences
    return s

#################################################
### função principal do programa - busca argumentos e chama 'stripSents' que faz de fato o sentenciamento
#################################################
def portSent():
    if (len(sys.argv) == 1):
        arguments = ["sents2.txt", ["Teste_Reli.txt"], 0, True]
        print("Assumindo default: 'sents.txt' como arquivo de saída, 'text1.txt' como arquivo de entrada, sem limite e substituições.")
    else:
        arguments = parseOptions(sys.argv)
    if (arguments != None):
        if (arguments[0] == ""):
            print("Assumindo 'sents.txt' como arquivo de saída")
            arguments[0] = 'sents.txt'
        if (arguments[1] == []):
            print("Nenhum arquivo de entrada válido - por favor corrija e tente novamente")
        else:
            outfile = open(arguments[0], "w")
            inputText = ""
            for oneInput in arguments[1]:
                infile = open(oneInput, "r")
                inputText += infile.read()
                infile.close()
            s = stripSents(inputText, outfile, arguments[2], arguments[3])
            outfile.close()
            print("Sentenciamento terminado com {} sentenças extraídas e salvas em {}".format(s, arguments[0]))
    else:
        print("Problemas com parâmetros - por favor corrija e tente novamente")

portSent()


