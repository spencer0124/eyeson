//
//  CameraScanVM.swift
//  eyeson
//
//  Created by 조승용 on 9/1/24.
//

import Foundation
import Alamofire

class ImageSearchViewModel: ObservableObject {
    @Published var searchResults: [ImageSearchResponse.SearchResult] = []
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
        .validate()
        .responseDecodable(of: ImageSearchResponse.self) { response in
            self.isLoading = false
            
            switch response.result {
            case .success(let data):
                self.searchResults = data.results
            case .failure(let error):
                self.errorMessage = "Failed to upload image: \(error.localizedDescription)"
            }
        }
    }
}
