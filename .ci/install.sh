#!/usr/bin/env bash
# In Python 3.4, we test the min version of NumPy and SciPy. In Python 2.7, we test more recent version.
if test -e ${CMSL1T_CONDA_PATH}/envs/cms; then
    echo "cms env already exists."
else
    echo "Creating cms env."
    conda install -y -q psutil
    conda create --yes -q -n cms python=${TRAVIS_PYTHON_VERSION}
fi

source activate cms
conda config --add channels http://conda.anaconda.org/NLeSC
conda config --set show_channel_urls yes

conda install -y -q \
  matplotlib \
  numpy \
  root>=6.04 \
  rootpy

pip install -U pip
pip install -r requirements.txt
source deactivate
