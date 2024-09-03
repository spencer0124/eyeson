//
//  ExhibitsDetailVM.swift
//  eyeson
//
//  Created by 조승용 on 9/3/24.
//


import Foundation
import Alamofire

class ExhibitsDetailViewModel: ObservableObject {
    @Published var exhibits: [ExhibitDetail] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    func fetchExhibits() {
        isLoading = true
        errorMessage = nil
        
        let url = "http://43.201.93.53:8000/images-with-metadata/"
        
        AF.request(url).responseJSON { response in
            self.isLoading = false
            
            switch response.result {
            case .success(let data):
                if let json = data as? [String: Any], let images = json["images"] as? [[String: Any]] {
                    self.exhibits = images.compactMap { dict in
                        guard let file = dict["file"] as? String,
                              let title = dict["title"] as? String,
                              let artist = dict["artist"] as? String,
                              let imageUrl = dict["image_url"] as? String else {
                            return nil
                        }
                        return ExhibitDetail(id: file, title: title, artist: artist, imageUrl: imageUrl)
                    }
                } else {
                    self.errorMessage = "Invalid response format."
                }
            case .failure(let error):
                self.errorMessage = "Failed to fetch exhibits: \(error.localizedDescription)"
            }
        }
    }
}

struct ExhibitDetail: Identifiable {
    let id: String
    let title: String
    let artist: String
    let imageUrl: String
}
