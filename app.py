from flask import Flask, request, render_template_string, jsonify
import yt_dlp, os, re
from urllib.parse import quote, unquote
import threading

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN', '8098351153:AAHddeFz1_sdVQCo7s2zje4og16vHJYM4JI')

PROFESSIONAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free YouTube Video Downloader - Fast & HD Downloads</title>
    <meta name="description" content="Download YouTube videos in HD 1080p, 720p, MP4, MP3. Fast, free, no ads. Instagram, TikTok, Facebook supported.">
    <meta name="keywords" content="youtube downloader, video downloader, mp3 converter, instagram downloader, tiktok downloader">
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f23; color: white; line-height: 1.6; overflow-x: hidden;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { 
            text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        h1 { font-size: 3rem; font-weight: 800; margin-bottom: 1rem; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; }
        .download-box { 
            background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); 
            border-radius: 20px; padding: 3rem; margin: 3rem 0; border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .url-input { 
            width: 100%; padding: 1.5rem 2rem; font-size: 1.1rem; 
            border: none; border-radius: 15px; background: rgba(255,255,255,0.1);
            color: white; outline: none; margin-bottom: 1.5rem;
        }
        .url-input::placeholder { color: rgba(255,255,255,0.7); }
        .download-btn { 
            background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 1.2rem 3rem;
            border: none; border-radius: 50px; color: white; font-size: 1.2rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s; width: 100%; margin-bottom: 1rem;
        }
        .download-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(255,107,107,0.4); }
        .loading { display: none; text-align: center; padding: 2rem; }
        .spinner { border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .results { display: none; }
        .video-info { text-align: center; margin-bottom: 2rem; }
        .video-info h3 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .video-info p { opacity: 0.8; }
        .format-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
        .format-btn { 
            background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); 
            border-radius: 15px; padding: 1.5rem; text-align: center; cursor: pointer;
            transition: all 0.3s; backdrop-filter: blur(10px);
        }
        .format-btn:hover { background: rgba(255,255,255,0.2); transform: translateY(-5px); }
        .quality-badge { background: #4ecdc4; color: #0f0f23; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem; font-weight: 600; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin: 4rem 0; }
        .feature { text-align: center; }
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        @media (max-width: 768px) { h1 { font-size: 2rem; } .download-box { padding: 2rem 1.5rem; } }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎥 Video Downloader</h1>
            <p class="subtitle">Download YouTube, Instagram, TikTok & Facebook videos in HD quality. Fast & Free.</p>
        </header>

        <div class="download-box">
            <input type="url" id="urlInput" class="url-input" placeholder="Paste YouTube, Instagram, TikTok or Facebook link here...">
            <button onclick="analyzeVideo()" class="download-btn">🔍 Analyze Video</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing video... Please wait</p>
            </div>
            
            <div class="results" id="results">
                <div class="video-info" id="videoInfo"></div>
                <div class="format-grid" id="formatGrid"></div>
            </div>
        </div>

        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>Lightning Fast</h3>
                <p>Downloads start instantly. No waiting, no buffering.</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🎨</div>
                <h3>HD Quality</h3>
                <p>Up to 1080p video & high quality audio extraction.</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🛡️</div>
                <h3>Safe & Clean</h3>
                <p>No malware, no ads, no registration required.</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📱</div>
                <h3>Mobile Ready</h3>
                <p>Works perfectly on phones, tablets & desktop.</p>
            </div>
        </div>
    </div>

    <script>
        async function analyzeVideo() {
            const url = document.getElementById('urlInput').value;
            if (!url) return alert('Please paste a video link');
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                
                if (data.success) {
                    showResults(data.video_info);
                } else {
                    alert('Invalid URL or video not supported');
                }
            } catch(e) {
                alert('Error processing video. Please try again.');
            }
            
            document.getElementById('loading').style.display = 'none';
        }
        
        function showResults(info) {
            document.getElementById('videoInfo').innerHTML = `
                <h3>${info.title}</h3>
                <p>${info.duration} • ${info.platform}</p>
            `;
            
            let formats = '';
            if (info.video720) formats += `<div class="format-btn" onclick="download('${info.video720}')"><div class="quality-badge">HD 720p</div>Video (MP4)</div>`;
            if (info.video1080) formats += `<div class="format-btn" onclick="download('${info.video1080}')"><div class="quality-badge">Full HD</div>Video (MP4)</div>`;
            if (info.audio) formats += `<div class="format-btn" onclick="download('${info.audio}')"><div class="quality-badge">MP3</div>Audio Only</div>`;
            
            document.getElementById('formatGrid').innerHTML = formats;
            document.getElementById('results').style.display = 'block';
        }
        
        function download(url) {
            window.open(url, '_blank');
        }
        
        // Enter key support
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') analyzeVideo();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(PROFESSIONAL_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url', '')
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            video720, video1080, audio = None, None, None
            
            # Find best formats
            for f in formats:
                height = f.get('height')
                if height == 720 and f.get('vcodec') != 'none':
                    video720 = f['url']
                elif height == 1080 and f.get('vcodec') != 'none':
                    video1080 = f['url']
                elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio = f['url']
            
            return jsonify({
                'success': True,
                'video_info': {
                    'title': info.get('title', 'Unknown'),
                    'duration': f"{int(info.get('duration', 0)//60)}:{int(info.get('duration', 0)%60):02d}",
                    'platform': info.get('uploader', 'YouTube'),
                    'video720': video720,
                    'video1080': video1080,
                    'audio': audio
                }
            })
    except:
        return jsonify({'success': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
