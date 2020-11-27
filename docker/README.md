
# Docker files for CMS L1T analysis

## Build ROOT docker container (baseline)

Since installing from conda-forge can take a bit of time, we instead build our own ROOT docker image.
This image will serve as a baseline for analysis images and it allows us to freeze ROOT and its dependencies in place.

```bash
git clone git@github.com:cms-l1t-offline/cms-l1t-analysis.git
pushd cms-l1t-analysis/docker/ROOT
ROOT_VERSION=v6-18-04
docker build \
  --build-arg ROOT_VERSION=${ROOT_VERSION} \
  -t cmsl1tanalysis/root:${ROOT_VERSION} .

docker push cmsl1tanalysis/root:${ROOT_VERSION}
popd
```

## Build dev docker

```bash
git clone git@github.com:cms-l1t-offline/cms-l1t-analysis.git
cd cms-l1t-analysis
ROOT_VERSION=v6-18-04
docker build \
  --build-arg ROOT_VERSION=${ROOT_VERSION} \
  -t cmsl1tanalysis/cmsl1t-dev:root_${ROOT_VERSION} \
  -f docker/dev/Dockerfile .

docker push cmsl1tanalysis/cmsl1t-dev:root_${ROOT_VERSION}
```

## Build production docker

```bash
git clone git@github.com:cms-l1t-offline/cms-l1t-analysis.git
cd cms-l1t-analysis
ROOT_VERSION=v6-18-04
CMSL1T_VERSION=$(python -c 'from __future__ import print_function; import cmsl1t; print(cmsl1t.__version__)')

docker build \
  --build-arg ROOT_VERSION=${ROOT_VERSION} \
  -t cmsl1tanalysis/cmsl1t:${CMSL1T_VERSION}_root_${ROOT_VERSION} \
  -f docker/production/Dockerfile .

docker push cmsl1tanalysis/cmsl1t:${CMSL1T_VERSION}_root_${ROOT_VERSION}
```

## Run dev docker

Development docker container does not have the cms-l1t-analysis package installed - it needs to be mounted from the host instead.

```bash
ROOT_VERSION=v6-18-04

docker run \
  -v $PWD:/opt/cms-l1t-analysis \
  -ti cmsl1tanalysis/cmsl1t-dev:root_${ROOT_VERSION} \
  bash
```

## Run production docker

```bash
ROOT_VERSION=v6-18-04
# /tmp or in a different location
mkdir -p /tmp/output
CMSL1T_VERSION=$(python -c 'from __future__ import print_function; import cmsl1t; print(cmsl1t.__version__)')

docker run \
  -v /tmp/output:/opt/cms-l1t-analysis/output \
  -ti cmsl1tanalysis/cmsl1t:${CMSL1T_VERSION}_root_${ROOT_VERSION} \
  cmsl1t config/demo.yaml
```