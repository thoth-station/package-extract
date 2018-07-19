FROM package-extract-base

COPY ./ /tmp/package-extract
RUN cd /tmp/package-extract && \
    make all && \
    rm -rf /tmp/package-extract

CMD ["extract-image"]
ENTRYPOINT ["thoth-package-extract"]
