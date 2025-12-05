FROM nginx:alpine3.21-slim

COPY entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
RUN chmod +x /usr/local/bin/nginx-entrypoint.sh

# Preserve the default nginx entrypoint; run our script as the CMD.
CMD ["/usr/local/bin/nginx-entrypoint.sh"]
