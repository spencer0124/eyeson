function getArtwork(title, artworkImg) {
    const url = `http://43.201.93.53:8000/chat/download-profile?title=${encodeURIComponent(title)}`;
    console.log('js url', url)
    
    fetch(url)
        .then(response => response.blob())  // 이미지 데이터를 blob 형태로 받기
        .then(blob => {
            // Blob을 Object URL로 변환
            const imageUrl = URL.createObjectURL(blob);

            // 미리 준비한 <img> 태그의 src 속성에 이미지 URL을 설정
            // const imgElement = document.getElementById("artwork-image");
            // imgElement.src = imageUrl;  // 이미지 표시
            artworkImg.src = imageUrl;
        })
        .catch(error => {
            console.error("Error:", error);
        });
}