async function fetchUserPersonality() {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
        document.getElementById("personality").innerHTML = `<p style="color:red;">請先登入</p>`;
        return;
    }

    try {
        const res = await fetch(`http://localhost:5002/questionnaire/personality/${userId}`);
        const data = await res.json();

        if (data.tea_type) {
            document.getElementById("personality").innerHTML = `
                <h3>你的人格茶型：${data.tea_type.name}</h3>
                <p>${data.tea_type.description}</p>
                <img src="${data.tea_type.image_url}" style="max-width: 150px;">
            `;
        } else {
            document.getElementById("personality").innerHTML = `
                <p style="color: orange;">尚未完成人格測驗，<a href="survey.html">點我測驗</a></p>
            `;
        }

    } catch (err) {
        console.error("🚨 載入人格資料失敗", err);
        document.getElementById("personality").innerHTML = `<p style="color:red;">⚠️ 載入人格資料失敗</p>`;
    }
}


function openMissionModal() {
    document.getElementById("missionModal").classList.remove("hidden");
}

function closeMissionModal() {
    document.getElementById("missionModal").classList.add("hidden");
}

async function fetchUserMissions() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');
    const content = document.getElementById("modalMissionContent");

    openMissionModal();

    if (!userId || !token) {
        content.innerHTML = '<p style="color:red;">請先登入查看任務。</p>';
        return;
    }

    content.innerHTML = '載入中...';

    try {
        const res = await fetch(`http://localhost:5003/missions/recommend/${userId}`);
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const result = await res.json();

        if (result.error === '無人格紀錄') {
            content.innerHTML = '<p>尚未完成茶型測驗，<a href="survey.html">前往測驗</a></p>';
            return;
        }

        if (result.missions && result.missions.length > 0) {
            let html = '<ul>';
            result.missions.forEach(m => {
                const status = m.is_completed
                    ? `<span style="color: green;">✅ 已完成</span> ${m.coupon ? `｜🎁 優惠券：<code>${m.coupon.code}</code>` : ''}`
                    : `<span style="color: gray;">❌ 未完成</span>`;
                html += `<li style="margin-bottom:10px;">📌 <strong>${m.title}</strong>（${m.type}）<br/>${status}</li>`;
            });
            html += '</ul>';
            content.innerHTML = html;
        } else {
            content.innerHTML = '<p>目前沒有任務。</p>';
        }
    } catch (err) {
        content.innerHTML = '<p style="color:red;">查詢任務失敗</p>';
        console.error("🚨 任務查詢錯誤：", err);
    }
}


document.addEventListener("DOMContentLoaded", async () => {
    await fetchUserPersonality();      // 確保人格資料已經完成
    await fetchUserMissions();         // 再接著抓任務（這樣才不會卡住）
});
