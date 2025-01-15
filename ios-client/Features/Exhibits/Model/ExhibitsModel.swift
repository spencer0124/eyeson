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
    let endDate: Date
}

struct ExhibitInfoResponse: Decodable {
    let exhibits: [Exhibit]
}

struct Exhibit: Decodable {
    let id: String
    let img: String
    let name: String
    let place: String
    let gallery: String
    let startYear: String
    let startMonth: String
    let startDay: String
    let EndYear: String
    let EndMonth: String
    let EndDay: String
    let info: String
}
