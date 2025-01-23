// 날짜 업데이트 함수
function updateDate() {
    const dateContainer = document.getElementById('date-container');
    const now = new Date();

    // 날짜 형식 지정
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    };

    // 현재 날짜만 표시
    dateContainer.textContent = now.toLocaleDateString('ko-KR', options);
}

// 날짜 변경 시점 계산
function scheduleDateUpdate() {
    const now = new Date();
    const nextMidnight = new Date(now);
    
    // 다음 날 자정으로 설정
    nextMidnight.setHours(24, 0, 0, 0); 

    // 자정까지 남은 시간을 계산 (다음 자정까지 남은 시간 밀리초)
    const timeUntilMidnight = nextMidnight - now;

    // 자정에 맞춰 업데이트 함수 호출 (다음 날 00:00:00)
    setTimeout(() => {
        updateDate();
        // 이후 매일 자정마다 날짜를 업데이트하도록 설정
        setInterval(updateDate, 86400000); // 24시간마다 날짜 업데이트
    }, timeUntilMidnight);
}

updateDate();
scheduleDateUpdate();