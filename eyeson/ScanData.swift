//
//  ScanData.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//

import Foundation

struct ScanData: Identifiable {
    var id = UUID()
    let content: String
    
    init(content:String) {
        self.content = content
    }
}
