from ghcr.io/rss-bridge/rss-bridge:latest

COPY ./ /

CMD ["/test-entrypoint.sh"]