================
 EPA evaluation
================

setup
=====

create a virtualenv::

  python3 -m venv py3-env
  source py3-env/bin/activate
  pip install -U pip wheel
  pip install scons
  pip install -r requirements.txt

Extract PEAR binary: PEAR 0.9.11 binaries and sources were downloaded
from http://www.exelixis-lab.org/web/software/pear - this required
filling out a registration form that worked only on Chrome. These are
stored in /src. To copy the binary to the virtualenv::

  tar -xf src/pear-0.9.11-linux-x86_64.tgz --strip-components 2 -C py3-env/bin pear-0.9.11-linux-x86_64/bin/pear

Build the Singularity images::

  mkdir -p singularity_images
  for fn in singularity/*; do sudo singularity build singularity_images/${fn#singularity/Singularity_}.simg $fn; done

