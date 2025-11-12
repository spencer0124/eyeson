// Data URI를 File 객체로 변환하는 헬퍼 함수
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

// Canvas를 이용해 지정된 영역을 캡처하는 함수 (원본 크기로 캡처)
function cropImageFromTransform(srcX, srcY, srcW, srcH, originalImageUrl, targetW, targetH) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = "Anonymous"; // CORS 문제 방지

        img.onload = function() {
            // Canvas의 크기를 뷰포트 크기(즉, 최종 파일 크기)로 설정합니다.
            canvas.width = Math.round(targetW);
            canvas.height = Math.round(targetH);

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

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('ask_AI_btn').addEventListener('click', async () => {
        
        // 1. 필요한 DOM 요소 및 이미지 데이터 가져오기
        const originalInput = document.getElementById('image');
        const targetInput = document.getElementById('targetImage')

        const promptMode = document.getElementById('promptModeSelect').value;
        const outputDiv = document.getElementById('resultOutput');
        const tmpDiv = document.getElementById('tmp');

        // 스타일이 적용되는 이미지 요소 (ID: targetImage)
        const $targetImage = $('#targetImage'); 
        const $wrapper = $targetImage.closest('.apiz-wrapper');

        console.log('original ', originalInput)
        console.log('target', targetInput)

        outputDiv.innerHTML = "처리 중... 잠시만 기다려 주세요.";
        const originalImageUrl = originalInput.src;
        const originalFile = await urlToFile(originalImageUrl, 'original_image.jpg');
        

        // 2. 🔍 Transform 값 추출
        const style = $targetImage.css('transform');
        if (!style || style === 'none') {
            alert("이미지에 transform 스타일이 적용되지 않았습니다. 줌을 먼저 해주세요.");
            return;
        }

        // matrix3d(scale, 0, 0, 0, 0, scale, 0, 0, 0, 0, 1, 0, translateX, translateY, 0, 1)
        const matrixValues = style.match(/matrix3d\((.+)\)/)[1].split(',').map(v => parseFloat(v.trim()));
        
        const zoomFactor = matrixValues[0]; // Scale (1번째 값)
        const translateX = matrixValues[12]; // X 이동 (13번째 값)
        const translateY = matrixValues[13]; // Y 이동 (14번째 값)
        console.log('zoom', zoomFactor)
        console.log('x', translateX)
        console.log('y',translateY)

        // 3. 📏 크기 및 좌표 계산
        
        // 원본 이미지 크기 (naturalWidth, naturalHeight)
        const img = new Image();
        img.src = originalImageUrl;
        await new Promise(resolve => img.onload = resolve);
        const naturalW = img.naturalWidth;
        const naturalH = img.naturalHeight;
        console.log('w',naturalW, 'h',naturalH)

        // 뷰포트 (wrapper) 크기 (캡처될 최종 이미지 크기)
        const viewportW = $wrapper.width();
        const viewportH = $wrapper.height();
        console.log('viewW',viewportW,'viewh',viewportH)

        // 내가 추가
        // const w = Math.round(naturalW * zoomFactor)
        // const h = Math.round(naturalH * zoomFactor)
        // const marginL = translateX
        // const marginT = translateY
        // const newW = w + marginL
        // const newH = h + marginT

        // console.log('w',w,'h',h)
        // console.log('marginL',marginL,'marginR',marginT)

        // 1. Zoom된 이미지의 크기 계산
        const zoomedW = naturalW * zoomFactor;
        const zoomedH = naturalH * zoomFactor;
        console.log('zoomedW',zoomedW, 'zoomedh',zoomedH)

        // 2. 초기 중앙 정렬을 위한 이동 거리 계산 (Initial Centering Offset)
        // 이미지가 중앙에 위치했을 때, 이미지의 좌상단이 뷰포트 좌상단으로부터 떨어진 거리
        const initialOffsetX = (viewportW - zoomedW) / 2;
        const initialOffsetY = (viewportH - zoomedH) / 2;

        // 3. ✂️ 순수 팬 이동 거리 계산 (Pure Pan Distance)
        // 최종 transform 값(translateX)에서 초기 중앙 정렬 값(initialOffset)을 뺍니다.
        const purePanX = translateX - initialOffsetX;
        const purePanY = translateY - initialOffsetY;

        // 4. 📐 원본 이미지 픽셀 기준 크롭 시작 좌표 (srcX, srcY) 계산
        // 순수 팬 이동 거리를 zoomFactor로 나누고, 뷰포트가 보는 시작점(음수 방향)이므로 -1을 곱합니다.
        // 이 공식이 중앙 정렬 오프셋 문제를 해결합니다.

        // const srcX = (-purePanX) / zoomFactor; 
        // const srcY = (-purePanY) / zoomFactor;
        const srcX = (-translateX) * zoomFactor
        const srcY = (-translateY) / zoomFactor
        console.log('-tX - viewW',(-translateX - viewportW))
        console.log('srcx',srcX,'srcy',srcY)

        // 5. 원본 이미지 픽셀 기준 크롭할 너비와 높이 (srcW, srcH)
        const srcW = viewportW / zoomFactor;
        const srcH = viewportH / zoomFactor;

        // 캡처 시작점 계산: 원본 이미지 픽셀 기준
        // 뷰포트 좌상단이 확대된 이미지 좌상단에서 얼마나 떨어진 픽셀인가?
        // (FastAPI의 계산 방식과 다름: apiz-wrapper는 이미지 좌상단을 기준으로 움직임)
        
        // 뷰포트 좌상단은 이미지 좌상단에서 (translateX, translateY)만큼 떨어져 있습니다.
        // 이 값은 뷰포트 좌표계가 이미지 좌표계에 겹쳐진 것을 의미합니다.
        
        // 원본 이미지 픽셀 기준 크롭 시작 좌표 (sx, sy)
        // const srcX = Math.abs(translateX) / zoomFactor;
        // const srcY = Math.abs(translateY) / zoomFactor;

        // // 원본 이미지 픽셀 기준 크롭할 너비와 높이 (sWidth, sHeight)
        // const srcW = viewportW / zoomFactor;
        // const srcH = viewportH / zoomFactor;

        // // ⚠️ 경계 보정 (원본 이미지를 벗어날 경우)
        // const finalSrcX = Math.max(0, srcX);
        // const finalSrcY = Math.max(0, srcY);
        // const finalSrcW = Math.min(srcW - (finalSrcX - srcX), naturalW - finalSrcX);
        // const finalSrcH = Math.min(srcH - (finalSrcY - srcY), naturalH - finalSrcY);
        
        // 4. ✂️ Canvas를 이용해 확대 영역 캡처
        outputDiv.innerHTML = "확대 영역 캡처 중...";
        const base64Image = await cropImageFromTransform(
            srcX, srcY, 
            srcW, srcH,
            originalImageUrl, 
            viewportW, viewportH // Canvas의 최종 크기는 뷰포트 크기로 설정
        );

        // 5. Base64를 File 객체로 변환
        const cropFile = dataURItoFile(base64Image, 'cropped_zoom_image.jpeg');

        // 6. 미리보기 표시 (tmpDiv)
        tmpDiv.innerHTML = '';
        const objectURL = URL.createObjectURL(cropFile);
        const imgPreview = document.createElement('img');
        imgPreview.src = objectURL;
        imgPreview.style.maxWidth = '100%';
        imgPreview.style.border = '3px dashed blue';
        tmpDiv.appendChild(imgPreview);

        // 7. FormData 객체 생성 및 FastAPI 전송
        const formData = new FormData();
        formData.append('original_image', originalFile); // Input File
        formData.append('crop_image', cropFile);        // Captured File

        const apiUrl = `/gpt-nonartwork/?promptmode=${promptMode}`;
        outputDiv.innerHTML = "AI 분석 요청 중... (응답 대기)";

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP 오류: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            outputDiv.innerHTML = `
                <h3>AI 설명 결과:</h3>
                <p>${data.description}</p>
            `;
            URL.revokeObjectURL(objectURL); // 임시 URL 해제

        } catch (error) {
            outputDiv.innerHTML = `<p style="color: red;">요청 실패: ${error.message}</p>`;
            console.error("Fetch Error:", error);
            URL.revokeObjectURL(objectURL);
        }
    });
});

async function urlToFile(url, filename) {
    const response = await fetch(url);
    const blob = await response.blob();
    return new File([blob], filename, { type: blob.type });
}