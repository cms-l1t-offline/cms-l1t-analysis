FROM cern/cc7-base:20201116-1.x86_64

ENV CMSL1T_CONDA_PATH /software/cmsl1t/miniconda

# ROOT requirements
# RUN sudo apt install -y \
#     libjpeg \
#     libnss3-dev \
#     libreadline-dev \
#     libxpm-dev \
#     libxft-dev

RUN mkdir -p ${CMSL1T_CONDA_PATH}; rmdir ${CMSL1T_CONDA_PATH}
RUN yum install wget -y

RUN wget -nv https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
  bash /tmp/miniconda.sh -b -p ${CMSL1T_CONDA_PATH} && \
  rm -f miniconda.sh
ENV PATH="${CMSL1T_CONDA_PATH}/bin:$PATH"

RUN echo "Finished conda installation, updating conda and pip" && \
  conda update conda -yq && \
  conda update pip -yq && \
  conda install psutil -yq && \
  conda clean -t -y

COPY conda_requirements.txt /tmp/conda_requirements.txt

RUN conda create -n cms python=2.7 -yq &&\
  echo "Created conda environment, installing basic dependencies" && \
  /bin/bash -c "source activate cms && \
  conda install -yq --file /tmp/conda_requirements.txt -c conda-forge" && \
  conda clean -t -y

COPY requirements.txt /tmp/requirements.txt

RUN /bin/bash -c "source activate cms && \
  python -m pip install -U rootpy && \
  python -m pip install -U pip && \
  python -m pip install -r requirements.txt && \
  pip install --no-cache-dir -r /tmp/requirements.txt" && \
  conda clean -t -y

