
//
import SwiftUI
import Alamofire

class DescriptionViewModel: ObservableObject {
    @Published var descriptionText: String = ""
    @Published var explanationText: String = ""
    @Published var commentText: String = ""
    @Published var image_url: String = ""
    @Published var meta: [String: String] = [:]
    @Published var isLoadingFetchDescription: Bool = false
    @Published var isLoadingRequestDescription: Bool = false
    @Published var errorMessage: String?
    
    @Published var isDescriptionLoaded = false // 해설 로딩 완료 여부
    @Published var descriptionRequestError: String? = nil // 에러 메시지 저장

    func fetchDescription(for file: String, uniqueId: String) {
        isLoadingFetchDescription = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/description/get-origin/?uniqueid=\(uniqueId)"
        let parameters: [String: String] = ["file": file]
        
        AF.request(url, method: .post, parameters: parameters, encoding: JSONEncoding.default)
            .validate()
            .responseJSON { response in
                self.isLoadingFetchDescription = false
                
                switch response.result {
                case .success(let data):
                    if let json = data as? [String: Any] {
                        self.descriptionText = json["description"] as? String ?? "No description available."
                        self.explanationText = json["explanation"] as? String ?? "No explanation available."
                        self.commentText = json["comment"] as? String ?? "No comment available."
                        self.meta = json["meta"] as? [String: String] ?? [:]
                        self.image_url = json["image_url"] as? String ?? "no url available"
                    } else {
                        self.errorMessage = "Invalid response format."
                    }
                case .failure(let error):
                    self.errorMessage = "Failed to fetch description: \(error.localizedDescription)"
                }
            }
    }
    
    
    func requestDescriptionWithScreenshot(image: UIImage, file: String, uniqueId: String, promptmode: String) {
        isLoadingRequestDescription = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/description/gpt-artwork/?uniqueid=\(uniqueId)&promptmode=\(promptmode)"
        let headers: HTTPHeaders = [
            "Content-Type": "multipart/form-data"
        ]
        
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            self.errorMessage = "Failed to process image."
            self.isLoadingRequestDescription = false
            return
        }
        
        print("Request URL: \(url)")
        print("Headers: \(headers)")
        print("File Content: \(file)")

        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(Data(file.utf8), withName: "request")
            multipartFormData.append(imageData, withName: "crop_image", fileName: "image.jpg", mimeType: "image/jpeg")
        }, to: url, headers: headers) { $0.timeoutInterval = 180 }


//        .validate()
        .validate(statusCode: 200..<600)
        .responseData { response in
            self.isLoadingRequestDescription = false
            
//            print("Full response: \(response)")
            
            print("--- fetchDescription Response Start ---")
                            print("Request: \(String(describing: response.request))") // 요청 정보
                            print("Response: \(String(describing: response.response))") // HTTP 응답 정보 (상태 코드 등)
                            print("Result: \(response.result)") // 결과 (성공/실패)
                            if let data = response.data, let utf8Text = String(data: data, encoding: .utf8) {
                                print("Response Body (UTF-8): \(utf8Text)") // 응답 본문 (JSON 또는 문자열)
                            }
                            print("--- fetchDescription Response End ---")
            
            switch response.result {
            case .success(let data):
                if let utf8Text = String(data: data, encoding: .utf8) {
                    // Convert the UTF-8 string to JSON
                    if let jsonData = utf8Text.data(using: .utf8),
                       let json = try? JSONSerialization.jsonObject(with: jsonData, options: []) as? [String: Any] {
                        self.descriptionText = json["description"] as? String ?? "No description available."
                        // ✅ 성공적으로 데이터를 받아온 경우 isDescriptionLoaded를 true로 설정
                        self.isDescriptionLoaded = true
                        self.descriptionRequestError = nil // 에러 초기화
                    } else {
                        self.errorMessage = "Failed to parse the JSON response."
                        self.descriptionRequestError = self.errorMessage
                        self.isDescriptionLoaded = true // JSON 파싱 실패도 알림 표시
                    }
                } else {
                    self.errorMessage = "Failed to decode response as UTF-8."
                    self.descriptionRequestError = self.errorMessage
                    self.isDescriptionLoaded = true
                }
            case .failure(let error):
                self.errorMessage = "Failed to fetch description: \(error.localizedDescription)"
                self.descriptionRequestError = self.errorMessage
                self.isDescriptionLoaded = true
            }
        }
    }
}
