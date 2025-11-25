"""OCR识别服务"""
import os
from typing import Optional, List, Dict, Tuple
from paddleocr import PaddleOCR
from app.utils.logger import logging
from app.core.config import settings


class OCRService:
    """OCR识别服务类"""
    
    def __init__(self):
        """初始化OCR引擎"""
        try:
            # 初始化PaddleOCR，支持中英文识别
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # 使用方向分类器
                lang='ch',  # 中文模型，也支持英文
                use_gpu=False,  # 使用CPU
                show_log=False  # 不显示详细日志
            )
            logging.info("OCR引擎初始化成功")
        except Exception as e:
            logging.error(f"OCR引擎初始化失败: {str(e)}")
            raise
    
    def recognize_text(self, image_path: str) -> Dict:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别结果字典，包含：
            - success: 是否成功
            - text: 识别的完整文本
            - details: 详细识别结果列表
            - error: 错误信息（如果失败）
        """
        try:
            # 验证文件是否存在
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "text": "",
                    "details": [],
                    "error": "图片文件不存在"
                }
            
            # 执行OCR识别
            result = self.ocr.ocr(image_path, cls=True)
            
            # 检查识别结果
            if not result or not result[0]:
                logging.warning(f"OCR未能识别到文本: {image_path}")
                return {
                    "success": True,
                    "text": "",
                    "details": [],
                    "error": None
                }
            
            # 提取文本和详细信息
            text_lines = []
            details = []
            
            for line in result[0]:
                # line格式: [坐标框, (文本, 置信度)]
                box = line[0]  # 坐标框
                text_info = line[1]  # (文本, 置信度)
                text = text_info[0]
                confidence = text_info[1]
                
                text_lines.append(text)
                details.append({
                    "text": text,
                    "confidence": float(confidence),
                    "box": box
                })
            
            # 合并所有文本行
            full_text = "\n".join(text_lines)
            
            logging.info(f"OCR识别成功: {image_path}, 识别到 {len(text_lines)} 行文本")
            
            return {
                "success": True,
                "text": full_text,
                "details": details,
                "error": None
            }
            
        except Exception as e:
            logging.error(f"OCR识别失败: {image_path}, 错误: {str(e)}")
            return {
                "success": False,
                "text": "",
                "details": [],
                "error": str(e)
            }
    
    def recognize_text_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        从字节流识别文字
        
        Args:
            image_bytes: 图片字节流
            
        Returns:
            识别结果字典
        """
        import tempfile
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name
            
            # 识别文本
            result = self.recognize_text(temp_path)
            
            # 删除临时文件
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            logging.error(f"从字节流识别文本失败: {str(e)}")
            return {
                "success": False,
                "text": "",
                "details": [],
                "error": str(e)
            }
    
    def validate_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证图片是否有效
        
        Args:
            image_path: 图片路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            from PIL import Image
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return False, "图片文件不存在"
            
            # 尝试打开图片
            with Image.open(image_path) as img:
                # 验证图片格式
                if img.format not in ['JPEG', 'PNG', 'BMP']:
                    return False, f"不支持的图片格式: {img.format}"
                
                # 验证图片尺寸
                width, height = img.size
                if width < 10 or height < 10:
                    return False, "图片尺寸过小"
                
                if width > 10000 or height > 10000:
                    return False, "图片尺寸过大"
            
            return True, None
            
        except Exception as e:
            return False, f"图片验证失败: {str(e)}"


# 全局OCR服务实例
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """获取OCR服务实例（单例模式）"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
