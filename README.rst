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

