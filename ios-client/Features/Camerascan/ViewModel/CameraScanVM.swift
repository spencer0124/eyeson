//
//  CameraScanVM.swift
//  eyeson
//
//  Created by 조승용 on 9/1/24.
//
import Foundation
import Alamofire

class ImageSearchViewModel: ObservableObject {
    @Published var searchResults: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func searchImage(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            errorMessage = "Failed to convert image to JPEG."
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/search/?uniqueid=2023test"
        
        let headers: HTTPHeaders = [
            "Content-Type": "multipart/form-data"
        ]
        
        AF.upload(multipartFormData: { multipartFormData in
            multipartFormData.append(imageData, withName: "file", fileName: "image.jpg", mimeType: "image/jpeg")
        }, to: url, headers: headers)
        .responseJSON { response in
            self.isLoading = false
            
            print("Full response: \(response)")
            
            switch response.result {
            case .success(let data):
                if let json = data as? [String: Any],
                   let results = json["results"] as? [[String: Any]] {
                    // Extract the file name where rank is 1
                    if let rank1Result = results.first(where: { $0["rank"] as? Int == 1 }),
                       let fileName = rank1Result["file"] as? String {
                        self.searchResults = fileName.replacingOccurrences(of: "photo/", with: "")
                    } else {
                        self.errorMessage = "Rank 1 file not found."
                    }
                } else {
                    self.errorMessage = "Invalid response format."
                }
            case .failure(let error):
                self.errorMessage = "Failed to upload image: \(error.localizedDescription)"
                print("Error: \(error.localizedDescription)") // Print the error message
            }
        }
    }
}
