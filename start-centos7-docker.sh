#!/usr/bin/env bash
/usr/bin/docker run --rm --name cms-dev --hostname cms-dev \
  -v /cvmfs:/cvmfs:ro \
  -v ${PWD}:/code \
  -v $PWD/data:/cms/data:ro \
  -v /hdfs:/hdfs:ro \
  -v ~/.ssh:/home/cmsuser/.ssh \
  --network=host \
  --privileged \
  -ti kreczko/cms-dev \
  cdw
