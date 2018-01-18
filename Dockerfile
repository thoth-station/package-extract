FROM fedora:27
ENTRYPOINT ["thoth-pkgdeps"]
CMD ["thoth-pkgdeps"]
ENV \
  LANG=en_US.UTF-8 \
  THOTH_PKGDEPS_TMP_DIR='/tmp/thoth-pkgdeps-install' \
  GOPATH='/tmp/go'

RUN \
  dnf update -y &&\
  dnf install -y python3 python3-pip python-pip go git make skopeo dnf-utils &&\
  dnf clean all &&\
  mkdir -p ${THOTH_PKGDEPS_TMP_DIR}

# Install thoth-pkgdeps itself
COPY . ${THOTH_PKGDEPS_TMP_DIR}
RUN \
  cd ${THOTH_PKGDEPS_TMP_DIR} &&\
  make &&\
  pip3 install . &&\
  unset THOTH_PKGDEPS_TMP_DIR
