FROM package-extract-base

ENV THOTH_PKGDEPS_TMP_DIR='/tmp/thoth-package-extract-install'

RUN mkdir -p ${THOTH_PKGDEPS_TMP_DIR}

COPY ./ ${THOTH_PKGDEPS_TMP_DIR}

RUN cd ${THOTH_PKGDEPS_TMP_DIR} && \
    make && \
    rm -rf ${GOPATH} ${THOTH_PKGDEPS_TMP_DIR} && \
    unset THOTH_PKGDEPS_TMP_DIR 

CMD ["extract-image"]
ENTRYPOINT ["thoth-package-extract"]