import argparse

parser = argparse.ArgumentParser()
parser.add_argument('stats_file', help="file with raxml tree stats")
args = parser.parse_args()


dna = False
sub_mat = None
alpha = None
freqs = []
rates = []

with open(args.stats_file, 'r') as file:
    for line in file:
        if line.startswith("DataType:"):
            dna = (line.strip().split()[1] == "DNA")
        elif line.startswith("Substitution Matrix"):
            sub_mat = line.strip().split()[2]
            if not dna and sub_mat == "GTR":
                sub_mat = "PROTGTR"
        elif line.startswith("Base frequencies:"):
            freqs = line.strip().split()[2:]
        elif line.startswith("alpha"):
            _, raw_alpha, raw_rates = line.strip().split(':')
            alpha = raw_alpha.split()[0]
            rates = raw_rates.split()

model_descriptor = sub_mat + "{" + "/".join(rates) + "}+FU{" + "/".join(freqs) + "}+G4{" + alpha + "}"
print(model_descriptor)