# portTokenizer
This repository has `portTok.py` program, a tokenizer for Portuguese text using Universal Dependencies (UD) format (CoNLL-U) to store the tokenized sentences.

This program receives as input a single textual file with the sentences, one per line, and generates a `.conllu` file with all sentences tokenized according to the CoNLL-U format.

The tokenization process performs usual tokenization tasks, as dealing with punctuations, but also performs the decomposition of contracted words (e.g. `da` is decontracted into `de`+ `a`), enclisis (e.g. `dizer-nos` is decomposed into `dizer`+`nos`), mesoclisis (`ajudar-nos-ia` is decomposed into `ajudaria`+ `nos`), explicit double enclisis (e.g. `assegurando-se-lhes` is decomposed into `assegurando`+`se`+`lhes`), and implicit double enclisis (e.g. `disse-lho` is decomposed into `disse`+`lhe`+`o`) while the original form is kept in the CoNLL-U as a contracted token (see example below).

Another important feature of the tokenizer is the heuristic to disambiguate word forms that can either be a contracted word or not, as is the case of the pronoun `nos` and the contracted preposition and determiner `em`+`os`. The other dealt cases are the forms `consigo` and `com`+`si`, `pelo` and `por`+`o`, `pelos` and `por`+`os`, `pela` and `por`+`a`, `pelas` and `por`+`as`, and finally the case of `pra` that can either be an abbreviated form of `para` or `para`+`a`. To perform these disambiguations the tokenizer uses the PortiLexicon-UD, a Portuguese lexikon to examine the possible classes of neighboring words of the disambiguation candidates. An example of disambiguation is shown below in sentence examples that have one time the form `nos` employed as a pronoun and another time employed as the contracted preposition and determiner `em`+`o` (see example below).

This program also consults a list of known abbreviations in Portuguese that is read from the file `abbrev.txt`.

## Tokenization Example

For example, if the following sentences are the input of the tokenizer:

`A rua Dr. Flores é uma rua da cidade de Porto Alegre?`

`Provavelmente, 90% dos gaúchos vai dizer-nos que sim.`

`Até os que não moram nos bairros de Porto Alegre.`

The follwing CoNLL-U will be generated:

![conllu1](https://github.com/LuceleneL/portTokenizer/assets/81653183/45190e19-ecf1-451d-b7f2-f5dab7affeeb)
![conllu2](https://github.com/LuceleneL/portTokenizer/assets/81653183/d067587e-fa0d-4531-bbe5-178dcaf4ba5e)
![conllu3](https://github.com/LuceleneL/portTokenizer/assets/81653183/8a4bc06d-dcc4-4b5e-837c-d70993d7640b)

## Program Options
This program also performs, optionally, the avoidance of breaking into multiple tokens chunks used on enumerative itemizations using letters as `a)` or `(b)`, and with roman numbers `iii)` or `(iv)`. Therefore, such set of characters is not decomposed leaving the parenthesis together with the enumeration label in a single token. This option is triggered on with the argument `-p`.

This program also performs, optionally, a verification of the matching punctuations (quotation marks, parenthesis, brackets, curly braces) eventually removing missing pairs. This option is triggered on with the argument `-m`.

Another option available is the removal of uppercased preambules in sentences, usually found as headlines in jornalistic texts, as for example the sentence:

`A CRONOLOGIA Governo concede visto de permanência a Battisti em 2015.`

Where the words `A CRONOLOGIA` is not a part of the sentence, and therefore the sentence can be trimmed by the removal of the headline words. This option is triggered on with the argument `-t`.

Another option available in the program is the definition of a model for the sentence identifier (SID) to be used in the produced CoNLL-U. For example if the model `S0000` is given, the sentences will be numbered as `S0001`, `S0002`, and so on. This option is triggered on with the argument `-s` followed by the model..

## Usage example
`python3 portTok -o sents.conllu -p -m -t -s S0000 sents.txt`

This command fetch the input from files `sents.txt`, while: It avoids enumerative item chunks (`-p`); It performs the matching of paired punctuations (`-m`); It performs the trim of sentence headlines (`-t`); and It sets the SID model as `S0000` (`-s S0000`). The resulting CoNLL-U is saved into the file `sents.conllu` (`-o sents.conllu`).

 # Contents
 The main files in this repository are:
- `README.md` - this read explanatory file;
- `portTok.py` - the Python 3 program;
- `abbrev.txt` - list of known abbreviations in Portuguese;
- `sents.txt` - the input file to be used as example;
- `sents.conllu` - the output file generated reading the example input file.

As this program uses a Portuguese lexikon (PortLexicon-UD), this lexikon files are included here, namely:
- `lexikon.py` - a Python 3 package file with the `class UDlexPT`, plus the data files:
   - `ADJ.tsv`
   - `ADP.tsv`
   - `ADV.tsv`
   - `AUX.tsv`
   - `CCONJ.tsv`
   - `DET.tsv`
   - `INTJ.tsv`
   - `NOUN.tsv`
   - `NUM.tsv`
   - `PRON.tsv`
   - `SCONJ.tsv`
   - `VERB.tsv`
   - `WORDmaster.txt`

# Acknowledgments
This work was carried out at the Center for Artificial Intelligence of the University of São Paulo (C4AI - [http://c4ai.inova.usp.br/](http://c4ai.inova.usp.br/)), with support by the São Paulo Research Foundation (FAPESP grant #2019/07665-4) and by the IBM Corporation. The project was also supported by the Ministry of Science, Technology and Innovation, with resources of Law N. 8.248, of October 23, 1991, within the scope of PPI-SOFTEX, coordinated by Softex and published as Residence in TIC 13, DOU 01245.010222/2022-44.

