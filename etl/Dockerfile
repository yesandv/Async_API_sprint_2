FROM elasticsearch:8.10.1

COPY etl/restore.sh /usr/share/elasticsearch/restore.sh

CMD ["sh", "-c", "/usr/share/elasticsearch/restore.sh"]
