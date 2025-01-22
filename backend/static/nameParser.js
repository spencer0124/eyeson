function extractUsernameFromName(userName) {
    const regex = /\((.*?)\)/;  // 괄호 안의 내용을 추출하는 정규식
    const match = userName.match(regex);

    if (match && match[1]) {
        return match[1];  // 괄호 안의 내용만 반환
    } else {
        return null;  // 괄호 안에 내용이 없으면 null 반환
    }
}