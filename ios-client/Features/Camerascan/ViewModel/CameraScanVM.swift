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
    
    // Array to store exhibit IDs and names
    @Published var exhibitInfo: [(id: String, name: String)] = []
    // 전시관 이름을 저장할 배열 추가
    @Published var exhibitNames: [String] = []
    
    func fetchExhibitInfo() {
            let url = "http://43.201.93.53:8000/metadata/exhibit-info/"

            AF.request(url)
                .responseDecodable(of: ExhibitInfoResponse.self) { response in
                    switch response.result {
                    case .success(let data):
                        // Extract id and name from the response
                        self.exhibitInfo = data.exhibits.map { ($0.id, $0.name) }
                        
                        self.exhibitInfo.sort { $0.name < $1.name }
                        
                        // 전시관 이름만 추출하여 exhibitNames에 저장
                        self.exhibitNames = self.exhibitInfo.map { $0.name }
                        
                        print("Exhibit Info: \(self.exhibitInfo)") // Print the fetched data
                        print("Exhibit Names: \(self.exhibitNames)") // Print the fetched names
                    case .failure(let error):
                        print("Error fetching exhibit info: \(error)")
                    }
                }
        }


    func searchImage(image: UIImage, uniqueId: String) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            errorMessage = "Failed to convert image to JPEG."
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/search/?uniqueid=\(uniqueId)"
        
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
