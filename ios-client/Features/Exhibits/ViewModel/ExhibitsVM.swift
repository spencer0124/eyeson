//
//  ExhibitsVM.swift
//  eyeson
//
//  Created by SeungYong on 1/16/25.
//

import Foundation
import Alamofire

class ExhibitsVM: ObservableObject {
    @Published var exhibitLists: [ExhibitList] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func fetchExhibits() {
        isLoading = true
        errorMessage = nil

        AF.request("http://43.201.93.53:8000/metadata/exhibit-info/")
            .validate()
            .responseDecodable(of: ExhibitInfoResponse.self) { response in
                defer { self.isLoading = false }

                switch response.result {
                case .success(let data):
//                    print("data: \(data)")
                    self.exhibitLists = data.exhibits.map { exhibit in
                        ExhibitList(
                            image: exhibit.img,
                            mainText: exhibit.name,
                            subText1: exhibit.place,
                            subText2: exhibit.gallery,
                            subText3: "\(exhibit.startYear).\(exhibit.startMonth).\(exhibit.startDay)-\(exhibit.EndYear).\(exhibit.EndMonth).\(exhibit.EndDay)",
                            endDate: Calendar.current.date(from: DateComponents(year: Int(exhibit.EndYear), month: Int(exhibit.EndMonth), day: Int(exhibit.EndDay))) ?? Date(), // endDate 계산,
                            ParamUniqueId: exhibit.id,
                            ParamExhibitName: exhibit.name,
                            ParamInfoUrl: exhibit.info
                        )
                    }
                case .failure(let error):
                    self.errorMessage = "데이터를 가져오는 중 오류가 발생했습니다.\n\(error.localizedDescription)"
                }
            }
    }
}
