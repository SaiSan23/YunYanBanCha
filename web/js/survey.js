// 問卷數據暫存的鍵名
const SURVEY_STORAGE_KEY = 'tempSurveyData';

// 頁面加載時初始化
document.addEventListener('DOMContentLoaded', function () {
    // 載入問卷題目
    loadQuestionnaire();

    // 註冊問卷提交事件
    const surveyForm = document.getElementById('userSurvey');
    if (surveyForm) {
        surveyForm.addEventListener('submit', handleSurveySubmit);
    }
});

// 載入問卷題目
function loadQuestionnaire() {
    // 發送請求到後端獲取問卷題目
    fetch('http://localhost:5001/api/questionnaire', {
        method: 'GET',
        headers: {
            "Content-Type": "application/json; charset=UTF-8"
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('載入問卷失敗:', data.error);
            } else {
                console.log('問卷題目:', data);
                // 生成問卷題目
                const questionsContainer = document.getElementById('questionsContainer');
                questionsContainer.innerHTML = '';

                // 动态生成问题，基于API返回的题目数量
                data.questionnaires.forEach((question, index) => {
                    const questionNumber = index + 1;
                    const questionDiv = document.createElement('div');
                    questionDiv.className = 'question';
                    questionDiv.innerHTML = `
                    <h3>${questionNumber}. ${question.title}</h3>
                    <div class="options">
                        <div class="option">
                            <input type="radio" id="q${questionNumber}_1" name="q${questionNumber}" value="1">
                            <label for="q${questionNumber}_1">1分</label>
                        </div>
                        <div class="option">
                            <input type="radio" id="q${questionNumber}_2" name="q${questionNumber}" value="2">
                            <label for="q${questionNumber}_2">2分</label>
                        </div>
                        <div class="option">
                            <input type="radio" id="q${questionNumber}_3" name="q${questionNumber}" value="3">
                            <label for="q${questionNumber}_3">3分</label>
                        </div>
                        <div class="option">
                            <input type="radio" id="q${questionNumber}_4" name="q${questionNumber}" value="4">
                            <label for="q${questionNumber}_4">4分</label>
                        </div>
                        <div class="option">
                            <input type="radio" id="q${questionNumber}_5" name="q${questionNumber}" value="5">
                            <label for="q${questionNumber}_5">5分</label>
                        </div>
                    </div>
                `;
                    questionsContainer.appendChild(questionDiv);
                });

                // 檢查登入狀態 && 檢查是否有暫存的問卷數據
                const isLoggedIn = checkLoginStatus();
                const tempSurveyData = localStorage.getItem(SURVEY_STORAGE_KEY);

                // 如果已登入且有暫存數據，自動填充表單
                if (isLoggedIn && tempSurveyData) {
                    try {
                        const surveyData = JSON.parse(tempSurveyData);
                        fillSurveyForm(surveyData);
                    } catch (e) {
                        console.error('解析暫存問卷數據失敗:', e);
                        localStorage.removeItem(SURVEY_STORAGE_KEY);
                    }
                }
            }
        })
        .catch(error => {
            console.error('載入問卷失敗:', error);
        });
}

// 填充問卷表單
function fillSurveyForm(data) {
    // 填充問卷答案
    Object.keys(data).forEach(key => {
        if (key.startsWith('q') && !isNaN(parseInt(key.substring(1)))) {
            const radioBtn = document.querySelector(`input[name="${key}"][value="${data[key]}"]`);
            if (radioBtn) radioBtn.checked = true;
        }
    });
}

// 收集問卷數據
function collectSurveyData() {
    const data = {};

    // 获取问题数量
    const questionCount = document.querySelectorAll('.question').length;

    // 收集所有問題的答案
    for (let i = 1; i <= questionCount; i++) {
        const answerEl = document.querySelector(`input[name="q${i}"]:checked`);
        data[`q${i}`] = answerEl ? parseInt(answerEl.value) : null;
    }

    // 計算總分
    data.score = Object.keys(data)
        .filter(key => key.startsWith('q'))
        .reduce((sum, key) => sum + (data[key] || 0), 0);

    return data;
}

// 驗證問卷數據
function validateSurveyData(data) {
    // 获取问题数量
    const questionCount = document.querySelectorAll('.question').length;

    // 檢查是否所有問題都已回答
    for (let i = 1; i <= questionCount; i++) {
        if (!data[`q${i}`]) {
            return `請回答問題 ${i}`;
        }
    }
    return null; // 验证通过
}

// 處理問卷提交
function handleSurveySubmit(e) {
    e.preventDefault();

    // 收集問卷數據
    const surveyData = collectSurveyData();

    // 驗證數據
    const validationError = validateSurveyData(surveyData);
    const messageElement = document.getElementById('surveyMessage');

    if (validationError) {
        // 顯示錯誤訊息
        messageElement.className = 'survey-message error';
        messageElement.innerText = validationError;
        messageElement.classList.remove('hidden');
        return;
    }

    // 暫存問卷數據
    localStorage.setItem(SURVEY_STORAGE_KEY, JSON.stringify(surveyData));

    // 檢查用戶是否已登入
    const isLoggedIn = checkLoginStatus();

    if (isLoggedIn) {
        // 已登入，直接提交問卷
        submitSurveyToServer(surveyData);
    } else {
        // 未登入，顯示登入提示
        document.getElementById('surveyForm').classList.add('hidden');
        document.getElementById('loginPrompt').classList.remove('hidden');
    }
}

// 提交問卷到伺服器
function submitSurveyToServer(surveyData) {
    const token = localStorage.getItem('token');

    fetch('http://localhost:5001/api/questionnaire/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify(surveyData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // 顯示錯誤訊息
                const messageElement = document.getElementById('surveyMessage');
                messageElement.className = 'survey-message error';
                messageElement.innerText = data.error;
                messageElement.classList.remove('hidden');
            } else {
                // 提交成功，清除暫存數據
                localStorage.removeItem(SURVEY_STORAGE_KEY);

                // 顯示成功訊息和茶型人格結果
                document.getElementById('surveyForm').classList.add('hidden');
                document.getElementById('surveySuccess').classList.remove('hidden');

                // 如果有茶型人格結果，顯示它
                if (data.tea_type) {
                    const resultDiv = document.getElementById('teaPersonalityResult');
                    resultDiv.classList.remove('hidden');

                    document.getElementById('teaTypeName').textContent = data.tea_type.name;
                    document.getElementById('teaTypeDescription').textContent = data.tea_type.description;

                    if (data.tea_type.image_url) {
                        const imgElement = document.getElementById('teaTypeImage');
                        imgElement.src = data.tea_type.image_url;
                        imgElement.classList.remove('hidden');
                    }
                }
            }
        })
        .catch(error => {
            // 顯示錯誤訊息
            const messageElement = document.getElementById('surveyMessage');
            messageElement.className = 'survey-message error';
            messageElement.innerText = '提交失敗：' + error.message;
            messageElement.classList.remove('hidden');
        });
}

// 檢查用戶是否從登入/註冊頁面返回
window.addEventListener('pageshow', function () {
    const isLoggedIn = checkLoginStatus();
    const tempSurveyData = localStorage.getItem(SURVEY_STORAGE_KEY);

    // 如果用戶已登入且有暫存的問卷數據，且登入提示正在顯示
    if (isLoggedIn && tempSurveyData && !document.getElementById('loginPrompt').classList.contains('hidden')) {
        try {
            // 解析暫存數據
            const surveyData = JSON.parse(tempSurveyData);

            // 隱藏登入提示，顯示問卷表單
            document.getElementById('loginPrompt').classList.add('hidden');
            document.getElementById('surveyForm').classList.remove('hidden');

            // 自動提交問卷
            submitSurveyToServer(surveyData);
        } catch (e) {
            console.error('解析暫存問卷數據失敗:', e);
            localStorage.removeItem(SURVEY_STORAGE_KEY);
        }
    }
});