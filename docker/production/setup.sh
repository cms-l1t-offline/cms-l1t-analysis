#!/usr/bin/env bash
PROJECT_NAME="cms-l1t-analysis"

if [ -n "${PROJECT_ROOT}" ] ; then
   old_projectbase=${PROJECT_ROOT}
fi

if [ "x${BASH_ARGV[0]}" = "x" ]; then
    if [ ! -f setup.sh ]; then
        echo ERROR: must "cd where/${PROJECT_NAME}/is" before calling ". setup.sh" for this version of bash!
        PROJECT_ROOT=; export PROJECT_ROOT
        return 1
    fi
    PROJECT_ROOT="$PWD"; export PROJECT_ROOT
else
    # get param to "."
    envscript=$(dirname ${BASH_ARGV[0]})
    PROJECT_ROOT=$(cd ${envscript};pwd); export PROJECT_ROOT
fi

# clean PATH and PYTHONPATH
if [ -n "${old_projectbase}" ] ; then
  PATH=`python ${PROJECT_ROOT}/bin/remove_from_path.py "$PATH" "${old_projectbase}"`
  PYTHONPATH=`python ${PROJECT_ROOT}/bin/remove_from_path.py "$PYTHONPATH" "${old_projectbase}"`
fi

# add project to PYTHONPATH
if [ -z "${PYTHONPATH}" ]; then
   PYTHONPATH=${PROJECT_ROOT}; export PYTHONPATH
else
   PYTHONPATH=${PROJECT_ROOT}:$PYTHONPATH; export PYTHONPATH
fi

# add project to PATH
PATH=${PROJECT_ROOT}/bin:$PATH; export PATH
# add local bin to PATH (for local flake8 installations, etc)
export PATH=~/.local/bin:$PATH

unset old_projectbase
unset envscript

# Capture the user's site-packages directory:
USER_SITE_PACKAGES="$(python -c "import site; print(site.USER_SITE)")"
# add project to PYTHONPATH
PYTHONPATH="${USER_SITE_PACKAGES}:$PYTHONPATH"

git submodule init
git submodule update

ulimit -c 0

echo "Environment for ${PROJECT_NAME} is ready"
