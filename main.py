#!/bin/env python3
#Author: Saurabh Pathak
#Main program: Stiches the pipeline together
#Usage: (main.py sourcefileneame) or just (main.py) for a text cli :)
from subprocess import Popen, PIPE, DEVNULL
from sys import argv, stderr
import ebmt, rulebaseprior, xml_input, data, os

def make_chunkset(text, tags, l, verbose=True):
    if verbose: print('Applying rules...', sep='', end='', flush=True, file=stderr)
    chunkset = rulebaseprior.apply_rules(text, tags, l)
    if verbose: print('Done\nEBMT is running...', sep='', end='', flush=True, file=stderr)
    chunkset.extend(ebmt.run(text, bm, l))
    if verbose: print('Done', flush=True, file=stderr)
    return chunkset

def translate_sent(text, p):
    print('Tagging input...', sep='', end='', flush=True, file=stderr)
    tags = rulebaseprior.tag_input(text)
    print('Done', flush=True, file=stderr)
    text = text.split()
    l = len(text)
    xml = xml_input.construct(make_chunkset(text, tags, l), text, l)
    print('Partially translated xml input:', xml, file=stderr)
    p.stdin.write('{}\n'.format(xml))
    p.stdin.flush()
    print('Moses is translating...', flush=True, file=stderr)
    print('Translated:', p.stdout.readline())

def translate_file(text):
    print('Tagging input...', sep='', end='', flush=True, file=stderr)
    tags = rulebaseprior.tag_input_file(text)
    print('Done\nRunning RBMT+EBMT...',sep='', end='', flush=True, file=stderr)
    i = 0
    with open(text) as f, open('{}/xml.out'.format(run), 'w', encoding='utf-8') as xml:
        for line in f:
            line = line.split()
            l = len(line)
            xml.write('{}\n'.format(xml_input.construct(make_chunkset(line, tags[i], l, False), line, l)))
            i += 1
    with open('{}/smt.out'.format(run), 'w') as smt:
        print('Done\nMoses is translating...', sep='', end='', flush=True, file=stderr)
        p = Popen('moses -inputtype 0 -f {} -xml-input inclusive -mp -i {}/xml.out'.format(ini, run).split(), universal_newlines=True, stdout=smt, stderr=DEVNULL)
        p.wait()
        smt.flush()
        if len(argv) == 3:
            p = Popen('{}/generic/multi-bleu.perl {}'.format(os.environ['SCRIPTSROOTDIR'], argv[2]).split(), universal_newlines=True, stdin=smt)
    print('Done\nCheck en.out in data/run. Bye!', flush=True, file=stderr)

print('Loading example-base...', sep='', end='', flush=True, file=stderr)
data.load()
print('Done\nLoading suffix arrays...', sep='', end='', flush=True, file=stderr)
bm = ebmt._BestMatch(data.dbdir)
print('Done', flush=True, file=stderr)
run  = '{}/data/run'.format(os.environ['THESISDIR'])
ini = '{}/moses-interactive.ini'.format(run)
try: translate_file(os.path.abspath(argv[1]))
except IndexError:
    print('Starting moses...', sep='', end='', flush=True, file=stderr)
    p = Popen('moses -inputtype 0 -f {} -xml-input inclusive -mp'.format(ini).split(), universal_newlines=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    while 'input-output' not in p.stderr.readline(): pass
    print('Ready\nWelcome to the SILP Hindi to English Translator!', flush=True, file=stderr)
    while True:
        try:
            text = input('Enter one Hindi sentence or ctrl+d to exit:\n')
            translate_sent(text, p)
        except EOFError:
            print('Bye!', file=stderr)
            exit(0)