FROM fedora:27
CMD ["extract-image"]
ENTRYPOINT ["thoth-package-extract"]
ENV \
 LANG=en_US.UTF-8 \
 THOTH_PKGDEPS_TMP_DIR='/tmp/thoth-package-extract-install' \
 GOPATH='/tmp/go'

RUN \
 dnf update -y &&\
 mkdir -p ${THOTH_PKGDEPS_TMP_DIR}

# Install thoth-package-deps itself
COPY ./ ${THOTH_PKGDEPS_TMP_DIR}
RUN \
 cd ${THOTH_PKGDEPS_TMP_DIR} &&\
 sh hack/install_rpm.sh &&\
 make &&\
 rm -rf ${GOPATH} ${THOTH_PKGDEPS_TMP_DIR} &&\
 unset THOTH_PKGDEPS_TMP_DIR &&\
 dnf clean all
