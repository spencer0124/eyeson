// 날짜 및 시간 업데이트 함수
function updateDate() {
    const dateContainer = document.getElementById('date-container');
    const now = new Date();

    // 날짜 형식 지정
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };

    // 날짜를 문자열로 변환하여 표시
    dateContainer.textContent = now.toLocaleDateString('en-US', options);
}

// 실시간으로 시간 업데이트 (1초 간격)
setInterval(updateDate, 1000);

// 페이지 로드 시 초기 호출
updateDate();