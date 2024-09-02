//
//  ArtworkVM.swift
//  eyeson
//
//  Created by 조승용 on 9/2/24.
//
import SwiftUI
import Alamofire

class DescriptionViewModel: ObservableObject {
    @Published var descriptionText: String = ""
    @Published var explanationText: String = ""
    @Published var commentText: String = ""
    @Published var meta: [String: String] = [:]
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func fetchDescription(for file: String) {
        isLoading = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/get-description/"
        let parameters: [String: String] = ["file": file]
        
        AF.request(url, method: .post, parameters: parameters, encoding: JSONEncoding.default)
            .validate()
            .responseJSON { response in
                self.isLoading = false
                
                switch response.result {
                case .success(let data):
                    if let json = data as? [String: Any] {
                        self.descriptionText = json["description"] as? String ?? "No description available."
                        self.explanationText = json["explanation"] as? String ?? "No explanation available."
                        self.commentText = json["comment"] as? String ?? "No comment available."
                        self.meta = json["meta"] as? [String: String] ?? [:]
                    } else {
                        self.errorMessage = "Invalid response format."
                    }
                case .failure(let error):
                    self.errorMessage = "Failed to fetch description: \(error.localizedDescription)"
                }
            }
    }
}
