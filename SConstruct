import os
import json
from os.path import join

from SCons.Script import Command

vars = Variables()
vars.Add('out', '', 'output')

env = Environment(
    variables=vars,
    SHELL='bash',
    input='/mnt/disk15/molmicro/working/ngh2/2018-08-08-bei-refset',
    out='output',
    cwd=os.getcwd(),
    epa=('singularity run --pwd $cwd -B $cwd,$input epa.simg'),
    gappa=('singularity run --pwd $cwd -B $cwd,$input gappa.simg'),
    taxit=('singularity exec '
           '--pwd $cwd -B $cwd,$input '
           '/molmicro/common/singularity/taxtastic-0.8.5-singularity2.4.img '
           'taxit')
)

##### inputs #######
# TODO: move to a config file

refpkg = '/mnt/disk15/molmicro/working/ngh2/2018-08-08-bei-refset/mkrefpkg/output/bei-hm27/bei-hm27-1.0.refpkg'

# merged alignment
# TODO: add cmmerge to pipeline
merged_msa = '$input/yapp/output/merged.fasta'

# known classifications
seq_info = '$input/data/seq_info.csv'

##### end inputs ###

def get_refpkg_contents(refpkg):
    with open(join(refpkg, 'CONTENTS.json')) as jfile:
        files = json.load(jfile)['files']
        return {k: join(refpkg, v) for k, v in files.items()}


refpkg_files = get_refpkg_contents(refpkg)
ref_msa = refpkg_files['aln_fasta']
tree = refpkg_files['tree']
tree_stats = refpkg_files['tree_stats']
ref_info = refpkg_files['seq_info']
ref_taxonomy = refpkg_files['taxonomy']

# TODO: if we start with the query sequences and align, this becomes unnecessary
qry_msa = env.Command(
    target='$out/seqs_aln.fasta',
    source=[seq_info, merged_msa],
    action='python bin/get_qry_msa.py ${SOURCES[0]} ${SOURCES[1]} > $TARGET'
)

taxon_file = env.Command(
    target='$out/taxonomy.txt',
    source=[ref_taxonomy, ref_info],
    action='$taxit lineage_table $SOURCES --taxonomy-table $TARGET'
)

epa_placements, epa_log = env.Command(
    target=['$out/epa_result.jplace', '$out/epa_info.log'],
    source=[ref_msa, tree, qry_msa, tree_stats],
    action=('$epa '
            '--ref-msa ${SOURCES[0]} '
            '--tree ${SOURCES[1]} '
            '--query ${SOURCES[2]} '
            '--model `python bin/get_model_descriptor.py ${SOURCES[3]}` '
            '--outdir $out')
)

# names of gappa targets appear to be hard-coded
labelled_tree, per_pquery_assign, profile = env.Command(
    target=['$out/labelled_tree', '$out/per_pquery_assign', '$out/profile.csv'],
    source=[epa_placements, taxon_file],
    action=('$gappa analyze assign '
            '--out-dir $out '
            '--jplace-path ${SOURCES[0]} --taxon-file ${SOURCES[1]}')
)

epa_classification = env.Command(
    target='$out/epa_classification.csv',
    source=per_pquery_assign,
    action='python bin/reformat_gappa_result.py $SOURCE > $TARGET'
)

comparison_table = env.Command(
    target='$out/comparison_table.csv',
    source=[epa_classification, seq_info],
    action='python bin/compare_results.py ${SOURCES[0]} ${SOURCES[1]} > $TARGET'
)
