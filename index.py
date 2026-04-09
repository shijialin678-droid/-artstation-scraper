from http.server import BaseHTTPRequestHandler
import json
import requests
import re
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        path = self.path
        
        # 路由
        if path.startswith('/api/search'):
            self.handle_search()
        elif path.startswith('/api/profile'):
            self.handle_profile()
        elif path == '/api/daily':
            self.handle_daily()
        elif path == '/api/health':
            self.handle_health()
        else:
            self.handle_index()
    
    def handle_search(self):
        """搜索候选人"""
        import urllib.parse
        
        # 解析参数
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        specialty = params.get('specialty', ['角色原画'])[0]
        limit = int(params.get('limit', ['10'])[0])
        
        # 搜索逻辑
        candidates = self._search_artstation(specialty, limit)
        
        self._send_json({
            "success": True,
            "data": candidates,
            "total": len(candidates),
            "specialty": specialty,
            "timestamp": datetime.now().isoformat()
        })
    
    def handle_profile(self):
        """获取候选人详情"""
        import urllib.parse
        
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        username = params.get('username', [''])[0]
        
        if not username:
            self._send_json({"success": False, "error": "缺少username参数"}, 400)
            return
        
        profile = self._get_profile(username)
        
        self._send_json({
            "success": True,
            "data": profile
        })
    
    def handle_daily(self):
        """每日抓取"""
        all_candidates = []
        
        # 抓取各个方向
        specialties = [
            ("角色原画", 10),
            ("场景原画", 10),
            ("美宣原画", 5)
        ]
        
        for specialty, count in specialties:
            candidates = self._search_artstation(specialty, count)
            all_candidates.extend(candidates)
        
        self._send_json({
            "success": True,
            "data": all_candidates,
            "total": len(all_candidates),
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    
    def handle_health(self):
        """健康检查"""
        self._send_json({
            "status": "ok",
            "service": "artstation-scraper",
            "timestamp": datetime.now().isoformat()
        })
    
    def handle_index(self):
        """首页"""
        self._send_json({
            "service": "ArtStation Scraper API",
            "version": "1.0.0",
            "endpoints": [
                "/api/search?specialty=角色原画&limit=10",
                "/api/profile?username=xxx",
                "/api/daily",
                "/api/health"
            ]
        })
    
    def _search_artstation(self, specialty, limit):
        """搜索ArtStation"""
        # 关键词映射
        keywords_map = {
            "角色原画": "character concept art",
            "场景原画": "environment concept art",
            "美宣原画": "key visual illustration",
            "动画师": "game animation"
        }
        
        keyword = keywords_map.get(specialty, specialty)
        
        try:
            # 调用ArtStation搜索API
            url = f"https://www.artstation.com/api/v2/search/users.json"
            params = {
                'q': keyword,
                'page': 1,
                'per_page': limit
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            candidates = []
            for user in data.get('data', []):
                candidates.append({
                    "name": user.get('full_name', user.get('username')),
                    "username": user.get('username'),
                    "profile_url": f"https://www.artstation.com/{user.get('username')}",
                    "location": user.get('location', ''),
                    "artwork_count": user.get('artwork_count', 0),
                    "specialty": specialty
                })
            
            return candidates
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_profile(self, username):
        """获取用户详情"""
        try:
            url = f"https://www.artstation.com/users/{username}/projects.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()
            
            return {
                "username": username,
                "projects": len(data.get('data', [])),
                "url": f"https://www.artstation.com/{username}"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _send_json(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
