# 实施计划

- [x] 1. 搭建项目基础架构
  - 创建前端Vue项目（使用Vite）和后端FastAPI项目
  - 配置Tailwind CSS和基础样式
  - 设置SQLAlchemy和SQLite数据库连接
  - 配置开发环境和依赖管理
  - 配置测试框架（pytest、hypothesis）
  - 创建测试目录结构和基础测试配置
  - _Requirements: 8.1_

- [x] 1.1 编写数据模型的单元测试


  - 测试User模型创建和字段验证
  - 测试ScheduleItem模型创建和关联
  - 测试Memo模型创建和标签存储
  - _Requirements: 4.2, 5.2_

- [x] 2. 实现用户认证系统



  - 创建User数据模型
  - 实现用户注册API（密码加密存储）
  - 实现用户登录API（JWT token生成）
  - 实现认证中间件
  - _Requirements: 10.1, 10.2_

- [x] 2.1 编写用户认证的单元测试


  - 测试用户注册API端点
  - 测试用户登录API端点
  - 测试JWT token生成和验证
  - 测试认证中间件功能
  - _Requirements: 10.1, 10.2_

- [x] 2.2 编写用户认证的属性测试


  - **Property 28: 密码加密存储**
  - **Validates: Requirements 10.1**

- [x] 2.3 编写访问权限验证的属性测试


  - **Property 29: 访问权限验证**
  - **Validates: Requirements 10.2**

- [x] 3. 实现文件上传和输入功能




  - 创建前端输入组件（文本输入框、文件上传、拍照按钮）
  - 实现文件格式和大小验证
  - 创建文件上传API端点





  - 实现文件存储逻辑
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_


- [ ] 3.1 编写文件上传的单元测试
  - 测试文件上传API端点
  - 测试文件格式验证逻辑
  - 测试文件大小限制
  - 测试文件存储功能




  - _Requirements: 1.1, 1.4, 1.5, 1.6_




- [x] 3.2 编写文件处理的属性测试


  - **Property 1: 图片传递到OCR引擎**
  - **Validates: Requirements 1.1, 1.2**



- [x] 3.3 编写文本输入的属性测试



  - **Property 2: 文本输入接收**
  - **Validates: Requirements 1.3**


- [ ] 3.4 编写文件格式验证的属性测试
  - **Property 3: 不支持格式拒绝**




  - **Validates: Requirements 1.4**

- [ ] 3.5 编写支持格式的属性测试
  - **Property 4: 支持格式接受**


  - **Validates: Requirements 1.6**


- [x] 4. 集成PaddleOCR引擎



  - 安装和配置PaddleOCR-VL
  - 创建OCRService类
  - 实现图片文字识别功能
  - 实现多语言支持（中英文）
  - 创建OCR识别API端点

  - _Requirements: 2.1, 2.2, 2.3_

- [x] 4.1 编写OCR服务的单元测试

  - 测试OCRService类初始化
  - 测试图片验证功能
  - 测试OCR识别API端点
  - 测试错误处理（无法识别文本的情况）
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 4.2 编写OCR文本提取的属性测试


  - **Property 5: OCR文本提取**
  - **Validates: Requirements 2.1**

- [ ] 4.3 编写多语言识别的属性测试
  - **Property 6: 多语言识别**
  - **Validates: Requirements 2.2**

- [ ] 5. 实现OCR结果预览和编辑
  - 创建OCR预览组件
  - 实现识别结果返回API
  - 实现前端编辑功能
  - _Requirements: 2.4, 2.5_

- [ ] 5.1 编写OCR结果返回的属性测试
  - **Property 7: OCR结果返回**
  - **Validates: Requirements 2.4**

- [ ] 5.2 编写OCR结果编辑的属性测试
  - **Property 8: OCR结果可编辑**
  - **Validates: Requirements 2.5**

- [ ] 6. 实现AI分类服务
  - 配置Parallax模型部署
  - 创建ClassificationService类
  - 实现文本分类逻辑（日程/备忘录）
  - 创建分类API端点
  - 实现分类置信度判断和手动选择提示
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6.1 编写AI分类服务的单元测试
  - 测试ClassificationService类
  - 测试文本分类API端点
  - 测试置信度判断逻辑
  - 测试日程信息提取功能
  - 测试备忘录信息提取功能
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6.2 编写文本分类的属性测试
  - **Property 9: 文本分类**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [ ] 7. 实现日程信息提取和存储
  - 创建ScheduleItem数据模型
  - 实现日程信息提取逻辑（时间、日期、事件描述）
  - 创建日程创建API
  - 实现缺少时间信息的提示
  - _Requirements: 4.1, 4.2, 4.4_

- [ ] 7.1 编写日程管理的单元测试
  - 测试日程创建API
  - 测试日程信息提取逻辑
  - 测试缺少时间信息的错误处理
  - 测试日程数据持久化
  - _Requirements: 4.1, 4.2, 4.4_

- [ ] 7.2 编写日程信息提取的属性测试
  - **Property 10: 日程信息提取**
  - **Validates: Requirements 4.1**

- [ ] 7.3 编写存储完整性的属性测试
  - **Property 11: 归档内容存储完整性**
  - **Validates: Requirements 4.2, 5.2**

- [ ] 8. 实现日程查看和筛选功能
  - 创建日程列表组件
  - 实现日程查询API（按时间排序）
  - 实现日期范围筛选功能
  - _Requirements: 4.3, 4.5_

- [ ] 8.1 编写日程查询的单元测试
  - 测试日程查询API
  - 测试时间排序功能
  - 测试日期范围筛选
  - 测试空结果处理
  - _Requirements: 4.3, 4.5_

- [ ] 8.2 编写日程排序的属性测试
  - **Property 12: 日程时间排序**
  - **Validates: Requirements 4.3**

- [ ] 8.3 编写日期筛选的属性测试
  - **Property 13: 日期范围筛选**
  - **Validates: Requirements 4.5**

- [ ] 9. 实现备忘录信息提取和存储
  - 创建Memo数据模型
  - 实现备忘录信息提取逻辑（创建时间、摘要）
  - 创建备忘录创建API
  - 实现标签功能
  - _Requirements: 5.1, 5.2, 5.4_

- [ ] 9.1 编写备忘录管理的单元测试
  - 测试备忘录创建API
  - 测试备忘录信息提取逻辑
  - 测试标签功能
  - 测试备忘录数据持久化
  - _Requirements: 5.1, 5.2, 5.4_

- [ ] 9.2 编写备忘录信息提取的属性测试
  - **Property 14: 备忘录信息提取**
  - **Validates: Requirements 5.1**

- [ ] 9.3 编写备忘录标签的属性测试
  - **Property 16: 备忘录标签保存**
  - **Validates: Requirements 5.4**

- [ ] 10. 实现备忘录查看和筛选功能
  - 创建备忘录列表组件
  - 实现备忘录查询API（按时间倒序）
  - 实现标签筛选功能
  - _Requirements: 5.3, 5.5_

- [ ] 10.1 编写备忘录查询的单元测试
  - 测试备忘录查询API
  - 测试时间倒序排序
  - 测试标签筛选功能
  - 测试空结果处理
  - _Requirements: 5.3, 5.5_

- [ ] 10.2 编写备忘录排序的属性测试
  - **Property 15: 备忘录时间倒序**
  - **Validates: Requirements 5.3**

- [ ] 10.3 编写标签筛选的属性测试
  - **Property 17: 标签筛选**
  - **Validates: Requirements 5.5**

- [ ] 11. 实现跨端数据同步
  - 实现用户数据查询API
  - 实现数据立即持久化
  - 添加前端数据刷新机制
  - 实现离线缓存（可选）
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 11.1 编写用户数据访问的属性测试
  - **Property 18: 用户数据访问**
  - **Validates: Requirements 6.1**

- [ ] 11.2 编写数据同步一致性的属性测试
  - **Property 19: 数据同步一致性**
  - **Validates: Requirements 6.2, 6.3**

- [ ] 11.3 编写数据隔离的属性测试
  - **Property 30: 数据隔离**
  - **Validates: Requirements 10.4**

- [ ] 12. 实现搜索功能
  - 创建搜索组件
  - 实现全文搜索API
  - 实现模糊搜索和精确搜索模式
  - 实现搜索结果相关度排序
  - 实现多字段搜索（日程和备忘录）
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 12.1 编写搜索功能的单元测试
  - 测试搜索API端点
  - 测试模糊搜索和精确搜索
  - 测试多字段搜索
  - 测试空搜索结果处理
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 12.2 编写关键词搜索的属性测试
  - **Property 20: 关键词搜索**
  - **Validates: Requirements 7.1**

- [ ] 12.3 编写搜索排序的属性测试
  - **Property 21: 搜索结果排序**
  - **Validates: Requirements 7.2**

- [ ] 12.4 编写全字段搜索的属性测试
  - **Property 22: 全字段搜索**
  - **Validates: Requirements 7.3, 7.4**

- [ ] 12.5 编写搜索模式的属性测试
  - **Property 23: 搜索模式支持**
  - **Validates: Requirements 7.5**

- [ ] 13. 实现模型注册中心
  - 创建ModelRegistry类
  - 实现模型配置文件加载
  - 实现动态模型注册
  - 实现任务类型到模型的映射
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 13.1 编写模型注册中心的单元测试
  - 测试ModelRegistry类初始化
  - 测试模型注册功能
  - 测试模型获取功能
  - 测试配置文件加载
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 13.2 编写模型动态注册的属性测试
  - **Property 24: 模型动态注册**
  - **Validates: Requirements 9.2**

- [ ] 13.3 编写任务模型选择的属性测试
  - **Property 25: 任务模型选择**
  - **Validates: Requirements 9.3**

- [ ] 14. 实现模型监控和容错
  - 创建ModelMetrics数据模型
  - 实现模型调用监控
  - 实现模型失败重试和备用模型切换
  - 创建模型性能查询API
  - _Requirements: 9.4, 9.5_

- [ ] 14.1 编写模型监控的单元测试
  - 测试ModelMetrics数据模型
  - 测试模型调用监控功能
  - 测试模型性能查询API
  - 测试备用模型切换逻辑
  - _Requirements: 9.4, 9.5_

- [ ] 14.2 编写模型监控的属性测试
  - **Property 26: 模型调用监控**
  - **Validates: Requirements 9.4**

- [ ] 14.3 编写模型容错的属性测试
  - **Property 27: 模型容错切换**
  - **Validates: Requirements 9.5**

- [ ] 15. 实现数据删除功能
  - 实现日程删除API
  - 实现备忘录删除API
  - 确保数据永久删除
  - _Requirements: 10.5_

- [ ] 15.1 编写数据删除的单元测试
  - 测试日程删除API
  - 测试备忘录删除API
  - 测试删除后数据不可恢复
  - 测试删除权限验证
  - _Requirements: 10.5_

- [ ] 15.2 编写数据删除的属性测试
  - **Property 31: 数据永久删除**
  - **Validates: Requirements 10.5**

- [ ] 16. 完善UI和响应式设计
  - 使用Tailwind CSS优化界面布局
  - 实现移动端适配
  - 添加加载指示器
  - 优化视觉层次和用户体验
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 17. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

- [ ] 18. 编写部署文档和配置
  - 创建数据库迁移脚本
  - 编写环境配置说明
  - 创建Docker配置（可选）
  - 编写README和使用文档
