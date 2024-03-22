FROM ulaskaraoz/kb_debmicrotrait_base

RUN curl --location https://github.com/ukaraoz/microtrait/releases/download/kb/microtrait_1.0.0.tar.gz > /tmp/microtrait.tar.gz
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