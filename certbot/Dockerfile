FROM certbot/certbot

COPY entrypoint.sh /usr/local/bin/certbot-entrypoint.sh
RUN chmod +x /usr/local/bin/certbot-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/certbot-entrypoint.sh"]
