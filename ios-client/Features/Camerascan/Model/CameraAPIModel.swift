//
//  CameraAPIModel.swift
//  eyeson
//
//  Created by 조승용 on 9/1/24.
//

import Foundation

struct ImageSearchResponse: Decodable {
    let results: [SearchResult]
    
    struct SearchResult: Decodable {
        let rank: Int
        let file: String
    }
}
