FROM alpine:3.14

RUN apk update
RUN apk add postgresql

COPY dump-database.sh .

ENTRYPOINT [ "/bin/sh" ]
CMD [ "./dump-database.sh" ]