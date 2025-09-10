

import SwiftUI
import Kingfisher

struct ExhibitsView: View {
    @StateObject private var viewModel = ExhibitsVM()
    @StateObject private var locationpermissionManager = LocationPermissionManager()
    @State private var searchText = ""
    @State private var sortOrder: SortOrder = .title // 기본값: 전시제목 순
    
    enum SortOrder {
            case title, deadline
        }

    
    var body: some View {
               ZStack {
                   Color("backgroundColor")
                       .ignoresSafeArea()
                   VStack {
                       Picker("정렬 기준", selection: $sortOrder) {
                                   Text("전시제목 순서").tag(SortOrder.title)
                                   Text("마감일 순서").tag(SortOrder.deadline)
                               }
                               .pickerStyle(SegmentedPickerStyle())
                               .padding(.horizontal)
                               
                       
                       List {
                           ForEach(filteredAndSortedExhibits) { exhibit in
                               NavigationLink(destination: ExhibitsDetailView(exhibit: exhibit)) {
                                   HStack {
                                       KFImage(URL(string: exhibit.image))
                                           .resizable()
                                           .scaledToFit()
                                           .frame(width: 65, height: 65)
                                       Spacer()
                                           .frame(width: 20)
                                       VStack(alignment: .leading) {
                                           Text(exhibit.mainText)
                                               .font(.headline)
                                               .accessibilityLabel("전시제목: \(exhibit.mainText)")
                                           HStack {
                                               Text(exhibit.subText1)
                                                   .accessibilityLabel("전시장소: \(exhibit.subText1)")
                                               Text("|")
                                                   .accessibilityHidden(true)
                                               Text(exhibit.subText2)
                                                   .accessibilityLabel("전시갤러리: \(exhibit.subText2)")
//                                               Text("|")
//                                                   .accessibilityHidden(true)
                                               
                                           }
                                           .font(.caption)
                                           .foregroundColor(.black)
                                           Text(exhibit.subText3)
                                               .font(.caption)
                                               .foregroundColor(.black)
                                               .accessibilityLabel("전시기간: \(dateAccessibilityLabel(for: exhibit.subText3))")
                                       }
                                   }
                                   .padding(.vertical, 4)
                               }
                               
                               
                           }
                       }
                       .searchable(text: $searchText, placement: .navigationBarDrawer(displayMode: .always), prompt: "전시관 검색하기")
                       
                       Spacer()
                   }
               }
               .navigationTitle("전시관")
               .navigationBarTitleDisplayMode(.large)
              
               .onAppear {
                   viewModel.fetchExhibits()
                   let result: () = locationpermissionManager.checkLocationPermission()
//                   print(result)
                   
                   
               }
           .tint(.black)
        
    }
    
    var filteredAndSortedExhibits: [ExhibitList] {
        viewModel.exhibitLists
            .filter { searchText.isEmpty ? true : $0.mainText.contains(searchText) || $0.subText1.contains(searchText) || $0.subText2.contains(searchText) || $0.subText3.contains(searchText) }
            .sorted {
                switch sortOrder {
                case .title:
                    return $0.mainText < $1.mainText
                case .deadline:
                    return $0.endDate < $1.endDate
                }
            }
    }
    
    func dateAccessibilityLabel(for dateText: String) -> String {
        // 날짜 형식이 "24.09.04-24.09.11" 형식으로 변경됨
        let components = dateText.split(separator: "-")
        if components.count == 2 {
            let startComponents = components[0].split(separator: ".")
            let endComponents = components[1].split(separator: ".")
            if startComponents.count == 3 && endComponents.count == 3 {
                let start = "\(startComponents[0])년 \(startComponents[1])월 \(startComponents[2])일"
                let end = "\(endComponents[0])년 \(endComponents[1])월 \(endComponents[2])일"
                return "\(start)부터 \(end)까지"
            }
        }
        return dateText // 기본적으로 원래 텍스트를 반환
    }

}

#Preview {
    ExhibitsView()
}
