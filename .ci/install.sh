!/usr/bin/env bash
# In Python 3.4, we test the min version of NumPy and SciPy. In Python 2.7, we test more recent version.
if test -e ${CMSL1T_CONDA_PATH}/envs/cms; then
    echo "cms env already exists."
else
    echo "Creating cms env."
    conda create --yes -q -n cms python=${TRAVIS_PYTHON_VERSION}
fi

source activate cms
conda update conda -yq
conda update pip -yq
conda install psutil -yq
conda config --add channels http://conda.anaconda.org/NLeSC
conda config --set show_channel_urls yes

conda install -y -q \
  matplotlib \
  numpy \
  pandas==0.23 \
  root>=6.04 \
  root-numpy \
  rootpy

pip install -r requirements.txt
source deactivate
