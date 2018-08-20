import argparse

parser = argparse.ArgumentParser()
parser.add_argument('epa_classification', help="csv with epa classifications")
parser.add_argument('seq_info', help="file with info about ref seqs")
args = parser.parse_args()

epa_results = {}
with open(args.epa_classification, 'r') as file:
    for line in file:
        name, species, LWR = line.strip().split(',')
        if name not in epa_results:
            epa_results[name] = []
        epa_results[name].append((species, float(LWR)))

print(",".join(['seq_name', 'tax_name', 'species', 'LWR']))

with open(args.seq_info, 'r') as file:
    for line in file:
        seq_name, _, tax_name = line.split(',')[:3]
        if seq_name in epa_results.keys():
            # concatenate epa_classification into one list of species-LWR pairs, sorted by LWR
            epa_class = [str(x)
                         for pair in sorted(epa_results[seq_name], key=lambda (species, LWR): LWR, reverse=True)
                         for x in pair]
            print(",".join([seq_name, tax_name[1:-1]] + epa_class))
            


