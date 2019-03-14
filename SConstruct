import os
import json
from os.path import join, basename
import configparser
from collections import namedtuple, OrderedDict
import csv

from SCons.Script import Command
from bioscons.fileutils import rename


def get_refpkg(refpkg):
    """Return a namedtuple with attributes corresponding to files in the
    refpkg

    """

    with open(join(refpkg, 'CONTENTS.json')) as jfile:
        files = json.load(jfile)['files']
        Refpkg = namedtuple('Refpkg', sorted(files.keys()))
        return Refpkg(**{k: join(refpkg, v) for k, v in files.items()})


##### inputs #######
conf_file = 'settings.conf'
conf = configparser.ConfigParser(allow_no_value=True)
conf.read(conf_file)

images = {k + '_simg': v for k, v in conf['singularity'].items()
          if k not in set(conf['DEFAULT'].keys()) and not k.startswith('_')}

krona_labels = conf.get('input', 'krona_labels')

data_file = 'data/data.conf'
data = configparser.ConfigParser(allow_no_value=True)
data.read(data_file)

sections = list(data.items())[1:]  # exclude DEFAULT section

##### end inputs ###

Decider('MD5-timestamp')
vars = Variables()
vars.Add('out', '', conf['output']['outdir'])

# Define some PATH elements explicitly.
venv = os.environ['VIRTUAL_ENV']
PATH=':'.join([
    'bin',
    join(venv, 'bin'),
    '/app/bin',  # provides R
    '/usr/local/bin', '/usr/bin', '/bin'])

env = Environment(
    ENV=dict(os.environ, PATH=PATH),
    variables=vars,
    SHELL='bash',
    cwd=os.getcwd(),
    epa=('singularity run --pwd $cwd -B $cwd,$refpkg $epa_simg'),
    gappa=('singularity run --pwd $cwd -B $cwd $gappa_simg'),
    krona=('singularity run --pwd $cwd -B $cwd $krona_simg'),
    fastq_mcf=('singularity exec '
               '--pwd $cwd -B $cwd $ea_utils_simg fastq-mcf'),
    super_deduper=('singularity exec '
                   '--pwd $cwd -B $cwd $htstream_simg hts_SuperDeduper'),
    deenurp_img=('singularity exec --pwd $cwd -B $cwd,$refpkg $deenurp_simg'),
    nproc=15,
    **images
)

## begin analysis
krona_data = []
for_counts = []
for label, input in sections:
    r1, r2 = input['r1'], input['r2']
    refpkg_pth = input['refpkg']

    refpkg = get_refpkg(refpkg_pth)

    e = env.Clone(
        label=label,
        out='$out/$label',
        refpkg=refpkg_pth,
    )

    # TODO: do this only once for each refpkg
    taxon_file = e.Command(
        target='$out/ref_taxonomy.txt',
        source=[refpkg.taxonomy, refpkg.seq_info],
        action=('singularity exec --pwd $cwd -B $cwd,$refpkg $taxit_simg taxit '
                'lineage_table $SOURCES --taxonomy-table $TARGET')
    )

    for_counts.append(r1)

    # barcode filter
    # TODO: move max_reads to settings.conf or data.conf
    max_reads = None
    bcop_action = ('barcodecop ${SOURCES[1:]} -f ${SOURCES[0]} '
                   '--outfile $TARGET '
                   '--match-filter '
                   '--qual-filter '
                   '--min-qual 30 ')
    if max_reads:
        bcop_action += ' --head {}'.format(max_reads)

    if input['indexing'] == 'single':
        index_reads = [r1.replace('_R1_', '_I1_')]
    elif input['indexing'] == 'dual':
        index_reads = [r1.replace('_R1_', '_I1_'), r1.replace('_R1_', '_I2_')]
    else:
        raise ValueError('invalid value for indexing: "{}"'.format(input['indexing']))

    r1_bcop = e.Command(
        target='$out/r1_barcodecop.fastq.gz',
        source=[r1] + index_reads,
        action=bcop_action
    )
    for_counts.append(r1_bcop)

    r2_bcop = e.Command(
        target='$out/r2_barcodecop.fastq.gz',
        source=[r2] + index_reads,
        action=bcop_action
    )

    # trim and quality filter
    r1_cleaned, r2_cleaned, fqmcf_log = e.Command(
        target=['$out/cleaned_R1.fastq.gz',
                '$out/cleaned_R2.fastq.gz',
                '$out/fastq_mcf.log'],
        source=['data/Illumina_adaptors_v2.fa', r1_bcop, r2_bcop],
        action=('$fastq_mcf -o ${TARGETS[0]} -o ${TARGETS[1]} '
                '-D 0 -k 0 -q 5 -l 25 $SOURCES '
                '1> ${TARGETS[2]}')
    )
    for_counts.append(r1_cleaned)

    # remove PCR duplicates
    r1_deduped, r2_deduped, dedup_log = e.Command(
        target=['$out/deduped_R1.fastq',
                '$out/deduped_R2.fastq',
                '$out/super_deduper.log'],
        source=[r1_cleaned, r2_cleaned],
        action=('$super_deduper --force '
                '--prefix $out/deduped '
                '--read1-input ${SOURCES[0]} '
                '--read2-input ${SOURCES[1]} '
                '--stats-file ${TARGETS[2]} ')
    )
    for_counts.append(r1_deduped)

    # assemble paired reads
    assembled_fq, discarded, r1_unassembled_fq, r2_unassembled_fq = e.Command(
        target=['$out/pear.assembled.fastq',
                '$out/pear.discarded.fastq',
                '$out/pear.unassembled.forward.fastq',
                '$out/pear.unassembled.reverse.fastq'],
        source=[r1_deduped, r2_deduped],
        action=('pear -f ${SOURCES[0]} -r ${SOURCES[1]} '
                '--min-trim-length 25 '
                '--threads $nproc '
                '--output $out/pear ')
        )
    for_counts.extend([assembled_fq, discarded, r1_unassembled_fq])

    # convert to fasta
    assembled = e.Command(
        target=rename(assembled_fq, ext='.fasta'),
        source=assembled_fq,
        action='seqmagick convert $SOURCE $TARGET')

    r1_unassembled = e.Command(
        target=rename(r1_unassembled_fq, ext='.fasta'),
        source=r1_unassembled_fq,
        action='seqmagick convert --name-suffix _r1 $SOURCE $TARGET')

    r2_unassembled = e.Command(
        target=rename(r2_unassembled_fq, ext='.fasta'),
        source=r2_unassembled_fq,
        action='seqmagick convert --name-suffix _r2 $SOURCE $TARGET')

    # concatenate into a single file
    unfiltered = e.Command(
        target='$out/unfiltered.fasta',
        source=[
            assembled,
            r1_unassembled, r2_unassembled],
        action='cat $SOURCES > $TARGET'
    )

    # remove non-16s reads
    seqs_16s, seqs_not16s, cmsearch_scores = e.Command(
        target=['$out/seqs-16s.fasta',
                '$out/seqs-not16s.fasta',
                '$out/cmsearch_scores.txt'],
        source=[unfiltered, 'data/RRNA_16S_BACTERIA.calibrated.cm'],
        action=('$deenurp_img '
                'bin/cmfilter.py $SOURCES '
                '--outfile ${TARGETS[0]} '
                '--discarded ${TARGETS[1]} '
                '--scores ${TARGETS[2]} '
                '--min-evalue 0.01 '
                '--cpu $nproc '
                '--reverse-complement ')
    )
    Depends(seqs_16s, 'bin/cmfilter.py')
    for_counts.extend([seqs_16s, seqs_not16s])

    # align input seqs with cmalign
    query_sto, cmalign_scores = e.Command(
        target=['$out/query.sto', '$out/cmalign.scores'],
        source=[seqs_16s, refpkg.profile],
        # ncores=args.nproc,
        # timelimit=30,
        # slurm_args = '--mem=130000',
        # slurm_queue=large_queue,
        action=(
            '$deenurp_img '
            'cmalign '
            '--cpu $nproc '
            '--mxsize 8196 '
            '--noprob '
            '--dnaout '
            '-o ${TARGETS[0]} '  # alignment in stockholm format
            '--sfile ${TARGETS[1]} '  # scores
            '${SOURCES[1]} '  # alignment profile
            '${SOURCES[0]} '  # input fasta file
            '| grep -E "^#"'  # limit stdout to commented lines
        ))

    # place ref and query alignments into the same alignemnt register
    refalign, qalign_unmerged = e.Command(
        target=['$out/refalign.fasta', '$out/qalign_unmerged.fasta'],
        source=[refpkg.aln_sto, query_sto],
        action=('$deenurp_img bin/merge.py $SOURCES $TARGETS')
    )
    Depends(refalign, 'bin/merge.py')
    for_counts.append(qalign_unmerged)

    # calculate a consensus for unassembled read pairs
    qalign = e.Command(
        target='$out/qalign.fasta',
        source=qalign_unmerged,
        action='bin/get_consensus.py $SOURCE -o $TARGET'
    )
    Depends(qalign, 'bin/get_consensus.py')
    for_counts.append(qalign)

    # place reads onto the reference tree
    epa_placements, epa_log = e.Command(
        target=['$out/epa_result.jplace', '$out/epa_info.log'],
        source=[refalign, refpkg.tree,
                # qalign_unmerged,
                qalign,
                refpkg.tree_stats],
        action=('$epa '
                '--ref-msa ${SOURCES[0]} '
                '--tree ${SOURCES[1]} '
                '--query ${SOURCES[2]} '
                '--model $$(python bin/get_model_descriptor.py ${SOURCES[3]}) '
                '--outdir $out')
    )

    # classify
    # names of gappa targets appear to be hard-coded
    labelled_tree, per_pquery_assign, gappa_profile, krona_raw = e.Command(
        target=['$out/labelled_tree', '$out/per_pquery_assign',
                '$out/profile.csv', '$out/krona-${label}-raw'],
        source=[epa_placements, taxon_file],
        action=[('$gappa analyze assign '
                '--krona '
                '--out-dir $out '
                '--jplace-path ${SOURCES[0]} '
                 '--taxon-file ${SOURCES[1]}'),
                'mv $out/krona.profile ${TARGETS[3]}']
    )
    # krona_data.append(krona_raw)

    # filter by likelihood and reformat
    classifications, lineages, krona_filtered = e.Command(
        target=['$out/classifications.csv',
                '$out/lineages.csv',
                '$out/krona-${label}-filtered'],
        source=per_pquery_assign,
        action=('bin/get_classifications.py $SOURCE '
                '--classifications ${TARGETS[0]} '
                '--lineages ${TARGETS[1]} '
                '--krona ${TARGETS[2]} '
                '--min-afract 0.30 '
                '--min-total 0.45 '
        )
    )
    Depends(classifications, 'bin/get_classifications.py')
    krona_data.append(krona_filtered)

    krona = e.Command(
        target='$out/krona.html',
        source=[krona_raw, krona_filtered],
        action='$krona -o $TARGET $SOURCES'
    )

# count reads in all fastq files
read_counts = env.Command(
    target='$out/read_counts.csv',
    source=Flatten(for_counts),
    action='bin/read_depth.py -j $nproc $SOURCES -o $TARGET'
)

read_stats = env.Command(
    target='$out/read_stats.csv',
    source=[data_file, read_counts],
    action='read_stats.py $SOURCES -o $TARGET'
)

# all krona plots
if krona_data:
    if krona_labels:
        with open(krona_labels) as f:
            labels = OrderedDict(csv.reader(f))

        krona_data_labeled = [(str(f).split('/')[1], f) for f in krona_data]
        krona_data_labeled.sort(key=lambda x: list(labels.keys()).index(x[0]))
        krona_action = ('$krona -o $TARGET {}'.format(
            ' '.join('{},"{}"'.format(f, labels[bc]) for bc, f in krona_data_labeled)))
    else:
        krona_action = '$krona -o $TARGET $SOURCES'

    krona_all = env.Command(
        target='$out/krona.html',
        source=krona_data,
        action=krona_action
    )

# save project state
version_info = env.Command(
    target='$out/version_info.txt',
    source='SConstruct',
    action=('pwd > $out/$TARGET && '
            'git status >> $out/$TARGET && '
            'git --no-pager log -n1 >> $out/$TARGET ')
)

conf_out = env.Command(
    target='$out/data.conf',
    source=conf_file,
    action=Copy('$TARGET', '$SOURCE')
)
