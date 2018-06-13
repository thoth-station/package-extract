FROM package-extract-base

RUN make &&  

CMD ["extract-image"]
ENTRYPOINT ["thoth-package-extract"]
