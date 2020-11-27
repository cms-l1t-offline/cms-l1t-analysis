FROM centos:centos7

COPY packages packages

RUN yum update -q -y \
    && yum install -y epel-release \
    && yum install -y $(cat packages) \
    && localedef -i en_US -f UTF-8 en_US.UTF-8 \
    && rm -f /packages \
    && rm -fr /var/cache/yum/*

ARG ROOT_VERSION="v6-18-04"

RUN cd /tmp \
    && git clone --depth 1 --branch ${ROOT_VERSION} https://github.com/root-project/root /usr/src/root \
    && cmake3 /usr/src/root \
    -Dminimal=ON \
    -Dcxx11=ON \
    -Dfail-on-missing=ON \
    -Dgnuinstall=ON \
    -Drpath=ON \
    -Dbuiltin_afterimage=OFF \
    -Dbuiltin_ftgl=OFF \
    -Dbuiltin_gl2ps=OFF \
    -Dbuiltin_glew=OFF \
    -Dbuiltin_tbb=ON \
    -Dbuiltin_unuran=OFF \
    -Dbuiltin_vc=ON \
    -Dbuiltin_vdt=ON \
    -Dbuiltin_veccore=ON \
    -Dbuiltin_xrootd=ON \
    -Dgfal=ON \
    -Dtbb=ON \
    -Dpyroot=ON \
    -Dpython=ON \
    -Dxrootd=ON \
    -Dvc=ON \
    -Dveccore=ON \
    -Dssl=ON  \
    -Dmathmore=ON \
    -Ddataframe=ON \
    && cmake3 --build . -- -j$(nproc) \
    && cmake3 --build . --target install \
    && rm -rf /usr/src/root /tmp/*

RUN ln -s /usr/local/bin/root.exe /usr/local/bin/root

ENV PYTHONPATH /usr/local/lib:/usr/local/lib/root