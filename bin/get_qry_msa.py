import argparse

parser = argparse.ArgumentParser()
parser.add_argument('seq_info', help="file with info about ref seqs")
parser.add_argument('merged_fasta', help="file with ref and qry msa")
args = parser.parse_args()

qry_seq_names = set()
with open(args.seq_info, 'r') as file:
    for line in file:
        qry_seq_names.add(line.split(',')[0])

with open(args.merged_fasta, 'r') as file:
    while True:
        try:
            name_line = file.next()
            seq_line = file.next()
            name = name_line.strip()[1:]
            seq = seq_line.strip()
            if name in qry_seq_names:
                print('>' + name)
                print(seq)
        except StopIteration:
            break
