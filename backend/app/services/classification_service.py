"""AI分类服务"""
import re
import json
import httpx
from typing import Dict, Optional, List, Tuple
from datetime import datetime, date, time
from app.utils.logger import logging
from app.core.config import settings


class ClassificationService:
    """AI分类服务类 - 用于识别和分类文本内容（使用LLM）"""
    
    # 分类置信度阈值
    CONFIDENCE_THRESHOLD = 0.6
    
    # LLM API配置
    LLM_API_URL = getattr(settings, 'LLM_API_URL', 'http://localhost:8000/v1/chat/completions')
    LLM_MODEL = getattr(settings, 'LLM_MODEL', 'Qwen/Qwen2-VL-7B-Instruct')
    LLM_TIMEOUT = 30.0  # 超时时间（秒）
    
    # 日程关键词
    SCHEDULE_KEYWORDS = [
        '会议', '约', '预约', '安排', '计划', '提醒', '待办',
        '明天', '今天', '后天', '下周', '下月',
        '点', '时', '分', '上午', '下午', '晚上', '早上',
        'meeting', 'appointment', 'schedule', 'plan', 'todo',
        'am', 'pm', 'tomorrow', 'today'
    ]
    
    # 备忘录关键词
    MEMO_KEYWORDS = [
        '记录', '笔记', '想法', '感想', '总结', '心得', '日记',
        '备忘', '提示', '注意', '重要',
        'note', 'memo', 'idea', 'thought', 'diary', 'journal'
    ]
    
    # 时间模式
    TIME_PATTERNS = [
        r'\d{1,2}[：:]\d{2}',  # 14:30, 14：30
        r'\d{1,2}点\d{0,2}分?',  # 14点30分, 14点
        r'(上午|下午|晚上|早上)\d{1,2}点',  # 下午2点
        r'\d{1,2}\s*(am|pm|AM|PM)',  # 2 pm
    ]
    
    # 日期模式
    DATE_PATTERNS = [
        r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?',  # 2024-01-01, 2024年1月1日
        r'\d{1,2}[-/月]\d{1,2}日?',  # 1-1, 1月1日
        r'(明天|后天|今天|昨天)',
        r'(下周|下月|本周|本月)',
        r'(周|星期)(一|二|三|四|五|六|日|天)',
    ]
    
    def __init__(self):
        """初始化分类服务"""
        self.use_llm = True  # 默认使用LLM
        self.client = httpx.AsyncClient(timeout=self.LLM_TIMEOUT)
        logging.info(f"分类服务初始化成功 (LLM模式: {self.use_llm}, API: {self.LLM_API_URL})")
    
    async def classify_text_with_llm(self, text: str) -> Dict:
        """
        使用LLM分类文本内容
        
        Args:
            text: 待分类的文本
            
        Returns:
            分类结果字典
        """
        prompt = f"""请分析以下文本，判断它是"日程安排"还是"备忘录"。

日程安排的特征：
- 包含明确的时间信息（日期、时间）
- 描述未来要做的事情
- 通常包含会议、约会、活动等关键词

备忘录的特征：
- 记录想法、心得、笔记
- 没有明确的时间要求
- 通常是个人记录或总结

文本内容：
{text}

请以JSON格式返回结果，包含以下字段：
{{
    "type": "schedule" 或 "memo",
    "confidence": 0.0-1.0之间的置信度,
    "reasoning": "分类理由"
}}

只返回JSON，不要其他内容。"""

        try:
            response = await self.client.post(
                self.LLM_API_URL,
                json={
                    "model": self.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个文本分类助手，擅长区分日程安排和备忘录。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # 兼容不同的API响应格式
                choice = result['choices'][0]
                if 'messages' in choice:
                    content = choice['messages']['content']
                elif 'message' in choice:
                    content = choice['message']['content']
                else:
                    content = choice.get('content', '')
                
                # 解析JSON响应
                # 尝试提取JSON（可能包含在markdown代码块中）
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                classification = json.loads(content)
                
                # 根据分类类型提取信息
                if classification['type'] == 'schedule':
                    extracted_data = self.extract_schedule_info(text)
                else:
                    extracted_data = self.extract_memo_info(text)
                
                return {
                    "type": classification['type'],
                    "confidence": float(classification['confidence']),
                    "extracted_data": extracted_data
                }
            else:
                logging.warning(f"LLM API返回错误: {response.status_code}")
                return self._fallback_classify(text)
                
        except Exception as e:
            logging.error(f"LLM分类失败: {str(e)}")
            return self._fallback_classify(text)
    
    def classify_text(self, text: str) -> Dict:
        """
        分类文本内容（同步接口，用于向后兼容）
        
        Args:
            text: 待分类的文本
            
        Returns:
            分类结果字典，包含：
            - type: 'schedule' 或 'memo'
            - confidence: 置信度 (0-1)
            - extracted_data: 提取的结构化数据
        """
        if not text or not text.strip():
            return {
                "type": "memo",
                "confidence": 0.5,
                "extracted_data": {}
            }
        
        # 如果不使用LLM，使用规则方法
        if not self.use_llm:
            return self._fallback_classify(text)
        
        # 使用规则方法作为后备（因为同步方法无法调用异步LLM）
        return self._fallback_classify(text)
    
    def _fallback_classify(self, text: str) -> Dict:
        """
        后备分类方法（基于规则）
        
        Args:
            text: 待分类的文本
            
        Returns:
            分类结果字典
        """
        # 计算日程和备忘录的得分
        schedule_score = self._calculate_schedule_score(text)
        memo_score = self._calculate_memo_score(text)
        
        # 判断类型
        if schedule_score > memo_score:
            classification_type = "schedule"
            confidence = schedule_score
            extracted_data = self.extract_schedule_info(text)
        else:
            classification_type = "memo"
            confidence = memo_score
            extracted_data = self.extract_memo_info(text)
        
        logging.info(f"文本分类结果（规则方法）: {classification_type}, 置信度: {confidence:.2f}")
        
        return {
            "type": classification_type,
            "confidence": confidence,
            "extracted_data": extracted_data
        }
    
    def _calculate_schedule_score(self, text: str) -> float:
        """计算日程得分"""
        score = 0.0
        text_lower = text.lower()
        
        # 检查时间模式
        has_time = any(re.search(pattern, text) for pattern in self.TIME_PATTERNS)
        if has_time:
            score += 0.4
        
        # 检查日期模式
        has_date = any(re.search(pattern, text) for pattern in self.DATE_PATTERNS)
        if has_date:
            score += 0.3
        
        # 检查日程关键词
        keyword_count = sum(1 for keyword in self.SCHEDULE_KEYWORDS if keyword in text_lower)
        score += min(keyword_count * 0.1, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_memo_score(self, text: str) -> float:
        """计算备忘录得分"""
        score = 0.4  # 基础分数（降低以避免默认为备忘录）
        text_lower = text.lower()
        
        # 检查备忘录关键词
        keyword_count = sum(1 for keyword in self.MEMO_KEYWORDS if keyword in text_lower)
        score += min(keyword_count * 0.15, 0.3)
        
        # 如果文本较长且没有明确的时间信息，更可能是备忘录
        if len(text) > 50:
            has_time = any(re.search(pattern, text) for pattern in self.TIME_PATTERNS)
            if not has_time:
                score += 0.25
        
        return min(score, 1.0)
    
    def extract_schedule_info(self, text: str) -> Dict:
        """
        从文本中提取日程信息
        
        Args:
            text: 文本内容
            
        Returns:
            包含日程信息的字典
        """
        info = {
            "date": None,
            "time": None,
            "description": text,
            "has_time_info": False
        }
        
        # 提取时间
        time_str = self._extract_time(text)
        if time_str:
            # 标准化时间格式为 HH:MM
            normalized_time = self._normalize_time(time_str)
            if normalized_time:
                info["time"] = normalized_time
                info["has_time_info"] = True
        
        # 提取日期
        date_str = self._extract_date(text)
        if date_str:
            # 标准化日期格式为 YYYY-MM-DD
            normalized_date = self._normalize_date(date_str)
            if normalized_date:
                info["date"] = normalized_date
                info["has_time_info"] = True
        
        # 提取事件描述（移除时间和日期信息）
        description = text
        for pattern in self.TIME_PATTERNS + self.DATE_PATTERNS:
            description = re.sub(pattern, '', description)
        info["description"] = description.strip() or text
        
        return info
    
    def extract_memo_info(self, text: str) -> Dict:
        """
        从文本中提取备忘录信息
        
        Args:
            text: 文本内容
            
        Returns:
            包含备忘录信息的字典
        """
        info = {
            "content": text,
            "summary": self._generate_summary(text),
            "tags": self._extract_tags(text)
        }
        
        return info
    
    def _extract_time(self, text: str) -> Optional[str]:
        """提取时间信息"""
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """提取日期信息"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _generate_summary(self, text: str, max_length: int = 100) -> str:
        """生成文本摘要"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _extract_tags(self, text: str) -> List[str]:
        """提取标签（简单实现）"""
        tags = []
        text_lower = text.lower()
        
        # 根据关键词提取标签
        if any(keyword in text_lower for keyword in ['工作', 'work', '项目', 'project']):
            tags.append('工作')
        if any(keyword in text_lower for keyword in ['学习', 'study', '课程', 'course']):
            tags.append('学习')
        if any(keyword in text_lower for keyword in ['生活', 'life', '日常']):
            tags.append('生活')
        if any(keyword in text_lower for keyword in ['想法', 'idea', '思考']):
            tags.append('想法')
        
        return tags
    
    def _normalize_time(self, time_str: str) -> Optional[str]:
        """
        标准化时间格式为 HH:MM
        
        Args:
            time_str: 原始时间字符串
            
        Returns:
            标准化的时间字符串 (HH:MM) 或 None
        """
        try:
            # 处理 14:30 或 14：30 格式
            if ':' in time_str or '：' in time_str:
                time_str = time_str.replace('：', ':')
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                return f"{hour:02d}:{minute:02d}"
            
            # 处理 14点30分 或 14点 格式
            if '点' in time_str:
                time_str = time_str.replace('分', '')
                parts = time_str.split('点')
                hour = int(re.search(r'\d+', parts[0]).group())
                minute = 0
                if len(parts) > 1 and parts[1].strip():
                    minute_match = re.search(r'\d+', parts[1])
                    if minute_match:
                        minute = int(minute_match.group())
                
                # 处理上午/下午
                if '下午' in time_str or '晚上' in time_str:
                    if hour < 12:
                        hour += 12
                elif '上午' in time_str or '早上' in time_str:
                    if hour == 12:
                        hour = 0
                
                return f"{hour:02d}:{minute:02d}"
            
            # 处理 2 pm 或 2pm 格式
            if 'pm' in time_str.lower():
                hour = int(re.search(r'\d+', time_str).group())
                if hour < 12:
                    hour += 12
                return f"{hour:02d}:00"
            
            if 'am' in time_str.lower():
                hour = int(re.search(r'\d+', time_str).group())
                if hour == 12:
                    hour = 0
                return f"{hour:02d}:00"
            
        except Exception as e:
            logging.warning(f"时间标准化失败: {time_str}, 错误: {str(e)}")
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        标准化日期格式为 YYYY-MM-DD
        
        Args:
            date_str: 原始日期字符串
            
        Returns:
            标准化的日期字符串 (YYYY-MM-DD) 或 None
        """
        try:
            from datetime import datetime, timedelta
            
            # 处理相对日期
            today = datetime.now().date()
            
            if '今天' in date_str:
                return today.strftime('%Y-%m-%d')
            elif '明天' in date_str:
                return (today + timedelta(days=1)).strftime('%Y-%m-%d')
            elif '后天' in date_str:
                return (today + timedelta(days=2)).strftime('%Y-%m-%d')
            elif '昨天' in date_str:
                return (today - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 处理 2024-01-01 或 2024/01/01 格式
            if re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', date_str):
                date_str = date_str.replace('/', '-')
                parts = date_str.split('-')
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                return f"{year:04d}-{month:02d}-{day:02d}"
            
            # 处理 2024年1月1日 格式
            if '年' in date_str and '月' in date_str:
                year_match = re.search(r'(\d{4})年', date_str)
                month_match = re.search(r'(\d{1,2})月', date_str)
                day_match = re.search(r'(\d{1,2})日', date_str)
                
                if year_match and month_match:
                    year = int(year_match.group(1))
                    month = int(month_match.group(1))
                    day = int(day_match.group(1)) if day_match else 1
                    return f"{year:04d}-{month:02d}-{day:02d}"
            
            # 处理 1-1 或 1月1日 格式（使用当前年份）
            if re.match(r'\d{1,2}[-/月]\d{1,2}', date_str):
                date_str = date_str.replace('月', '-').replace('日', '')
                parts = date_str.split('-')
                month = int(parts[0])
                day = int(parts[1]) if len(parts) > 1 else 1
                year = today.year
                return f"{year:04d}-{month:02d}-{day:02d}"
            
        except Exception as e:
            logging.warning(f"日期标准化失败: {date_str}, 错误: {str(e)}")
        
        return None
    
    def needs_manual_selection(self, confidence: float) -> bool:
        """
        判断是否需要用户手动选择分类
        
        Args:
            confidence: 分类置信度
            
        Returns:
            是否需要手动选择
        """
        return confidence < self.CONFIDENCE_THRESHOLD


# 全局分类服务实例
_classification_service: Optional[ClassificationService] = None


def get_classification_service() -> ClassificationService:
    """获取分类服务实例（单例模式）"""
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService()
    return _classification_service
