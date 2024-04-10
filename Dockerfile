FROM ulaskaraoz/kb_debmicrotrait2:latest

RUN curl --location https://kbmicrotrait.s3.us-west-1.amazonaws.com/microtrait_1.0.0.tar.gz > /tmp/microtrait.tar.gz
RUN R -e "install.packages('/tmp/microtrait.tar.gz', repos = NULL, type='source')"
RUN R -e "microtrait::prep.hmmmodels()"
RUN pip install pypdf

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]