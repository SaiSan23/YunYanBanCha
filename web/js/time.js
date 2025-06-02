// 更新當前時間的函數
function updateCurrentTime() {
    const now = new Date();
    document.getElementById('currentTime').innerText = now.toLocaleString('zh-TW');
}

// 獲取資料庫時間的函數
function fetchTime() {
    // 檢查是否已登入
    const token = localStorage.getItem('token');
    if (!token) {
        document.getElementById('time').innerText = '請先登入系統';
        return;
    }

    fetch('http://localhost:5001/api/time')
        .then(response => response.json())
        .then(data => {
            document.getElementById('time').innerText = data.time;
        });
}

// 頁面加載時初始化
document.addEventListener('DOMContentLoaded', function() {
    // 更新當前時間
    updateCurrentTime();
    // 每秒更新一次時間
    setInterval(updateCurrentTime, 1000);
});

