ARG ROOT_VERSION
FROM cmsl1tanalysis/root:${ROOT_VERSION}

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir -U "pip<21.0" "setuptools<45.0.0" \
 && python -m pip install --no-cache-dir -U rootpy "numpy<1.17" \
 && python -m pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /opt/cms-l1t-analysis
ENV PROJECT_ROOT /opt/cms-l1t-analysis
ENV PATH ${PROJECT_ROOT}/bin:${PATH}
ENV PYTHONPATH ${PROJECT_ROOT}:${PYTHONPATH}

