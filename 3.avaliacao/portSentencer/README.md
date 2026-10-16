# portSentencer
This repository has the `portSent.py` program, a sentencer for Portuguese text.

This program receives as input one or more textual files with text in Portuguese and generates a single textual file where each sentence is saved in a different line.

## Sentencing Example
For example, if the following text is given as input:

`A rua Dr. Flores é uma rua da cidade de Porto`

`Alegre? Provavelmente, 90% dos gaúchos vai`

`dizer-nos que sim. Até os que não moram`

`nos bairros de Porto Alegre.`

The output will be split in three sentences:

`A rua Dr. Flores é uma rua da cidade de Porto Alegre?`

`Provavelmente, 90% dos gaúchos vai dizer-nos que sim.`

`Até os que não moram nos bairros de Porto Alegre.`

To do so, this program needs a list of known abbreviations in Portuguese that is read from the file `abbrev.txt`.

## Program Options
This program also performs, optionally, replacing of unusual characters, as non standard quotation marks and dashes, by the traditional characters available in both ASCII and UTF-8.

Another option available in this program is to provide a limit for the number of characters in each sentence.

## Usage example
`python3 portSent.py -o sents.txt -r -l 2048 text1.txt text2.txt`

This command fetch the input from files `text1.txt` and `text2.txt`, it performs the substitution of non standard characters (`-r`) and sets a limit of 2048 characters per sentence (`-l 2048`), saving the produced sentences in the file `sents.txt` (`-o sents.txt`).

# Contents
The files in this repository are:
- `README.md` - this read explanatory file;
- `portSent.py` - the Python 3 program;
- `abbrev.txt` - a list of usual abbreviation used in Portuguese, one abbreviation (cased) per line, you can edit this file for your own application;
- `text1.txt` - an input file to be used as example;
- `sents.txt` - the output file generated reading the example input file.

# Acknowledgments
This work was carried out at the Center for Artificial Intelligence of the University of São Paulo (C4AI - [http://c4ai.inova.usp.br/](http://c4ai.inova.usp.br/)), with support by the São Paulo Research Foundation (FAPESP grant #2019/07665-4) and by the IBM Corporation. The project was also supported by the Ministry of Science, Technology and Innovation, with resources of Law N. 8.248, of October 23, 1991, within the scope of PPI-SOFTEX, coordinated by Softex and published as Residence in TIC 13, DOU 01245.010222/2022-44.

