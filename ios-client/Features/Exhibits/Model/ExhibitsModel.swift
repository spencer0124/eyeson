

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
    let ParamUniqueId: String
    let ParamExhibitName: String
    let ParamInfoUrl: String
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
