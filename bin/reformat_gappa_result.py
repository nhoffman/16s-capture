import sys

with open(sys.argv[1], 'r') as file:
    name = ""
    line = file.readline()
    while line:
        if len(line.split('\t')) == 1:
            name = line.strip()
        else: 
            lineage = line.strip().split('\t')[4].split(';')
            if len(lineage) == 7:
                LWR = float(line.split('\t')[0])
                species = lineage[-1][3:]
                print(",".join([name, species, str(LWR)]))
        line = file.readline()
