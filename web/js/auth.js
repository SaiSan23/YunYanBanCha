// 註冊表單提交處理
function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const email = document.getElementById('registerEmail').value;

    fetch('http://localhost:5001/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password, email })
    })
        .then(response => response.json())
        .then(data => {
            const messageElement = document.getElementById('registerMessage');
            if (data.error) {
                messageElement.className = 'error';
                messageElement.innerText = data.error;
            } else {
                messageElement.className = 'success';
                messageElement.innerText = data.message || '註冊成功！請登入';
                // 清空表單
                document.getElementById('registerForm').reset();

                // 可選：延遲後跳轉到登入頁面
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            }
        })
        .catch(error => {
            document.getElementById('registerMessage').className = 'error';
            document.getElementById('registerMessage').innerText = '註冊失敗：' + error.message;
        });
}

// 登入表單提交處理
function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    fetch('http://localhost:5001/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
        .then(response => response.json())
        .then(data => {

            console.log("🔥 登入後回傳的資料：", data);

            const messageElement = document.getElementById('loginMessage');
            if (data.error) {
                messageElement.className = 'error';
                messageElement.innerText = data.error;
            } else {
                messageElement.className = 'success';
                messageElement.innerText = data.message || '登入成功！';

                // 保存令牌和用戶名
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', data.username);
                localStorage.setItem('user_id', data.user_id);  

                // 顯示用戶信息，隱藏登入表單
                if (document.getElementById('loginForm')) {
                    document.getElementById('loginForm').classList.add('hidden');
                }
                if (document.getElementById('userInfoSection')) {
                    document.getElementById('userInfoSection').classList.remove('hidden');
                    document.getElementById('usernameDisplay').innerText = data.username;
                }

                // 清空表單
                document.getElementById('loginForm').reset();

                // 檢查有沒有暫存問卷數據，有的話跳轉到問卷頁面，沒有的話跳轉到首頁，延遲2秒後跳轉
                const survey = localStorage.getItem('tempSurveyData');
                if (!!survey) {
                    setTimeout(() => {
                        window.location.href = 'survey.html';
                    }, 2000);
                }else{
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 2000);
                }
                
            }
        })
        .catch(error => {
            document.getElementById('loginMessage').className = 'error';
            document.getElementById('loginMessage').innerText = '登入失敗：' + error.message;
        });
}

// 登出按鈕處理
function handleLogout() {
    // 清除本地存儲的令牌和用戶名
    localStorage.removeItem('token');
    localStorage.removeItem('username');

    // 如果在用戶信息頁面，則跳轉到登入頁面
    window.location.href = 'login.html';
}

// 檢查用戶登入狀態
function checkLoginStatus() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    // 更新導航欄顯示
    updateNavigation(!!token);

    if (token && username) {
        // 驗證令牌
        fetch('http://localhost:5001/api/auth/verify-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        })
            .then(response => response.json())
            .then(data => {
                if (!data.valid) {
                    // 令牌無效，清除本地存儲
                    localStorage.removeItem('token');
                    localStorage.removeItem('username');
                    updateNavigation(false);
                }
            })
            .catch(error => {
                console.error('令牌驗證失敗：', error);
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                updateNavigation(false);
            });
    }

    return !!token;
}

// 更新導航欄顯示
function updateNavigation(isLoggedIn) {
    const navElement = document.querySelector('.nav-links');
    if (!navElement) return;

    if (isLoggedIn) {
        const username = localStorage.getItem('username');
        navElement.innerHTML = `
            <a href="index.html">首頁</a>
            <a href="survey.html">問卷調查</a>
            <span>歡迎, ${username}!</span>
            <a href="#" id="logoutLink">登出</a>
        `;
        // 添加登出事件監聽器
        document.getElementById('logoutLink').addEventListener('click', handleLogout);
    } else {
        navElement.innerHTML = `
            <a href="index.html">首頁</a>
            <a href="login.html">登入</a>
            <a href="register.html">註冊</a>
            <a href="survey.html">問卷調查</a>
        `;
    }
}

// 頁面加載時初始化
document.addEventListener('DOMContentLoaded', function () {
    // 檢查登入狀態
    const isLoggedIn = checkLoginStatus();

    // 註冊表單事件監聽
    const registerForm = document.getElementById('registerForm');
    // 如果頁面上有註冊表單，則添加事件監聽
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // 登入表單事件監聽
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // 登出按鈕事件監聽
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }

    // 用戶信息顯示
    const userInfoSection = document.getElementById('userInfoSection');
    const loginRegisterForms = document.getElementById('loginRegisterForms');

    if (isLoggedIn && userInfoSection && loginRegisterForms) {
        loginRegisterForms.classList.add('hidden');
        userInfoSection.classList.remove('hidden');
        const username = localStorage.getItem('username');
        if (document.getElementById('usernameDisplay')) {
            document.getElementById('usernameDisplay').innerText = username;
        }
    }
});