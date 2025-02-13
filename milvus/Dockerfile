FROM milvusdb/milvus:v2.5.4

COPY embedEtcd.yaml /milvus/configs/embedEtcd.yaml
COPY user.yaml /milvus/configs/user.yaml

CMD ["milvus", "run", "standalone"]
