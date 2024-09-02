//
//  CameraScanVM.swift
//  eyeson
//
//  Created by 조승용 on 9/1/24.
//
import Foundation
import Alamofire

class ImageSearchViewModel: ObservableObject {
    @Published var searchResults: [String] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func searchImage(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            errorMessage = "Failed to convert image to JPEG."
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/search/"
        
        let headers: HTTPHeaders = [
            "Content-Type": "multipart/form-data"
        ]
        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(imageData, withName: "file", fileName: "image.jpg", mimeType: "image/jpeg")
        }, to: url, headers: headers)
        .responseString { response in
            self.isLoading = false
            
            switch response.result {
            case .success(let data):
                // Assuming that the API returns a single string result
                self.searchResults = [data]
                print("Search Results: \(data)") // Print the raw string response
            case .failure(let error):
                self.errorMessage = "Failed to upload image: \(error.localizedDescription)"
                print("Error: \(error.localizedDescription)") // Print the error message
            }
        }
    }
}
