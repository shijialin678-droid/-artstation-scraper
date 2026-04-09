import json
import requests
from datetime import datetime

def handler(event, context):
    """Netlify Function Handler"""
    
    path = event.get('path', '/')
    query_params = event.get('queryStringParameters', {}) or {}
    
    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'ok', 'service': 'artstation-scraper'})
        }
    
    elif path.startswith('/api/search'):
        return handle_search(query_params)
    
    elif path == '/api/daily':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Daily scraping endpoint',
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        }
    
    else:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'service': 'ArtStation Scraper API',
                'version': '1.0.0',
                'endpoints': [
                    '/api/health',
                    '/api/search?specialty=角色原画&limit=10',
                    '/api/daily'
                ]
            })
        }

def handle_search(query_params):
    """搜索候选人"""
    specialty = query_params.get('specialty', '角色原画')
    limit = int(query_params.get('limit', '10'))
    
    keywords = {
        '角色原画': 'character concept art',
        '场景原画': 'environment concept art',
        '美宣原画': 'key visual illustration',
        '动画师': 'game animation'
    }
    keyword = keywords.get(specialty, specialty)
    
    try:
        url = 'https://www.artstation.com/api/v2/search/users.json'
        response = requests.get(
            url,
            params={'q': keyword, 'page': 1, 'per_page': limit},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=30
        )
        data = response.json()
        
        candidates = []
        for user in data.get('data', []):
            candidates.append({
                'name': user.get('full_name', user.get('username')),
                'username': user.get('username'),
                'profile_url': f"https://www.artstation.com/{user.get('username')}",
                'location': user.get('location', ''),
                'artwork_count': user.get('artwork_count', 0),
                'specialty': specialty
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'data': candidates,
                'total': len(candidates),
                'specialty': specialty
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'success': False, 'error': str(e)})
        }

