# ArtStation Scraper API

部署在Vercel的免费数据采集服务

## API端点

### 1. 搜索候选人
```
GET /api/search?specialty=角色原画&limit=10
```

参数：
- `specialty`: 专业方向（角色原画/场景原画/美宣原画/动画师）
- `limit`: 返回数量（默认10，最大50）

返回：
```json
{
  "success": true,
  "data": [
    {
      "name": "艺术家姓名",
      "username": "artstation用户名",
      "profile_url": "https://www.artstation.com/username",
      "location": "地区",
      "artwork_count": 20,
      "specialty": "角色原画"
    }
  ],
  "total": 10
}
```

### 2. 获取候选人详情
```
GET /api/profile?username=xxx
```

### 3. 每日自动抓取
```
GET /api/daily
```

返回当天抓取的候选人列表

### 4. 健康检查
```
GET /api/health
```

## 部署方法

1. Fork本仓库到GitHub
2. 在Vercel导入项目
3. 自动部署完成

## 免费额度

- 每月100GB带宽
- 每月10万次请求
- 完全够用
