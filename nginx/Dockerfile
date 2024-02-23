FROM nginx:latest
COPY ./conf/terraform-gui.com.conf /etc/nginx/conf.d
RUN mkdir -p /var/www/vhosts/terraform-gui.com/public_html
EXPOSE 80