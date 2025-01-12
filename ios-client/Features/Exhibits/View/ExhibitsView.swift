//
//  ExhibitsView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI

struct ExhibitsView: View {
    @StateObject private var locationpermissionManager = LocationPermissionManager()
    @State private var searchText = ""
    
    let exhibits: [ExhibitList] = [
        ExhibitList(image: "image_museum", mainText: "나의 모든 순간", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"),
//        ExhibitList(image: "image_museum", mainText: "abcd", subText1: "수원", subText2: "SKKU", subText3: "9.4-9.11"),
    ]
    
    
    var body: some View {
        
          
               ZStack {
                   Color("backgroundColor")
                       .ignoresSafeArea()
                   VStack {
                       List {
                           ForEach(exhibits.filter { searchText.isEmpty ? true : $0.mainText.contains(searchText) || $0.subText1.contains(searchText) || $0.subText2.contains(searchText) || $0.subText3.contains(searchText) }) { exhibit in
                               NavigationLink(destination: ExhibitsDetailView(exhibit: exhibit)) {
                                   HStack {
                                       Image(exhibit.image)
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
                                               Text("|")
                                                   .accessibilityHidden(true)
                                               Text(exhibit.subText3)
                                                   .accessibilityLabel("전시기간: \(dateAccessibilityLabel(for: exhibit.subText3))")
                                           }
                                           .font(.subheadline)
                                           .foregroundColor(.black)
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
                   let result: () = locationpermissionManager.checkLocationPermission()
                   print(result)
               }
           .tint(.black)
        
}
    
    func dateAccessibilityLabel(for dateText: String) -> String {
        // 날짜 형식이 "9.4-9.11"이라 가정하고 처리
        let components = dateText.split(separator: "-")
        if components.count == 2 {
            let start = components[0].replacingOccurrences(of: ".", with: "월 ") + "일"
            let end = components[1].replacingOccurrences(of: ".", with: "월 ") + "일"
            return "\(start)부터 \(end)까지"
        }
        return dateText // 기본적으로 원래 텍스트를 반환
    }

}

#Preview {
    ExhibitsView()
}
