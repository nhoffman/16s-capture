================
 EPA evaluation
================

setup::

  python3 -m venv py3-env
  source py3-env/bin/activate
  pip install -U pip wheel
  pip install scons

Build gappa Singularity image::

  sudo singularity build gappa.simg Singularity-gappa
  sudo singularity build ea-utils.simg singularity/Singularity_ea-utils
  sudo singularity build htstream.simg singularity/Singularity_htstream

Download PEAR 0.9.11 binaries and sources from
http://www.exelixis-lab.org/web/software/pear - this required filling
out a registration form that worked only on Chrome. Placed these
in /src and copied the binary to /py3-env/bin
