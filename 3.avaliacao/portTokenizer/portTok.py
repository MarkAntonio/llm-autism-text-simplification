# portTokenizer - tokenizador de sentenças em Portugues para um arquivo CoNLL-U
#
# Este programa recebe um arquivo de entrada textual com uma sentença
#    por linha e gera um arquivo CoNLL-U devidamente tokenizado.
#
# Este programa utiliza um léxico de Português, PortiLexicon-UD através da
#    chamada da classe UDlexPT incluída no arquivo "lexikon.py" disponível
#    em conjunto com este arquivo ("portTok.py") e com os arquivos textuais
#    do léxico ("ADJ.tsv", "ADP.tsv", "ADV.tsv", "AUX.tsv", "CCONJ.tsv", 
#    "DET.tsv", "INTJ.tsv", "NOUN.tsv", "NUM.tsv", "PRON.tsv", "SCONJ.tsv", 
#    "VERB.tsv", "WORDmaster.txt").
#
# Opções:
#
# -h help
# -o output file
# -p preserve as one token itemizations as a) b) and i) ii)
# -m matches the paired punctuations
# -t trims headlines (heuristic)
# -s sentence id (sid) model
#
# Exemplo de utilização:
#
# portTok -o sents.conllu -p -m -t -s S0000 sents.txt
#
# Busca as sentenças no arquivo 'sents.txt',
#   preserva tokens em itens como a) b) i) ii),
#   corrige pontuações casadas (aspas, parenteses, etc),
#   remove possíveis MANCHETES que precedem as frases,
#   usa S0000 como modelo de identificador de sentença e
#   salva as sentenças devidamente tokenizadas no arquivo 'sents.conllu'
#
# last edit: 10/31/2024
# created by Lucelene Lopes - lucelene@gmail.com

import sys, os
import lexikon
lex = lexikon.UDlexPT()


#################################################
### Captura de argumentos da linha de comando
#################################################
def parseOptions(arguments):
    # default options
    output_file, input_file, preserve, match, trim, model = "", [], False, False, False, "S0000"
    i = 1
    while i < len(arguments):
        if (arguments[i][0] == "-"):
            # ajuda (help) - mostra ajuda, nada é executado
            if ((arguments[i][1] == "h") and (len(arguments[i])==2)) or \
               (arguments[i] == "-help"):
                print("Opções:\n-h ajuda\n-o arquivo de saída", \
                      "-m corrige pontuações casadas (aspas, parenteses, etc)", \
                      "-t remove possíveis MANCHETES que precedem as frases", \
                      "Exemplo de utilização:", \
                      "portTok -o sents.conllu -m -t -s S0000 sents.txt", \
                      "Busca as sentenças no arquivo 'sents.txt',", \
                      "  corrige pontuações casadas (aspas, parenteses, etc),", \
                      "  remove possíveis MANCHETES que precedem as frases", \
                      "  usa S0000 como modelo de identificador de sentença e"
                      "  salva as sentenças devidamente tokenizadas no arquivo 'sents.conllu''", \
                      sep="\n")
                return None
            # opção de correção (preserve) para itens a) b) i) ii)
            elif ((arguments[i][1] == "p") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-preserve"):
                preserve = True
                i += 1
            # opção de correção (matching) de pontuações pareadas
            elif ((arguments[i][1] == "m") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-match"):
                match = True
                i += 1
            # opção de remoção (trim) de manchetes no início da sentença
            elif ((arguments[i][1] == "t") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-trim"):
                trim = True
                i += 1
            # opção de modelo de identificador de sentença (sid) - 0 para sem limite
            elif ((arguments[i][1] == "s") and (len(arguments[i])==2)) or \
                 (arguments[i] == "-sid"):
                try:
                    model = arguments[i+1]
                    i += 2
                except:
                    print("modelo de identificador de sentença não informado - assumindo S000")
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
        # arquivo de entrada - só é incluído se existir
        else:
            if (os.path.isfile(arguments[i])):
                input_file = arguments[i]
                i += 1
            else:
                print("O arquivo {} não foi encontrado, por favor execute novamente".format(arguments[i]))
                return None
    return [output_file, input_file, preserve, match, trim, model]

#############################################################################
#  Increment a name index
#############################################################################
def nextName(name):
    # increment the digits from right to left
    ans = ""
    while name != "":
        digit, name = name[-1], name[:-1]
        if digit == "9":
            ans = "0" + ans
        elif digit == "8":
            ans = "9" + ans
            return name+ans
        elif digit == "7":
            ans = "8" + ans
            return name+ans
        elif digit == "6":
            ans = "7" + ans
            return name+ans
        elif digit == "5":
            ans = "6" + ans
            return name+ans
        elif digit == "4":
            ans = "5" + ans
            return name+ans
        elif digit == "3":
            ans = "4" + ans
            return name+ans
        elif digit == "2":
            ans = "3" + ans
            return name+ans
        elif digit == "1":
            ans = "2" + ans
            return name+ans
        elif digit == "0":
            ans = "1" + ans
            return name+ans
        else:
            ans = "1" + ans
            return name+ans
    return "overflow"+ans

#############################################################################
#  Trim the unwanted bits at the sentence - trimIt (step 1)
#############################################################################
def trimIt(s):
    # generate the bits separated by blanks trimming blanks before, after, and multiples
    bits = s.strip().replace("  ", " ").replace("  ", " ").split(" ")
    start = 0
    # remove itemize symbols
    if (bits[0] in ["*", "★", "-", "—", "–", ">", "."]):
        if (len(bits) == 1):
            return ""
        else:
            start = 1
    # remove (BELO HORIZONTE) ... kind
    if (bits[start][0] == "(") and (bits[-1][-1] != ")"):
        for i in range(len(bits)):
            if (bits[i][-1] == ")"):
                start = i+1
                break
    # remove CRONOLOGIA .... kind
    i = start
    while (i<len(bits)):
        if (bits[i].isupper()):
            start = i
            i += 1
        else:
            break
    if ((len(bits[start]) > 1) and (bits[start].isupper())) and \
        (start+1 < len(bits)):              # make sure the next after all upper
        if (bits[start+1][0].isupper()):    #   is not a beginning of sentence
            start += 1
    ans = bits[start]
    for i in range(start+1,len(bits)):
        ans += " "+bits[i]
    return ans

#############################################################################
#  Tag the itemize prompts and double paragraph with //*||*\\ or //*|(|*\\ - tagIt (step 2)
#############################################################################
def tagIt(s):
    romans = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", \
              "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", \
              "xix", "xx", "xxi", "xxii", "xxiii", "xxiv", "xxvi", "xxvii", \
              "xxviii", "xxix", "xxx", "xxxi", "xxxii", "xxxiii", "xxxiv", "xxxv"]
                # limited up to 35
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", \
               "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
                # limited to single letters
    itemizePrompts = romans+letters
    # go over the sent string looking for itemize prompt patern
    ans = ""
    bits = s.split(" ")
    for i in range(len(bits)):
        if (bits[i][-1] == ")"):
            if (bits[i][0] == "("):
                if (bits[i][1:-1] in itemizePrompts):
                    ans += "//*||*\\\\"+bits[i]+"//*||*\\\\ "
                else:
                    ans += bits[i]+" "
            else:
                if (bits[i][0:-1] in itemizePrompts):
                    ans += "//*|(|*\\\\"+bits[i]+"//*||*\\\\ "
                else:
                    ans += bits[i]+" "
        elif (bits[i] == "§§"):
            ans += "//*||*\\\\"+bits[i]+"//*||*\\\\ "
        else:
            ans += bits[i]+" "
    return ans

#############################################################################
#  Clear matching punctuations - punctIt (step 3)
#############################################################################
def punctIt(s):
    def notAlpha(sent):
        ans = True
        for c in sent:
            if c.isalpha():
                ans = False
                break
        return ans
    doubleQuotes = s.count('"')
    singleQuotes = s.count("'")
    openParentes = s.count("(")
    closParentes = s.count(")")
    openBrackets = s.count("[")
    closBrackets = s.count("]")
    openCurBrace = s.count("{")
    closCurBrace = s.count("}")
    openAligator = s.count("<")
    closAligator = s.count(">")
    if  ((doubleQuotes == 2 ) and (s[0] == '"') and (s[-1] == '"')) or \
        ((singleQuotes == 2 ) and (s[0] == "'") and (s[-1] == "'")) or \
        ((openParentes == 1 ) and (closParentes == 1 ) and (s[0] == "(") and (s[-1] == ")")) or \
        ((openBrackets == 1 ) and (closBrackets == 1 ) and (s[0] == "[") and (s[-1] == "]")) or \
        ((openCurBrace == 1 ) and (closCurBrace == 1 ) and (s[0] == "{") and (s[-1] == "}")) or \
        ((openAligator == 1 ) and (closAligator == 1 ) and (s[0] == "<") and (s[-1] == ">")):
        S = s[1:-1].strip()
    else:
        S = s.strip()
    if (doubleQuotes % 2 != 0):
        S = S.replace('"', '')
    if (singleQuotes % 2 != 0):
        S = S.replace("'", "")
    if (openParentes != closParentes):
        S = S.replace("(", "").replace(")", "")
    if (openBrackets != closBrackets):
        S = S.replace("[", "").replace("]", "")
    if (openCurBrace != closCurBrace):
        S = S.replace("{", "").replace("}", "")
    if (openAligator != closAligator):
        S = S.replace("<", "").replace(">", "")
    if (S == "") or (notAlpha(S)):
        return ""
    elif (S[-2:] == "..") and S[-3:] != "...":
        S = S[:-2]+"."
    elif (S[-2:] in [":.", ";."]):
        S = S[:-2]+"."
    elif (S[-1] not in [".", "!", "?", ":", ";"]):
        if (S[-1] in ["'", '"', ")", "]", "}", ">"]) and (S[-2] in [".", "!", "?", ":", ";"]):
            S = S[:-2]+S[-1]+S[-2]
        else:
            S = S+"."
    return S.replace("  ", " ").replace("  ", " ")

#############################################################################
#  Decide if ambiguous tokens are contracted or not - desambIt (within step 4)
#############################################################################
def desambIt(token, bits, i, lastField, s, SID, tokens):
    def stripWord(w):
        start, end = 0, len(w)
        for j in range(len(w)):
            if (not w[j].isalpha()):
                start = j+1
            else:
                break
        for j in range(start,len(w)):
            if (not w[j].isalpha()):
                end = j
                break
        return w[start:end].lower()
    # nos - em os - nos
    if (token.lower() == "nos"):
        if (i > 0):
            preVERB = lex.pexists(stripWord(bits[i-1]), "VERB") or lex.pexists(stripWord(bits[i-1]), "AUX")
        else:
            preVERB = False
        if (i < len(bits)-1):
            posVERB = lex.pexists(stripWord(bits[i+1]), "VERB") or lex.pexists(stripWord(bits[i+1]), "AUX")
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "DET")
            if (posNOUNDET):
                possible = lex.pget(stripWord(bits[i+1]), "NOUN")+lex.pget(stripWord(bits[i+1]), "ADJ")+lex.pget(stripWord(bits[i+1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Sing" not in feats[2]) and ("Gender=Fem" not in feats[2]):
                        agree = True
                        break
                if (not agree):
                    posNOUNDET = False
        else:
            posVERB = False
            posNOUNDET = False
        if (posVERB and not posNOUNDET):
            tokens.append([token, lastField])  # don't break
        else:
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["EM","_"])
                tokens.append(["OS","_"])
            elif (token[0].isupper()):
                tokens.append(["Em","_"])
                tokens.append(["os","_"])
            else:
                tokens.append(["em","_"])
                tokens.append(["os","_"])
    # consigo - com si - consigo
    elif (token.lower() == "consigo"):
        if (i > 0):
            prePRONADV = lex.pexists(stripWord(bits[i-1]), "PRON") or lex.pexists(stripWord(bits[i-1]), "ADV")
        else:
            prePRONADV = False
        if (i < len(bits)-1):
            posVERB = lex.pexists(stripWord(bits[i+1]), "VERB") or lex.pexists(stripWord(bits[i+1]), "AUX")
        else:
            posVERB = False
        if (i < len(bits)-2):
            doQue = ((bits[i+1] == "do") and (bits[i+2] == "que")) or ((bits[i+1] == "sua"))
        else:
            doQue = False
        if ((prePRONADV) or (posVERB)) and (not doQue):
            tokens.append([token, lastField])  # don't break
        else:
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["COM","_"])
                tokens.append(["SI","_"])
            elif (token[0].isupper()):
                tokens.append(["Com","_"])
                tokens.append(["si","_"])
            else:
                tokens.append(["com","_"])
                tokens.append(["si","_"])
    # pra - para a - para
    elif (token.lower() == "pra"):
        if (i < len(bits)-1):
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "DET")
            if (posNOUNDET):
                possible = lex.pget(stripWord(bits[i+1]), "NOUN")+lex.pget(stripWord(bits[i+1]), "ADJ")+lex.pget(stripWord(bits[i+1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Plur" not in feats[2]) and ("Gender=Masc" not in feats[2]):
                        agree = True
                        break
                if (not agree):
                    posNOUNDET = False
        else:
            posNOUNDET = False
        if (posNOUNDET):
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["PARA","_"])
                tokens.append(["A","_"])
            elif (token[0].isupper()):
                tokens.append(["Para","_"])
                tokens.append(["a","_"])
            else:
                tokens.append(["para","_"])
                tokens.append(["a","_"])
        else:
            tokens.append([token, lastField])  # don't break
    # pela - por a - pela
    elif (token.lower() == "pela"):
        if (i < len(bits)-1):
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "NUM") or lex.pexists(stripWord(bits[i+1]), "DET")
            properNOUNDIGIT = bits[i+1][0].isupper() or bits[i+1][0].isnumeric()
        else:
            posNOUNDET = False
            properNOUNDIGIT = False
        if (posNOUNDET) or (properNOUNDIGIT):
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["POR","_"])
                tokens.append(["A","_"])
            elif (token[0].isupper()):
                tokens.append(["Por","_"])
                tokens.append(["a","_"])
            else:
                tokens.append(["por","_"])
                tokens.append(["a","_"])
        else:
            tokens.append([token, lastField])  # don't break
    # pelas - por as - pelas
    elif (token.lower() == "pelas"):
        if (i < len(bits)-1):
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "NUM") or lex.pexists(stripWord(bits[i+1]), "DET")
            properNOUNDIGIT = bits[i+1][0].isupper() or bits[i+1][0].isnumeric()
        else:
            posNOUNDET = False
            properNOUNDIGIT = False
        if (posNOUNDET) or (properNOUNDIGIT):
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["POR","_"])
                tokens.append(["AS","_"])
            elif (token[0].isupper()):
                tokens.append(["Por","_"])
                tokens.append(["as","_"])
            else:
                tokens.append(["por","_"])
                tokens.append(["as","_"])
        else:
            tokens.append([token, lastField])  # don't break
    # pelo - por o - pelo
    elif (token.lower() == "pelo"):
        if (i > 0):
            preART = lex.pexists(stripWord(bits[i-1]), "DET")
            if (preART):
                possible = lex.pget(stripWord(bits[i-1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Plur" not in feats[2]) and ("Gender=Fem" not in feats[2]):
                        agree = True
                        break
                if (not agree):
                    preART = False
                else:
                    preART = (stripWord(bits[i-1]) != "que") and (stripWord(bits[i-1]) != "dado") and (stripWord(bits[i-1]) != "tanto") and (stripWord(bits[i-1]) != "quanto") and (stripWord(bits[i-1]) != "mais")
        else:
            preART = False
        if (i < len(bits)-1):
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "DET")
            posLower = not bits[i+1][0].isupper()
            if (posNOUNDET):
                possible = lex.pget(stripWord(bits[i+1]), "NOUN")+lex.pget(stripWord(bits[i+1]), "ADJ")+lex.pget(stripWord(bits[i+1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Plur" not in feats[2]) and ("Gender=Fem" not in feats[2]):
                        agree = True
                        break
                if (not agree):
                    posNOUNDET = False
        else:
            posNOUNDET = False
            posLower = True
        if (preART) and (not posNOUNDET) and (posLower):
            tokens.append([token, lastField])  # don't break
        else:
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["POR","_"])
                tokens.append(["O","_"])
            elif (token[0].isupper()):
                tokens.append(["Por","_"])
                tokens.append(["o","_"])
            else:
                tokens.append(["por","_"])
                tokens.append(["o","_"])
    # pelos - por os - pelos
    elif (token.lower() == "pelos"):
        if (i > 0):
            preART = lex.pexists(stripWord(bits[i-1]), "DET")
            if (preART):
                possible = lex.pget(stripWord(bits[i-1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Sing" not in feats[2]) and ("Gender=Fem" not in feats[2]) and ("PronType=Art" in feats[2]):
                        agree = True
                        break
                if (not agree):
                    preART = False
                else:
                    preART = (stripWord(bits[i-1]) != "que") and (stripWord(bits[i-1]) != "dado") and (stripWord(bits[i-1]) != "tanto") and (stripWord(bits[i-1]) != "quanto") and (stripWord(bits[i-1]) != "mais")
        else:
            preART = False
        if (i < len(bits)-1):
            posNOUNDET = lex.pexists(stripWord(bits[i+1]), "NOUN") or lex.pexists(stripWord(bits[i+1]), "ADJ") or lex.pexists(stripWord(bits[i+1]), "DET")
            posLower = not bits[i+1][0].isupper()
            if (posNOUNDET):
                possible = lex.pget(stripWord(bits[i+1]), "NOUN")+lex.pget(stripWord(bits[i+1]), "ADJ")+lex.pget(stripWord(bits[i+1]), "DET")
                agree = False
                for feats in possible:
                    if ("Number=Sing" not in feats[2]) and ("Gender=Fem" not in feats[2]) and ("PronType=Art" in feats[2]):
                        agree = True
                        break
                if (not agree):
                    posNOUNDET = False
        else:
            posNOUNDET = False
            posLower = True
        if (preART) and (not posNOUNDET) and (posLower):
            tokens.append([token, lastField])  # don't break
        else:
            tokens.append([token, "c"+lastField])  # break
            if (token.isupper()):
                tokens.append(["POR","_"])
                tokens.append(["OS","_"])
            elif (token[0].isupper()):
                tokens.append(["Por","_"])
                tokens.append(["os","_"])
            else:
                tokens.append(["por","_"])
                tokens.append(["os","_"])

#############################################################################
#  Tokenizing - tokenizeIt (step 4)
#############################################################################
def tokenizeIt(s, SID, outfile):
    removable = ["'", '"', "(", ")", "[", "]", "{", "}", "<", ">", \
                 "!", "?", ",", ";", ":", "=", "+", "*", "★", "|", "/", "\\", \
                 "&", "^", "_", "`", "'", "~", "%", "§"]
    ignored   = ["@", "#"]
    digits  = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    contracts = {"à":["a","a"],
                 "às":["a","as"],
                 "ao":["a", "o"],
                 "aos":["a", "os"],
                 "àquela":["a", "aquela"],
                 "àquelas":["a", "aquelas"],
                 "àquele":["a", "aquele"],
                 "àqueles":["a", "aqueles"],
                 "comigo":["com", "mim"],
                 "contigo":["com", "ti"],
                 "consigo":["com", "si"],
                 "conosco":["com", "nós"],
                 "convosco":["com", "vós"],
                 "da":["de", "a"],
                 "das":["de", "as"],
                 "do":["de", "o"],
                 "dos":["de", "os"],
                 "dali":["de", "ali"],
                 "daqui":["de", "aqui"],
                 "daí":["de", "aí"],
                 "desta":["de", "esta"],
                 "destas":["de", "estas"],
                 "deste":["de", "este"],
                 "destes":["de", "estes"],
                 "dessa":["de", "essa"],
                 "dessas":["de", "essas"],
                 "desse":["de", "esse"],
                 "desses":["de", "esses"],
                 "daquela":["de", "aquela"],
                 "daquelas":["de", "aquelas"],
                 "daquele":["de", "aquele"],
                 "daqueles":["de", "aqueles"],
                 "disto":["de", "isto"],
                 "disso":["de", "isso"],
                 "daquilo":["de", "aquilo"],
                 "dela":["de", "ela"],
                 "delas":["de", "elas"],
                 "dele":["de", "ele"],
                 "deles":["de", "eles"],
                 "doutra":["de", "outra"],
                 "doutras":["de", "outras"],
                 "doutro":["de", "outro"],
                 "doutros":["de", "outros"],
                 "dum":["de", "um"],
                 "duns":["de", "uns"],
                 "duma":["de", "uma"],
                 "dumas":["de", "umas"],
                 "na":["em", "a"],
                 "nas":["em", "as"],
                 "no":["em", "o"],
                 "nos":["em", "os"],
                 "nesta":["em", "esta"],
                 "nestas":["em", "estas"],
                 "neste":["em", "este"],
                 "nestes":["em", "estes"],
                 "nessa":["em", "essa"],
                 "nessas":["em", "essas"],
                 "nesse":["em", "esse"],
                 "nesses":["em", "esses"],
                 "naquela":["em", "aquela"],
                 "naquelas":["em", "aquelas"],
                 "naquele":["em", "aquele"],
                 "naqueles":["em", "aqueles"],
                 "nisto":["em", "isto"],
                 "nisso":["em", "isso"],
                 "naquilo":["em", "aquilo"],
                 "nela":["em", "ela"],
                 "nelas":["em", "elas"],
                 "nele":["em", "ele"],
                 "neles":["em", "eles"],
                 "noutra":["em", "outra"],
                 "noutras":["em", "outras"],
                 "noutro":["em", "outro"],
                 "noutros":["em", "outros"],
                 "num":["em", "um"],
                 "nuns":["em", "uns"],
                 "numa":["em", "uma"],
                 "numas":["em", "umas"],
                 "pela":["por", "a"],
                 "pelas":["por", "as"],
                 "pelo":["por", "o"],
                 "pelos":["por", "os"],
                 "pra":["para", "a"],
                 "pras":["para", "as"],
                 "pro":["para", "o"],
                 "pros":["para", "os"],
                 "prum":["para", "um"],
                 "pruns":["para", "uns"],
                 "pruma":["para", "uma"],
                 "prumas":["para", "umas"]}
    ambigous = ["nos", "consigo", "pra", "pela", "pelas", "pelo", "pelos"]
#    ambigous = ["nos", "consigo", "pra", "pelo", "pelos"]
    enclisis = ['me', 'te', 'se', 'lhe', 'o', 'a', 'nos', 'vos', 'lhes', 'os', 'as', 'lo', 'la', 'los', 'las']
    doubleEnclisis = ["mo", "to", "lho", "lhos", "ma", "ta", "lha", "lhas", "mos", "tos"]
    doubleEnclisisTri = ["no-lo", "vo-lo", "no-la", "vo-la", "no-los", "vo-los", "no-las", "vo-las"]
    terminations = ["ia", "ias", "as", "iamos", "ieis", "iam", "ei", "as", "a", "emos", "eis", "ão", "á"]
    abbrev = []
    infile = open("abbrev.txt", "r")
    for line in infile:
        abbrev.append(line[:-1])
    infile.close()
    def isAbbrev(chunk, abbrev):
        abbr = False
        for a in abbrev:
            if (chunk == a):
                abbr = True
                break
            #else:
            #    lasts = -len(a)
            #    if (chunk[lasts:] == a) and (not chunk[lasts-1].isalpha()):
            #        abbr = True
            #        break
        return abbr
    tokens = []
    bits = s.split(" ")
    k = 0
    for b in bits:
        pretagged = False
        if (len(b) > 16):
            if (b[:8] == "//*||*\\\\") or (b[:9] == "//*|(|*\\\\"):
                pretagged = True
        if (pretagged):
            # keep the bit as token and clean the tags //*||*\\ before and after
            tokens.append([b.replace("//*||*\\\\", "").replace("//*||*\\\\", "").replace("//*|(|*\\\\", ""), "_"])
        else:
            # deal with the pre (before) middle
            pre = []
            changed = True
            while (changed) and (len(b) > 1):
                changed = False
                if (b[0] in removable) or ((b[0] == "$") and (b[1] in digits)) or ((b[0] == "-") and (b[1] not in digits)):
                    pre.append(b[0])
                    b = b[1:]
                    changed = True
            # deal with the pos (after) middle
            tmp = []
            changed = True
            while (changed) and (len(b) > 1):
                if (isAbbrev(b, abbrev)):
                    break
                changed = False
                if (b[-1] in removable+["-", "."]):
                    tmp.append(b[-1])
                    b = b[:-1]
                    changed = True
            pos = []
            reticent = ""
            for i in range(len(tmp)-1, -1, -1):
                if (tmp[i] == "."):
                    if (reticent == ""):
                        reticent = "."
                    elif (reticent == "."):
                        reticent = ".."
                    elif (reticent == ".."):
                        pos.append("...")
                        reticent = ""
                else:
                    if (reticent != ""):
                        pos.append(reticent)
                        reticent = ""
                    pos.append(tmp[i])
            if (reticent != ""):
                pos.append(reticent)
            # deal with the middle
            buf = b.split("-")
            if (len(buf) == 1):
                parts = pre+[b]+pos
            # enclisis (types I - infinitive e.g. cumprí-lo and type II - sonore e.g. satisfê-lo)
            elif (len(buf) == 2) and (buf[1] in enclisis):
                if (buf[0][-1] == "á"):
                    if (lex.pexists(buf[0][:-1]+"ar", "VERB")):
                        parts = pre+["*^*"+b, buf[0][:-1]+"ar", buf[1]]+pos
                    else:
                        if (lex.pexists(buf[0][:-1]+"as", "VERB")):
                            parts = pre+["*^*"+b, buf[0][:-1]+"as", buf[1]]+pos
                        else:
                            parts = pre+["*^*"+b, buf[0][:-1]+"az", buf[1]]+pos
                elif (buf[0][-1] == "ê"):
                    if (lex.pexists(buf[0][:-1]+"er", "VERB")):
                        parts = pre+["*^*"+b, buf[0][:-1]+"er", buf[1]]+pos
                    else:
                        if (lex.pexists(buf[0][:-1]+"es", "VERB")):
                            parts = pre+["*^*"+b, buf[0][:-1]+"es", buf[1]]+pos
                        else:
                            parts = pre+["*^*"+b, buf[0][:-1]+"ez", buf[1]]+pos
                elif (buf[0][-1] == "í"):
                    if (lex.pexists(buf[0][:-1]+"ir", "VERB")):
                        parts = pre+["*^*"+b, buf[0][:-1]+"ir", buf[1]]+pos
                    else:
                        if (lex.pexists(buf[0][:-1]+"is", "VERB")):
                            parts = pre+["*^*"+b, buf[0][:-1]+"is", buf[1]]+pos
                        else:
                            parts = pre+["*^*"+b, buf[0][:-1]+"iz", buf[1]]+pos
                elif (buf[0][-1] == "ô"):
                    if (lex.pexists(buf[0][:-1]+"or", "VERB")):
                        parts = pre+["*^*"+b, buf[0][:-1]+"or", buf[1]]+pos
                    else:
                        if (lex.pexists(buf[0][:-1]+"os", "VERB")):
                            parts = pre+["*^*"+b, buf[0][:-1]+"os", buf[1]]+pos
                        else:
                            parts = pre+["*^*"+b, buf[0][:-1]+"oz", buf[1]]+pos
                else:
                    parts = pre+["*^*"+b, buf[0], buf[1]]+pos
            # double enclisis - type II (e.g. disse-lhos, dei-ta)
            elif (len(buf) == 2) and (buf[1] in doubleEnclisis):
                if (buf[1][-1] == "a"):
                    parts = pre+["*^^*"+b, buf[0], buf[1][:-1]+"e", buf[1][-1]]+pos
                elif (buf[1][-1] == "o"):
                    parts = pre+["*^^*"+b, buf[0], buf[1][:-1]+"e", buf[1][-1]]+pos
                elif (buf[1][-2:] == "as"):
                    parts = pre+["*^^*"+b, buf[0], buf[1][:-2]+"e", buf[1][-2:]]+pos
                elif (buf[1][-2:] == "os"):
                    parts = pre+["*^^*"+b, buf[0], buf[1][:-2]+"e", buf[1][-2:]]+pos
                else:
                    parts = pre+["*^*"+b, buf[0], buf[1]]+pos
            # double enclisis - type I (e.g. dá-se-lhes)
            elif (len(buf) == 3) and (buf[1] in enclisis) and (buf[2] in enclisis):
                if (buf[0][-1] == "á"):
                    parts = pre+["*^^*"+b, buf[0][:-1]+"ar", buf[1], buf[2]]+pos
                elif (buf[0][-1] == "ê"):
                    parts = pre+["*^^*"+b, buf[0][:-1]+"er", buf[1], buf[2]]+pos
                elif (buf[0][-1] == "í"):
                    parts = pre+["*^^*"+b, buf[0][:-1]+"ir", buf[1], buf[2]]+pos
                elif (buf[0][-1] == "ô"):
                    parts = pre+["*^^*"+b, buf[0][:-1]+"or", buf[1], buf[2]]+pos
                else:
                    parts = pre+["*^^*"+b, buf[0], buf[1], buf[2]]+pos
            # mesoclisis - type I (e.g. dar-lo-ia)
            elif (len(buf) == 3) and (buf[1] in enclisis) \
                and (buf[0][-1] == "r") and (buf[2] in terminations):
                parts = pre+["*^*"+b, buf[0]+buf[2], buf[1]]+pos
            # mesoclisis - type II (e.g. dá-lo-ia)
            elif (len(buf) == 3) and (buf[1] in enclisis) \
                and (buf[0][-1] in ["á", "ê", "í", "ô"]) and (buf[2] in terminations):
                if (buf[0][-1] == "á"):
                    parts = pre+["*^*"+b, buf[0][:-1]+"ar"+buf[2], buf[1]]+pos
                elif (buf[0][-1] == "ê"):
                    parts = pre+["*^*"+b, buf[0][:-1]+"er"+buf[2], buf[1]]+pos
                elif (buf[0][-1] == "í"):
                    parts = pre+["*^*"+b, buf[0][:-1]+"ir"+buf[2], buf[1]]+pos
                elif (buf[0][-1] == "ô"):
                    parts = pre+["*^*"+b, buf[0][:-1]+"or"+buf[2], buf[1]]+pos
            else:
                parts = pre+[b]+pos
            # transform parts into tokens to be added
            i = 0
            while (i < len(parts)):
                if (i == len(parts)-1):
                    lastField = "_"
                else:
                    lastField = "SpaceAfter=No"
                if (parts[i][:3] == "*^*"):
                    if (i+3 == len(parts)):
                        tokens.append([parts[i][3:], "c_"])
                    else:
                        tokens.append([parts[i][3:], "cSpaceAfter=No"])
                    i += 1
                    tokens.append([parts[i], "_"])
                    i += 1
                    tokens.append([parts[i], "_"])
                elif (parts[i][:4] == "*^^*"):
                    if (i+4 == len(parts)):
                        tokens.append([parts[i][4:], "C_"])
                    else:
                        tokens.append([parts[i][4:], "CSpaceAfter=No"])
                    i += 1
                    tokens.append([parts[i], "_"])
                    i += 1
                    tokens.append([parts[i], "_"])
                    i += 1
                    tokens.append([parts[i], "_"])
                elif (parts[i] not in ambigous):
                    ans = contracts.get(parts[i].lower())
                    if (ans == None):
                        tokens.append([parts[i], lastField])
                    else:
                        tokens.append([parts[i], "c"+lastField])
                        if (parts[i].isupper()):
                            tokens.append([ans[0].upper(),"_"])
                            tokens.append([ans[1].upper(),"_"])
                        elif (parts[i][0].isupper()):
                            tokens.append([ans[0][0].upper()+ans[0][1:],"_"])
                            tokens.append([ans[1],"_"])
                        else:
                            tokens.append([ans[0],"_"])
                            tokens.append([ans[1],"_"])
                else:
                    desambIt(parts[i], bits, k, lastField, s, SID, tokens)
                i += 1
        k += 1
    # output the sentence with all the tokens
    print("# sent_id =", SID, file=outfile)
    print("# text =", s.replace("//*||*\\\\", "").replace("//*||*\\\\", "").replace("//*|(|*\\\\", ""), file=outfile)
    ## printout tokens
    toks = 0
    for i in range(len(tokens)):
        if (tokens[i][1][0] == "c"):
            # contracted word (two parts)
            print(str(toks+1)+"-"+str(toks+2), tokens[i][0], "_", "_", "_", "_", "_", "_", "_", tokens[i][1][1:], sep="\t", file=outfile)
        elif (tokens[i][1][0] == "C"):
            # contracted word (three parts)
            print(str(toks+1)+"-"+str(toks+3), tokens[i][0], "_", "_", "_", "_", "_", "_", "_", tokens[i][1][1:], sep="\t", file=outfile)
        elif (tokens[i][0].strip() != ""):
            # non contracted word
            toks += 1
            print(str(toks), tokens[i][0].strip(), "_", "_", "_", "_", "_", "_", "_", tokens[i][1], sep="\t", file=outfile)
    print(file=outfile)
    return(toks)

#################################################
### Deal with a sentence, clean it, if required, then tokenize it
#################################################
def dealWith(outfile, sent, SID, preserve, match, trim):
    if (trim):       # step 1
        sent = trimIt(sent)
    if (preserve):   # step 2
        sent = tagIt(sent)
    if (match):      # step 3
        sent = punctIt(sent)
    if (sent != ""): # step 4
        return 1, tokenizeIt(sent, SID, outfile)
    else:
        return 0, 0

#################################################
### função principal do programa - busca argumentos e chama 'tokenize' para cada sentença da entrada
#################################################
def portTok():
    if (len(sys.argv) == 1):
        #arguments = ["/Users/pf64/Desktop/alienista/alienista_empty.conllu", "/Users/pf64/Desktop/alienista/alienista.txt", False, True, False, "ATENISTA_SENT0000"]
        arguments = ["sents.conllu", "sents.txt", True, True, True, "S0000"]
        print("Assumindo default: 'sents.conllu' como arquivo de saída, 'sents.txt' como arquivo de entrada, correções, remoções e S0000 como sid.")
    else:
        arguments = parseOptions(sys.argv)
    if (arguments != None):
        if (arguments[0] == ""):
            print("Assumindo 'sents.conllu' como arquivo de saída")
            arguments[0] = 'sents.conllu'
        if (arguments[1] == []):
            print("Arquivo de entrada inválido - por favor corrija e tente novamente")
        else:
            outfile = open(arguments[0], "w")
            #print("# newdoc id = {}\n# newpar".format(arguments[0]), file=outfile)
            infile = open(arguments[1], "r")
            SID = arguments[5]
            sTOTAL, tTOTAL = 0, 0
            for line in infile:
                SID = nextName(SID)
                s, t = dealWith(outfile, line[:-1], SID, arguments[2], arguments[3], arguments[4])
                if (s == 1):
                    sTOTAL += 1
                    tTOTAL += t
            outfile.close()
            infile.close()
            print("Tokenização terminada com {} sentenças extraídas ({} tokens) e salvas em {}".format(sTOTAL, tTOTAL, arguments[0]))
    else:
        print("Problemas com parâmetros - por favor corrija e tente novamente")

portTok()
