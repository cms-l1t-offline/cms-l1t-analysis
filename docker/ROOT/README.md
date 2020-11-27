
```bash
git clone git@github.com:cms-l1t-offline/cms-l1t-analysis.git
pushd cms-l1t-analysis/docker/ROOT
ROOT_VERSION=v6-18-04
docker build --build-arg ROOT_VERSION=${ROOT_VERSION} -t cmsl1tanalysis/ROOT:${ROOT_VERSION} .

docker push cmsl1tanalysis/ROOT:${ROOT_VERSION}
popd
```