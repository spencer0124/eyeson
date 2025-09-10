
import Foundation
import SwiftUI
import Alamofire

class FreeCameraModeViewModel: ObservableObject {
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

    
    func requestDescriptionWithScreenshot2(image1: UIImage, image2: UIImage, promptmode: String) {
        isLoadingRequestDescription = true
        errorMessage = nil
        
        let url = "http://XXXX:8000/description/gpt-nonartwork/?promptmode=\(promptmode)"
        let headers: HTTPHeaders = [
            "Content-Type": "multipart/form-data"
        ]
        
        guard let imageData1 = image1.jpegData(compressionQuality: 0.8) else {
            self.errorMessage = "Failed to process image."
            self.isLoadingRequestDescription = false
            return
        }
        
        guard let imageData2 = image2.jpegData(compressionQuality: 0.8) else {
            self.errorMessage = "Failed to process image."
            self.isLoadingRequestDescription = false
            return
        }
        
        print("Request URL: \(url)")
        print("Headers: \(headers)")
        

        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(imageData1, withName: "original_image", fileName: "original_image.jpg", mimeType: "image/jpeg")
            multipartFormData.append(imageData2, withName: "crop_image", fileName: "crop_image.jpg", mimeType: "image/jpeg")
        }, to: url, headers: headers) { $0.timeoutInterval = 180 }


        .validate(statusCode: 200..<600)
        .responseData { response in
            self.isLoadingRequestDescription = false

            
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
                    } else {
                        self.errorMessage = "Failed to parse the JSON response."
                    }
                } else {
                    self.errorMessage = "Failed to decode response as UTF-8."

                }
            case .failure(let error):
                self.errorMessage = "Failed to fetch description: \(error.localizedDescription)"
 
            }
        }
    }
}
