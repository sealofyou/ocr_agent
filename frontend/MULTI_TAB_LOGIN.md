# 多标签页登录说明

## 当前行为（默认）

**使用 localStorage（默认设置）**
- ✅ 所有标签页共享同一个登录状态
- ✅ 在一个标签页登录后，其他标签页自动登录
- ✅ 刷新页面后仍保持登录状态
- ❌ 无法在同一浏览器的不同标签页中登录不同账号

## 如何启用多标签页独立登录

### 方法1：修改配置（推荐用于开发测试）

编辑 `frontend/src/stores/auth.ts`：

```typescript
// 将这一行改为 true
const USE_SESSION_STORAGE = true
```

**效果：**
- ✅ 每个标签页可以独立登录不同账号
- ✅ 标签页1：用户A
- ✅ 标签页2：用户B
- ✅ 标签页3：用户C
- ❌ 刷新页面后需要重新登录（sessionStorage在标签页关闭后清除）

### 方法2：使用不同浏览器（推荐用于生产环境）

不修改代码，使用不同的浏览器或浏览器模式：

1. **Chrome 正常模式** - 登录用户A
2. **Chrome 隐私模式** - 登录用户B
3. **Firefox** - 登录用户C
4. **Edge** - 登录用户D

## 对比

| 特性 | localStorage（默认） | sessionStorage |
|------|---------------------|----------------|
| 多标签页独立登录 | ❌ | ✅ |
| 刷新后保持登录 | ✅ | ❌ |
| 关闭标签页后保持登录 | ✅ | ❌ |
| 适用场景 | 生产环境 | 开发测试 |

## 使用场景

### 场景1：普通用户（推荐 localStorage）
- 用户只需要登录一个账号
- 希望刷新页面后仍保持登录
- 所有标签页使用同一账号

**配置：**
```typescript
const USE_SESSION_STORAGE = false // 默认
```

### 场景2：开发测试（推荐 sessionStorage）
- 需要同时测试多个账号
- 在不同标签页中登录不同用户
- 测试用户数据隔离

**配置：**
```typescript
const USE_SESSION_STORAGE = true
```

### 场景3：演示/培训
- 需要展示多用户功能
- 使用不同浏览器或隐私模式
- 保持默认配置

**配置：**
```typescript
const USE_SESSION_STORAGE = false // 默认
```

## 如何切换

### 启用多标签页独立登录

1. 打开 `frontend/src/stores/auth.ts`
2. 找到这一行：
   ```typescript
   const USE_SESSION_STORAGE = false
   ```
3. 改为：
   ```typescript
   const USE_SESSION_STORAGE = true
   ```
4. 保存文件
5. 刷新浏览器（Vite会自动热重载）

### 恢复默认行为

1. 打开 `frontend/src/stores/auth.ts`
2. 改回：
   ```typescript
   const USE_SESSION_STORAGE = false
   ```
3. 保存文件
4. 刷新浏览器

## 技术说明

### localStorage
- 数据存储在浏览器中，永久保存（除非手动清除）
- 同一域名下的所有标签页共享数据
- 关闭浏览器后数据仍然存在

### sessionStorage
- 数据存储在浏览器中，仅在当前标签页有效
- 每个标签页有独立的存储空间
- 关闭标签页后数据自动清除
- 刷新页面数据仍然存在

## 常见问题

### Q: 为什么我在标签页1登录后，标签页2也自动登录了？
A: 这是默认行为（使用localStorage）。如果需要独立登录，请启用sessionStorage。

### Q: 我启用了sessionStorage，为什么刷新后需要重新登录？
A: sessionStorage的数据在刷新后仍然存在，但如果您清除了缓存或使用了硬刷新（Ctrl+Shift+R），数据会被清除。

### Q: 生产环境应该用哪个？
A: 推荐使用localStorage（默认），这样用户体验更好。如果需要多账号，建议用户使用不同浏览器。

### Q: 可以让用户自己选择吗？
A: 可以，但需要额外的开发工作。当前实现是全局配置。

## 推荐配置

**开发环境：**
```typescript
const USE_SESSION_STORAGE = true  // 方便测试多用户
```

**生产环境：**
```typescript
const USE_SESSION_STORAGE = false  // 更好的用户体验
```

## 测试多用户功能

### 使用 sessionStorage（推荐）
1. 启用 `USE_SESSION_STORAGE = true`
2. 打开标签页1，登录用户A
3. 打开标签页2，登录用户B
4. 在两个标签页中分别操作

### 使用不同浏览器
1. 保持默认配置
2. Chrome：登录用户A
3. Firefox：登录用户B
4. 在两个浏览器中分别操作

### 使用隐私模式
1. 保持默认配置
2. 正常模式：登录用户A
3. 隐私模式（Ctrl+Shift+N）：登录用户B
4. 在两个窗口中分别操作
