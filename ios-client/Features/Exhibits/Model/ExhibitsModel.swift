//
//  ExhibitsModel.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import Foundation
import SwiftUI

struct ExhibitList: Identifiable {
    let id = UUID()
    let image: String
    let mainText: String
    let subText1: String
    let subText2: String
    let subText3: String
}
