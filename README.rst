===========================
 16S rRNA Capture Pipeline
===========================

Pipleine code for "Sensitive identification of bacterial DNA in clinical specimens by broad range 16S rRNA enrichment"

Sara Rassoulian Barrett [1], Noah G. Hoffman [1], Christopher Rosenthal [1], Andrew Bryan [1], Desiree A. Marshall [2], Joshua Lieberman [1], Brad T. Cookson [1], Stephen J. Salipante [1] (corresponding author)

- [1] Department of Laboratory Medicine, University of Washington, Seattle, WA, USA
- [2] Department of Pathology, University of Washington, Seattle, WA, USA

setup
=====

create a virtualenv::

  python3 -m venv py3-env
  source py3-env/bin/activate
  pip install -U pip wheel
  pip install scons==3.0.5
  pip install -r requirements.txt

Extract PEAR binary: PEAR 0.9.11 binaries and sources were downloaded
from http://www.exelixis-lab.org/web/software/pear - this required
filling out a registration form that worked only on Chrome. These are
stored in /src. To copy the binary to the virtualenv::

  tar -xf src/pear-0.9.11-linux-x86_64.tgz --strip-components 2 -C py3-env/bin pear-0.9.11-linux-x86_64/bin/pear

Build the Singularity images::

  mkdir -p singularity_images
  for fn in singularity/*; do sudo singularity build singularity_images/${fn#singularity/Singularity_}.simg $fn; done

methods
=======

Reference set creation
----------------------

A bacteria mock community of 16S rRNA gene reference sequences was acquired
and assembed from BEI Resources and aligned and used to create phylogenetic
trees [1].  Two additional reference packages were assembled by recruiting
16S rRNA reference sequences from a ya16sdb 0.4 curated set of NCBI 16s
sequences [2] and selecting based on similarity to clinical specimens using
DeeNuRP 0.2.4 search-sequences and select-references [3][4].

16s Classification
------------------

Illumina MiSeq reads were filtered, trimmed, deduplicated and assembled using
barcodecop 0.5 [5], ea-utils 1.04.807 fastqc-mcf [6],
HTStream 0.3.0 SuperDeduper [7] and PEAR 0.9.11 [8] respectively.  16s reads
were selected using Infernal 1.1.2 cmsearch and aligned using cmalign [9].
The resulting alignments were merged with reference alignments
(using 'esl-alimerge') to place all sequences in the same alignment register.
Query sequences were then placed on a phylogenetic tree of reference sequences
using epa-ng 0.3.5 [10] and classified using gappa 0.2.4 [11]. The full Python
Scons pipeline is available for evalutation at
https://github.com/salipante/16s-capture.git.

1. bei resources
2. https://github.com/nhoffman/ya16sdb
3. https://github.com/fhcrc/deenurp/tree/master/deenurp
4. https://doi.org/10.1371/journal.pone.0065226
5. https://github.com/nhoffman/barcodecop
6. https://github.com/ExpressionAnalysis/ea-utils
7. https://github.com/ibest/HTStream
8. https://doi.org/10.1093/bioinformatics/btt593
9. https://doi.org/10.1093/bioinformatics/btt509
10. https://doi.org/10.1093/sysbio/syy054
11. https://doi.org/10.1093/bioinformatics/btaa070
