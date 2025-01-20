function getArtwork() {
    let s3Key = "JeongyeonMoon_Comfort3.jpg"
    const url = `http://43.201.93.53:8000/chat/download-profile?s3_key=${encodeURIComponent(s3Key)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                console.log(data.message);  // "Image downloaded successfully" 메시지 출력
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

getArtwork();