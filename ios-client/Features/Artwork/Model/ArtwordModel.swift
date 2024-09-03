//
//  ArtwordModel.swift
//  eyeson
//
//  Created by 조승용 on 9/2/24.
//

import Foundation

// Request model
struct RequestBody: Encodable {
    let file: String
}

// Response model
struct APIResponse: Decodable {
    let eng_id: String
    let description: String
    let explanation: String
    let comment: String
    let meta: Meta
    let 음성url: String
}

struct Meta: Decodable {
    let title: String
    let artist: String
    let style: String
    let emotion: String
}
