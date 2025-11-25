import os
from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from dao.TestData import Data
from utils.baseresponse import ResponseModel
from core.fileConfig import accept_file, file_prefix_path
from utils.businessexception import ErrorCode
from utils.logger import logging


router = APIRouter()

@router.get("/get/", summary="get测试接口", tags=["test"])
async def get_test(data: str):
    """
    此接口只用来进行get请求测试在开发时请删去
    """
    return ResponseModel.success(data)

@router.post("/post/{id}", summary="post测试接口", tags=["test"])
async def post_test(id:int, q:str | None = None, data: Data = None):
    """
    此接口只用来进行post请求测试在开发时请删去
    """
    res = {"id": id}
    if q: 
        res.update({"q": q})
    if data: 
        res.update({"data": data})
    return ResponseModel.success(res)

@router.post("/file/", summary="上传文件测试接口", tags=["test"])
async def file_test(file: bytes = File()):
    """
    此接口只用来进行上传文件测试在开发时请删去
    该接口以bytes形式接收和读取文件内容适用于小型文件
    """
    return {"file_size": len(file)}

@router.post("/uploadfile/", summary="优先采用上传文件测试接口", tags=["test"])
async def upload_file_test(file: UploadFile):
    """
    此接口只用来进行上传文件测试在开发时请删去
    该接口以UploadFile形式接收和读取文件内容适用于*所有文件*
    """
    filename = file.filename
    type =  file.content_type
    type, suffix= type.split("/")
    if suffix not in accept_file:
        return ResponseModel.error(ErrorCode.OPERATION_ERROR, f"文件类型错误只接受{accept_file}类型")
    file_path = os.path.join(file_prefix_path, type, filename)
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    except Exception as e:
        logging.error(f"文件夹创建失败：" + e)
        return ResponseModel.error(ErrorCode.OPERATION_ERROR, "文件夹创建失败")
    with open(file_path, "wb") as f:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            f.write(chunk)
    await file.close()
    return ResponseModel.success(file_path)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.get("/items/")
async def read_items(token: Annotated[str| None, Depends(oauth2_scheme)]):
    return {"token": token}
