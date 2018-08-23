from SCons.Script import Command
import os

vars = Variables()
vars.Add('out', '', 'output')

env = Environment(
    variables=vars,
    SHELL='bash',
    input='/mnt/disk15/molmicro/working/ngh2/2018-08-08-bei-refset',
    out='output',
    cwd=os.getcwd(),
    epa=('singularity run --pwd $cwd -B $cwd,$input epa.simg'),
    gappa=('singularity run --pwd $cwd -B $cwd,$input gappa.simg')
)

# refpkg components
# TODO: wrapper script to provide paths of refpkg contents given refpkg as a single argument
# TODO: generate mothur_taxonomy from refpkg
ref_msa='$input/mkrefpkg/output/bei-hm27/bei-hm27-1.0.refpkg/alignment.fasta'
tree='$input/mkrefpkg/output/bei-hm27/bei-hm27-1.0.refpkg/tree_raxml.tre'
tree_stats='$input/mkrefpkg/output/bei-hm27/bei-hm27-1.0.refpkg/tree_raxml.stats'
taxon_file='$input/mkrefpkg/output/bei-hm27/mothur_taxonomy.txt'

# merged alignment
# TODO: add cmmerge to pipeline
merged_msa='$input/yapp/output/merged.fasta'

# known classifications
seq_info='$input/data/seq_info.csv'

qry_msa = env.Command(
    target='$out/seqs_aln.fasta',
    source=[seq_info, merged_msa],
    action='python bin/get_qry_msa.py ${SOURCES[0]} ${SOURCES[1]} > $TARGET'
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
