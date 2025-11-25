from pymilvus import MilvusClient
from app.core.config import settings
import logging

milvus_client = None
# 注册milvus 连接
if settings.USE_MILVUS:
   try:
      milvus_client = MilvusClient(host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
   except Exception as e:
      logging.error(f"Milvus connection error {e}")

def get_milvus():
   if milvus_client is None:
      logging.info("MilcvusClient connetct error")
      return None
   logging.info(f"Milvus connected {milvus_client.get_server_version}")
   return milvus_client
    

def del_milvus():
   if milvus_client: 
      milvus_client.close()


