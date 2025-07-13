<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工程週報生成器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        .header {
            margin-bottom: 30px;
        }

        .title {
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 16px;
            color: #718096;
            line-height: 1.5;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }

        .form-label {
            display: block;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 8px;
        }

        .form-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f7fafc;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            background: #fff;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .date-range {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .trigger-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 20px;
            position: relative;
            overflow: hidden;
        }

        .trigger-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .trigger-btn:active {
            transform: translateY(0);
        }

        .trigger-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            margin-top: 20px;
        }

        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result {
            margin-top: 25px;
            padding: 20px;
            border-radius: 12px;
            font-weight: 500;
            display: none;
        }

        .result.success {
            background: #f0fff4;
            color: #38a169;
            border: 2px solid #9ae6b4;
        }

        .result.error {
            background: #fed7d7;
            color: #e53e3e;
            border: 2px solid #feb2b2;
        }

        .result.info {
            background: #ebf8ff;
            color: #3182ce;
            border: 2px solid #90cdf4;
        }

        .status-icon {
            font-size: 24px;
            margin-bottom: 10px;
            display: block;
        }

        .quick-actions {
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .quick-btn {
            padding: 10px;
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            color: #4a5568;
        }

        .quick-btn:hover {
            background: #edf2f7;
            border-color: #cbd5e0;
        }

        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 14px;
            color: #718096;
        }

        .webhook-url {
            font-family: 'Courier New', monospace;
            background: #f7fafc;
            padding: 8px;
            border-radius: 6px;
            font-size: 12px;
            margin-top: 10px;
            word-break: break-all;
        }

        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
            
            .date-range {
                grid-template-columns: 1fr;
            }
            
            .quick-actions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🏭 工程週報生成器</h1>
            <p class="subtitle">自動化工程項目週報生成系統<br>點擊按鈕即可生成本週工程進度報告</p>
        </div>

        <form id="reportForm">
            <div class="form-group">
                <label class="form-label">📅 報告週期（可選）</label>
                <div class="date-range">
                    <div>
                        <input type="date" id="startDate" class="form-input" placeholder="開始日期">
                    </div>
                    <div>
                        <input type="date" id="endDate" class="form-input" placeholder="結束日期">
                    </div>
                </div>
                <small style="color: #718096; margin-top: 5px; display: block;">
                    留空將自動使用上週範圍（週一至週日）
                </small>
            </div>

            <div class="quick-actions">
                <button type="button" class="quick-btn" onclick="setLastWeek()">
                    📋 上週範圍
                </button>
                <button type="button" class="quick-btn" onclick="setCurrentWeek()">
                    📅 本週範圍
                </button>
            </div>

            <button type="submit" class="trigger-btn" id="generateBtn">
                🚀 生成週報
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
            <p>正在生成週報，請稍候...</p>
        </div>

        <div class="result" id="result">
            <span class="status-icon" id="statusIcon"></span>
            <div id="resultMessage"></div>
        </div>

        <div class="footer">
            <p>🔗 <strong>Webhook URL:</strong></p>
            <div class="webhook-url" id="webhookUrl">
                https://jerry-hsieh.app.n8n.cloud/webhook-test/generate-weekly-report
            </div>
            <p style="margin-top: 10px;">
                建廠工程專案管理系統 v2024 | 自動化報告生成
            </p>
        </div>
    </div>

    <script>
        const WEBHOOK_URL = 'https://jerry-hsieh.app.n8n.cloud/webhook-test/generate-weekly-report';
        
        // 設定上週日期範圍
        function setLastWeek() {
            const today = new Date();
            const lastMonday = new Date(today);
            lastMonday.setDate(today.getDate() - today.getDay() - 6);
            
            const lastSunday = new Date(lastMonday);
            lastSunday.setDate(lastMonday.getDate() + 6);
            
            document.getElementById('startDate').value = formatDate(lastMonday);
            document.getElementById('endDate').value = formatDate(lastSunday);
        }
        
        // 設定本週日期範圍
        function setCurrentWeek() {
            const today = new Date();
            const monday = new Date(today);
            monday.setDate(today.getDate() - today.getDay() + 1);
            
            const sunday = new Date(monday);
            sunday.setDate(monday.getDate() + 6);
            
            document.getElementById('startDate').value = formatDate(monday);
            document.getElementById('endDate').value = formatDate(sunday);
        }
        
        // 格式化日期
        function formatDate(date) {
            return date.toISOString().split('T')[0];
        }
        
        // 顯示結果
        function showResult(type, icon, message) {
            const result = document.getElementById('result');
            const statusIcon = document.getElementById('statusIcon');
            const resultMessage = document.getElementById('resultMessage');
            
            result.className = `result ${type}`;
            result.style.display = 'block';
            statusIcon.textContent = icon;
            resultMessage.innerHTML = message;
            
            // 滾動到結果區域
            result.scrollIntoView({ behavior: 'smooth' });
        }
        
        // 隱藏結果
        function hideResult() {
            document.getElementById('result').style.display = 'none';
        }
        
        // 顯示/隱藏載入狀態
        function toggleLoading(show) {
            const loading = document.getElementById('loading');
            const btn = document.getElementById('generateBtn');
            
            if (show) {
                loading.style.display = 'block';
                btn.disabled = true;
                btn.textContent = '生成中...';
                hideResult();
            } else {
                loading.style.display = 'none';
                btn.disabled = false;
                btn.textContent = '🚀 生成週報';
            }
        }
        
        // 主要觸發函數
        async function triggerWeeklyReport() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            toggleLoading(true);
            
            try {
                const payload = {
                    manualTrigger: true,
                    timestamp: new Date().toISOString()
                };
                
                // 如果有指定日期範圍，加入 payload
                if (startDate && endDate) {
                    payload.start_date = startDate;
                    payload.end_date = endDate;
                    console.log(`📅 使用自訂日期範圍: ${startDate} 至 ${endDate}`);
                } else {
                    console.log('📅 使用預設日期範圍（上週）');
                }
                
                console.log('🚀 觸發週報生成...', payload);
                
                const response = await fetch(WEBHOOK_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
                
                console.log(`📡 HTTP 狀態: ${response.status}`);
                
                if (response.ok) {
                    const result = await response.text();
                    console.log('✅ 成功回應:', result);
                    
                    showResult('success', '✅', `
                        <strong>週報生成成功！</strong><br>
                        系統已開始處理您的週報請求。<br>
                        <small>請檢查您的 Discord 或 Gmail 以獲取完成通知。</small>
                    `);
                } else {
                    const errorText = await response.text();
                    console.error('❌ HTTP 錯誤:', response.status, errorText);
                    
                    showResult('error', '❌', `
                        <strong>觸發失敗</strong><br>
                        HTTP ${response.status}: ${response.statusText}<br>
                        <small>${errorText}</small>
                    `);
                }
                
            } catch (error) {
                console.error('💥 網路錯誤:', error);
                
                showResult('error', '💥', `
                    <strong>網路連接錯誤</strong><br>
                    ${error.message}<br>
                    <small>請檢查網路連接或稍後重試。</small>
                `);
            } finally {
                toggleLoading(false);
            }
        }
        
        // 表單提交處理
        document.getElementById('reportForm').addEventListener('submit', function(e) {
            e.preventDefault();
            triggerWeeklyReport();
        });
        
        // 頁面載入時的初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🏭 工程週報生成器已載入');
            console.log('🔗 Webhook URL:', WEBHOOK_URL);
            
            // 預設設定為上週範圍
            setLastWeek();
        });
        
        // 鍵盤快捷鍵
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                triggerWeeklyReport();
            }
        });
    </script>
</body>
</html>
