//
//  ExhibitsDetailModel.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import Foundation
import SwiftUI

struct ExhibitDetailList: Identifiable {
    let id = UUID()
    let image: String
    let mainText: String
    let subText: String
}
