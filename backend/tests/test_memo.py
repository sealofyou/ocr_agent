"""备忘录管理单元测试"""
import pytest
from app.services.classification_service import ClassificationService


class TestMemoAPI:
    """测试备忘录API端点"""
    
    def test_create_memo_success(self, client, sample_user_data):
        """测试成功创建备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": "今天学习了Python的异步编程，理解了async/await的工作原理",
            "summary": "学习Python异步编程",
            "tags": ["学习", "Python"]
        }
        
        response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == memo_data["content"]
        assert data["summary"] == memo_data["summary"]
        assert "学习" in data["tags"]
        assert "Python" in data["tags"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_memo_auto_generate_summary(self, client, sample_user_data):
        """测试自动生成摘要"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录（不提供摘要）
        memo_data = {
            "content": "这是一段很长的内容" * 20,  # 超过100字符
            "tags": ["测试"]
        }
        
        response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["summary"] is not None
        assert len(data["summary"]) <= 103  # 100 + "..."
        assert data["summary"].endswith("...")
    
    def test_create_memo_without_tags(self, client, sample_user_data):
        """测试创建没有标签的备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录（不提供标签）
        memo_data = {
            "content": "简单的备忘录内容"
        }
        
        response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == memo_data["content"]
        assert data["tags"] is None or data["tags"] == ""
    
    def test_get_memos_list(self, client, sample_user_data):
        """测试查询备忘录列表"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建多个备忘录
        memos = [
            {
                "content": "第一条备忘录",
                "summary": "备忘录1",
                "tags": ["工作"]
            },
            {
                "content": "第二条备忘录",
                "summary": "备忘录2",
                "tags": ["学习"]
            }
        ]
        
        for memo in memos:
            client.post(
                "/api/v1/memos",
                json=memo,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询备忘录列表
        response = client.get(
            "/api/v1/memos",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["memos"]) == 2
        # 验证按创建时间倒序排序（最新的在前）
        assert data["memos"][0]["summary"] == "备忘录2"
        assert data["memos"][1]["summary"] == "备忘录1"
    
    def test_get_memos_with_tag_filter(self, client, sample_user_data):
        """测试按标签筛选备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建多个备忘录
        memos = [
            {
                "content": "工作相关的备忘录",
                "summary": "工作备忘",
                "tags": ["工作", "项目"]
            },
            {
                "content": "学习相关的备忘录",
                "summary": "学习备忘",
                "tags": ["学习", "Python"]
            },
            {
                "content": "生活相关的备忘录",
                "summary": "生活备忘",
                "tags": ["生活"]
            }
        ]
        
        for memo in memos:
            client.post(
                "/api/v1/memos",
                json=memo,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询带有"学习"标签的备忘录
        response = client.get(
            "/api/v1/memos?tags=学习",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["memos"][0]["summary"] == "学习备忘"
    
    def test_get_memos_with_multiple_tag_filter(self, client, sample_user_data):
        """测试使用多个标签筛选备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建多个备忘录
        memos = [
            {
                "content": "工作相关的备忘录",
                "summary": "工作备忘",
                "tags": ["工作", "项目"]
            },
            {
                "content": "学习相关的备忘录",
                "summary": "学习备忘",
                "tags": ["学习", "Python"]
            },
            {
                "content": "生活相关的备忘录",
                "summary": "生活备忘",
                "tags": ["生活"]
            }
        ]
        
        for memo in memos:
            client.post(
                "/api/v1/memos",
                json=memo,
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # 查询带有"工作"或"学习"标签的备忘录
        response = client.get(
            "/api/v1/memos?tags=工作,学习",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
    
    def test_update_memo(self, client, sample_user_data):
        """测试更新备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": "原始内容",
            "summary": "原始摘要",
            "tags": ["原始标签"]
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        memo_id = create_response.json()["id"]
        
        # 更新备忘录
        update_data = {
            "content": "更新后的内容",
            "tags": ["新标签"]
        }
        
        response = client.put(
            f"/api/v1/memos/{memo_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "更新后的内容"
        assert "新标签" in data["tags"]
        # 摘要应该自动重新生成
        assert data["summary"] == "更新后的内容"
    
    def test_delete_memo(self, client, sample_user_data):
        """测试删除备忘录"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": "要删除的备忘录",
            "summary": "删除测试"
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        memo_id = create_response.json()["id"]
        
        # 删除备忘录
        response = client.delete(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # 验证备忘录已删除
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404


class TestMemoInfoExtraction:
    """测试备忘录信息提取逻辑"""
    
    def test_extract_memo_info(self):
        """测试提取备忘录信息"""
        service = ClassificationService()
        text = "今天学习了Python的异步编程，理解了async/await的工作原理"
        
        info = service.extract_memo_info(text)
        
        assert "content" in info
        assert "summary" in info
        assert "tags" in info
        assert info["content"] == text
        assert info["summary"] is not None
    
    def test_generate_summary_short_text(self):
        """测试短文本摘要生成"""
        service = ClassificationService()
        text = "这是一段短文本"
        
        summary = service._generate_summary(text)
        
        assert summary == text
    
    def test_generate_summary_long_text(self):
        """测试长文本摘要生成"""
        service = ClassificationService()
        text = "这是一段很长的文本" * 20  # 超过100字符
        
        summary = service._generate_summary(text, max_length=100)
        
        assert len(summary) <= 103  # 100 + "..."
        assert summary.endswith("...")
    
    def test_extract_tags_work_related(self):
        """测试提取工作相关标签"""
        service = ClassificationService()
        text = "今天完成了项目的工作任务"
        
        tags = service._extract_tags(text)
        
        assert "工作" in tags
    
    def test_extract_tags_study_related(self):
        """测试提取学习相关标签"""
        service = ClassificationService()
        text = "今天学习了新的课程内容"
        
        tags = service._extract_tags(text)
        
        assert "学习" in tags
    
    def test_extract_tags_life_related(self):
        """测试提取生活相关标签"""
        service = ClassificationService()
        text = "今天的日常生活很充实"
        
        tags = service._extract_tags(text)
        
        assert "生活" in tags
    
    def test_extract_tags_idea_related(self):
        """测试提取想法相关标签"""
        service = ClassificationService()
        text = "我有一个新的想法和思考"
        
        tags = service._extract_tags(text)
        
        assert "想法" in tags


class TestMemoDataPersistence:
    """测试备忘录数据持久化"""
    
    def test_memo_persists_after_creation(self, client, sample_user_data):
        """测试备忘录创建后能够持久化"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": "测试持久化的备忘录内容",
            "summary": "持久化测试",
            "tags": ["测试"]
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        memo_id = create_response.json()["id"]
        
        # 查询备忘录验证持久化
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == memo_id
        assert data["content"] == memo_data["content"]
        assert data["summary"] == memo_data["summary"]
        assert "测试" in data["tags"]
    
    def test_memo_contains_all_required_fields(self, client, sample_user_data):
        """测试备忘录包含所有必需字段"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建备忘录
        memo_data = {
            "content": "完整字段测试",
            "summary": "字段测试",
            "tags": ["测试"]
        }
        
        response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        
        # 验证所有必需字段都存在
        required_fields = ["id", "user_id", "content", "summary", "tags", "created_at", "updated_at"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_memo_tags_saved_correctly(self, client, sample_user_data):
        """测试备忘录标签正确保存"""
        # 注册并登录用户
        client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        })
        token = login_response.json()["token"]
        
        # 创建带有多个标签的备忘录
        memo_data = {
            "content": "标签测试内容",
            "summary": "标签测试",
            "tags": ["标签1", "标签2", "标签3"]
        }
        
        create_response = client.post(
            "/api/v1/memos",
            json=memo_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        memo_id = create_response.json()["id"]
        
        # 查询备忘录验证标签
        get_response = client.get(
            f"/api/v1/memos/{memo_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = get_response.json()
        assert "标签1" in data["tags"]
        assert "标签2" in data["tags"]
        assert "标签3" in data["tags"]
