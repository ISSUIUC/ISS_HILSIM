FROM nginx
WORKDIR /etc/nginx/conf.d
COPY ./conf .
EXPOSE 80
RUN pwd
CMD ["nginx", "-c", "./conf.d/dev.conf"]