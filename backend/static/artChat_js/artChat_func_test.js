// Base64 Data URI를 File 객체로 변환하는 헬퍼 함수
function dataURItoFile(dataURI, filename) {
    const parts = dataURI.split(',');
    const mime = parts[0].match(/:(.*?);/)[1];
    const b64 = parts[1];
    const byteString = atob(b64);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new File([ab], filename, { type: mime });
}

// 캡처된 영역을 Canvas를 이용해 Base64로 변환하는 함수 (zoomFactor 인자 추가됨)
function cropImageFromZoom(srcX, srcY, srcW, srcH, originalImageUrl, zoomFactor) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = "Anonymous";

        img.onload = function() {
            // ★ 수정: Canvas의 크기를 '잘라낼 영역의 원본 픽셀 크기'로 설정합니다.
            // 이렇게 해야 최종 이미지 파일이 뷰포트 크기에 맞춰집니다.
            canvas.width = Math.round(srcW);
            canvas.height = Math.round(srcH);
            console.log('w',canvas.width)
            console.log('h',canvas.height)

            // drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight)
            ctx.drawImage(
                img,
                srcX, srcY, // 원본 이미지에서 자르기 시작할 X, Y 좌표
                srcW, srcH, // 원본 이미지에서 자를 너비와 높이
                0, 0,       // Canvas에 그리기 시작할 X, Y 좌표
                canvas.width, canvas.height // Canvas에 그려질 최종 크기
            );

            const base64Data = canvas.toDataURL('image/jpeg');
            resolve(base64Data);
        };
        img.onerror = (e) => reject(e);
        img.src = originalImageUrl;
    });
}

// =========================================================================

document.getElementById('ask_AI_btn').addEventListener('click', async () => {
    // 필요한 DOM 요소 가져오기
    const originalInput = document.getElementById('image');
    // Note: cropInput은 이제 사용하지 않지만, originalInput에서 원본 파일을 가져옵니다.
    const promptMode = document.getElementById('promptModeSelect').value;
    const outputDiv = document.getElementById('resultOutput');
    const $image = $('#image'); // jQuery를 사용해 이미지 요소 가져오기
    const zoomInstance = $image.data('__apiz__'); // ap-image-zoom 인스턴스 가져오기

    console.log('original ', originalInput)

    // 1. 파일 선택 및 Zoom 인스턴스 확인
    // if (originalInput.files.length === 0) {
    //     alert("원본 이미지를 선택해주세요.");
    //     return;
    // }
    if (!zoomInstance) {
        alert("이미지 줌 인스턴스를 찾을 수 없습니다. 라이브러리가 로드되었는지 확인하세요.");
        return;
    }

    outputDiv.innerHTML = "원본 이미지 로드 중...";
    const originalImageUrl = $image.attr('src');
    const originalFile = await urlToFile(originalImageUrl, 'original_image.jpg'); // 아래에 정의된 함수 사용

    // 2. 🔍 확대 영역 정보 추출 및 계산
    
    // a. Zoom 인스턴스에서 필요한 값 추출
    const zoomFactor = zoomInstance.currentZoom; // 현재 확대율
    const currentPos = zoomInstance.currentPosition; // 현재 이미지의 이동 위치 (Point {x, y})
    const naturalSize = zoomInstance.naturalSize; // 원본 이미지 크기
    const overlaySize = zoomInstance._getOverlaySize(); // 화면에 보이는 컨테이너 크기

    // b. 원본 이미지에서 잘라낼 영역 (Source Rectangle) 계산
    
    // 뷰포트 좌측 상단이 원본 이미지 중앙(0,0)에서 얼마나 떨어져 있는지 계산
    // Math.round(currentSize.width / 2)는 이미지 중앙이 0,0이 되도록 좌표를 보정함
    const currentSize = {
        width: naturalSize.width * zoomFactor,
        height: naturalSize.height * zoomFactor
    };
    console.log('current',currentSize)
    
    const VPR_X = (-1 * currentPos.x) - (currentSize.width / 2) + (overlaySize.width / 2);
    const VPR_Y = (-1 * currentPos.y) - (currentSize.height / 2) + (overlaySize.height / 2);

    // 3. ✂️ 원본 이미지 픽셀 기준 자르기 시작할 좌표 (Source X, Y)
    // VPR_X를 확대율로 나누면 원본 이미지 상의 좌표가 나옵니다.
    const srcX = VPR_X / zoomFactor;
    const srcY = VPR_Y / zoomFactor;

    // 4. 📏 원본 이미지 픽셀 기준 자를 너비와 높이 (Source Width, Height)
    // 뷰포트의 크기를 확대율로 나누면 원본 이미지 상의 크기가 나옵니다.
    const srcW = overlaySize.width / zoomFactor;
    const srcH = overlaySize.height / zoomFactor;


    // 5. ⚠️ 경계 보정 (0보다 작거나 원본 크기를 초과하지 않도록)
    const finalSrcX = Math.max(0, srcX);
    const finalSrcY = Math.max(0, srcY);

    const finalSrcW = Math.min(srcW - (finalSrcX - srcX), naturalSize.width - finalSrcX);
    const finalSrcH = Math.min(srcH - (finalSrcY - srcY), naturalSize.height - finalSrcY);

    // 최종 계산된 좌표로 cropImageFromZoom을 호출해야 합니다.
    console.log('Final Crop Area:', {finalSrcX, finalSrcY, finalSrcW, finalSrcH});
    
    // 3. Canvas를 이용해 확대 영역 캡처
    outputDiv.innerHTML = "확대 영역 캡처 중...";
    const base64Image = await cropImageFromZoom(
        srcX, srcY, 
        finalSrcX, finalSrcY, // 보정된 크기 사용
        originalImageUrl, 
        zoomFactor
    );

    // 4. Base64를 File 객체로 변환
    const cropFile = dataURItoFile(base64Image, 'cropped_zoom_image.jpeg');

    const tmpDiv = document.getElementById('tmp');

    // 1. 기존 내용 비우기 (새 이미지로 덮어쓰기 위해)
    tmpDiv.innerHTML = '';

    // 2. File 객체(Blob)에 접근할 수 있는 임시 URL 생성
    const objectURL = URL.createObjectURL(cropFile);

    // 3. 새로운 <img> 요소 생성 및 URL 할당
    const imgPreview = document.createElement('img');
    imgPreview.src = objectURL;
    imgPreview.alt = "크롭된 이미지 미리보기";

    // 4. 스타일 적용 (선택 사항)
    imgPreview.style.maxWidth = '100%';
    imgPreview.style.height = 'auto';
    imgPreview.style.border = '3px dashed blue'; // 구분을 위한 테두리

    // 5. <img> 요소를 <div id="tmp">에 삽입
    tmpDiv.appendChild(imgPreview);

    // 6. 메모리 정리 (페이지를 떠나거나 더 이상 필요 없을 때 호출해야 함. 
    //    보통 브라우저가 자동으로 정리하지만 명시적으로 호출하는 것이 좋습니다.)
    // URL.revokeObjectURL(objectURL);

    // 5. FormData 객체 생성 및 데이터 추가 (FastAPI로 전송)
    console.log('original_image', originalFile)
    console.log('crop_image', cropFile)

    const formData = new FormData();
    formData.append('original_image', originalFile);
    formData.append('crop_image', cropFile); // 캡처된 크롭 이미지 사용

    // 6. 요청 URL 생성 및 POST 요청 전송
    const apiUrl = `/gpt-nonartwork/?promptmode=${promptMode}`;
    outputDiv.innerHTML = "AI 분석 요청 중... (응답 대기)";

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });

        // 7. 응답 처리 (이하 기존 로직)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP 오류: ${response.status} - ${errorData.detail || response.statusText}`);
        }

        const data = await response.json();
        outputDiv.innerHTML = `
            <h3>AI 설명 결과:</h3>
            <p>${data.description}</p>
        `;

    } catch (error) {
        outputDiv.innerHTML = `<p style="color: red;">요청 실패: ${error.message}</p>`;
        console.error("Fetch Error:", error);
    }
});

async function urlToFile(url, filename) {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
}