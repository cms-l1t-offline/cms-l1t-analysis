ARG ROOT_VERSION
FROM cmsl1tanalysis/root:${ROOT_VERSION}

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir -U "pip<21.0" "setuptools<45.0.0" wheel \
 && python -m pip install --no-cache-dir -U rootpy "numpy<1.17" \
 && python -m pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt/cms-l1t-analysis/build
ENV PROJECT_ROOT /opt/cms-l1t-analysis
ENV PATH ${PROJECT_ROOT}/bin:${PATH}
ENV PYTHONPATH ${PROJECT_ROOT}:${PYTHONPATH}

ADD bin ${PROJECT_ROOT}/bin
ADD cmsl1t ${PROJECT_ROOT}/cmsl1t
ADD config ${PROJECT_ROOT}/config
ADD docs ${PROJECT_ROOT}/docs
ADD examples ${PROJECT_ROOT}/examples
ADD test ${PROJECT_ROOT}/test
ADD Makefile ${PROJECT_ROOT}/.
ADD README.md ${PROJECT_ROOT}/.
ADD run_lumi.csv ${PROJECT_ROOT}/.

RUN cd ${PROJECT_ROOT} \
  && make setup-external

WORKDIR ${PROJECT_ROOT}
