"""日程管理单元测试"""
import pytest
from datetime import date, time
from app.models.schedule import ScheduleItem
from app.services.classification_service import ClassificationService


class TestScheduleAPI:
    """测试日程API端点"""
    
    def test_create_schedule_success(self, client, sample_user_data):
        """测试成功创建日程"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == "2025-12-01"
        assert data["time"] == "14:30:00"
        assert data["description"] == "团队会议"
        assert data["original_text"] == "12月1日下午2点30分团队会议"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_schedule_missing_time_info(self, client, sample_user_data):
        """测试缺少时间信息的错误处理"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建没有时间信息的日程
        schedule_data = {
            "description": "团队会议",
            "original_text": "团队会议"
        }
        
        response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "缺少时间信息" in response.json()["detail"]
    
    def test_create_schedule_invalid_date_format(self, client, sample_user_data):
        """测试无效日期格式"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日期格式错误的日程
        schedule_data = {
            "date": "2025/12/01",  # 错误格式
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "无效的日期格式" in response.json()["detail"]
    
    def test_get_schedules_list(self, client, sample_user_data):
        """测试查询日程列表"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建多个日程
        schedules = [
            {
                "date": "2025-12-01",
                "time": "14:30",
                "description": "团队会议",
                "original_text": "12月1日下午2点30分团队会议"
            },
            {
                "date": "2025-12-02",
                "time": "10:00",
                "description": "客户拜访",
                "original_text": "12月2日上午10点客户拜访"
            }
        ]
        
        for schedule in schedules:
            client.post(
                "/api/v1/schedules",
                json=schedule,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询日程列表
        response = client.get(
            "/api/v1/schedules",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["schedules"]) == 2
        # 验证按时间排序
        assert data["schedules"][0]["date"] == "2025-12-01"
        assert data["schedules"][1]["date"] == "2025-12-02"
    
    def test_get_schedules_with_date_range(self, client, sample_user_data):
        """测试按日期范围筛选日程"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建多个日程
        schedules = [
            {
                "date": "2025-12-01",
                "time": "14:30",
                "description": "会议1",
                "original_text": "会议1"
            },
            {
                "date": "2025-12-15",
                "time": "10:00",
                "description": "会议2",
                "original_text": "会议2"
            },
            {
                "date": "2025-12-30",
                "time": "16:00",
                "description": "会议3",
                "original_text": "会议3"
            }
        ]
        
        for schedule in schedules:
            client.post(
                "/api/v1/schedules",
                json=schedule,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询特定日期范围的日程
        response = client.get(
            "/api/v1/schedules?start_date=2025-12-10&end_date=2025-12-20",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["schedules"][0]["description"] == "会议2"
    
    def test_update_schedule(self, client, sample_user_data):
        """测试更新日程"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        schedule_id = create_response.json()["id"]
        
        # 更新日程
        update_data = {
            "time": "15:00",
            "description": "团队会议（已改期）"
        }
        
        response = client.put(
            f"/api/v1/schedules/{schedule_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["time"] == "15:00:00"
        assert data["description"] == "团队会议（已改期）"
    
    def test_delete_schedule(self, client, sample_user_data):
        """测试删除日程"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        schedule_id = create_response.json()["id"]
        
        # 删除日程
        response = client.delete(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # 验证日程已删除
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404


class TestScheduleInfoExtraction:
    """测试日程信息提取逻辑"""
    
    def test_extract_schedule_with_date_and_time(self):
        """测试提取包含日期和时间的日程信息"""
        service = ClassificationService()
        text = "明天下午2点30分团队会议"
        
        info = service.extract_schedule_info(text)
        
        assert info["has_time_info"] is True
        assert info["time"] is not None
        assert info["date"] is not None
        assert "14:30" in info["time"]
    
    def test_extract_schedule_with_only_date(self):
        """测试提取只有日期的日程信息"""
        service = ClassificationService()
        text = "2025年12月1日团队会议"
        
        info = service.extract_schedule_info(text)
        
        assert info["has_time_info"] is True
        assert info["date"] is not None
        assert "2025-12-01" in info["date"]
    
    def test_extract_schedule_with_only_time(self):
        """测试提取只有时间的日程信息"""
        service = ClassificationService()
        text = "下午3点开会"
        
        info = service.extract_schedule_info(text)
        
        assert info["has_time_info"] is True
        assert info["time"] is not None
        assert "15:00" in info["time"]
    
    def test_extract_schedule_without_time_info(self):
        """测试提取没有时间信息的文本"""
        service = ClassificationService()
        text = "记得准备会议材料"
        
        info = service.extract_schedule_info(text)
        
        assert info["has_time_info"] is False
        assert info["date"] is None
        assert info["time"] is None
    
    def test_normalize_various_time_formats(self):
        """测试各种时间格式的标准化"""
        service = ClassificationService()
        
        test_cases = [
            ("14:30", "14:30"),
            ("14点30分", "14:30"),
            ("下午2点30分", "14:30"),
            ("上午10点", "10:00"),
            ("2 pm", "14:00"),
            ("10 am", "10:00"),
        ]
        
        for input_time, expected in test_cases:
            result = service._normalize_time(input_time)
            assert result == expected, f"Failed for {input_time}: got {result}, expected {expected}"
    
    def test_normalize_various_date_formats(self):
        """测试各种日期格式的标准化"""
        service = ClassificationService()
        
        test_cases = [
            ("2025-12-01", "2025-12-01"),
            ("2025年12月1日", "2025-12-01"),
        ]
        
        for input_date, expected in test_cases:
            result = service._normalize_date(input_date)
            assert result == expected, f"Failed for {input_date}: got {result}, expected {expected}"


class TestScheduleDataPersistence:
    """测试日程数据持久化"""
    
    def test_schedule_persists_after_creation(self, client, sample_user_data):
        """测试日程创建后能够持久化"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        create_response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        schedule_id = create_response.json()["id"]
        
        # 查询日程验证持久化
        get_response = client.get(
            f"/api/v1/schedules/{schedule_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == schedule_id
        assert data["date"] == "2025-12-01"
        assert data["time"] == "14:30:00"
        assert data["description"] == "团队会议"
        assert data["original_text"] == "12月1日下午2点30分团队会议"
    
    def test_schedule_contains_all_required_fields(self, client, sample_user_data):
        """测试日程包含所有必需字段"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建日程
        schedule_data = {
            "date": "2025-12-01",
            "time": "14:30",
            "description": "团队会议",
            "original_text": "12月1日下午2点30分团队会议"
        }
        
        response = client.post(
            "/api/v1/schedules",
            json=schedule_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        
        # 验证所有必需字段都存在
        required_fields = ["id", "user_id", "date", "time", "description", "original_text", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
