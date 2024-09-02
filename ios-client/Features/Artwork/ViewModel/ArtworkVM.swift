//
//  ArtworkVM.swift
//  eyeson
//
//  Created by 조승용 on 9/2/24.
//

import Foundation
import Alamofire

class DescriptionViewModel: ObservableObject {
    @Published var apiResponse: APIResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func fetchDescription(fileId: String) {
        let url = "http://43.201.93.53:8000/get-description"
        let parameters = RequestBody(file: fileId)
        
        isLoading = true
        
        AF.request(url, method: .post, parameters: parameters, encoder: JSONParameterEncoder.default).responseDecodable(of: APIResponse.self) { response in
            DispatchQueue.main.async {
                self.isLoading = false
                switch response.result {
                case .success(let data):
                    self.apiResponse = data
                case .failure(let error):
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }
}
