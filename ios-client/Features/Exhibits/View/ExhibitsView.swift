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
        ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"),
//        ExhibitList(image: "image_museum", mainText: "abcd", subText1: "수원", subText2: "SKKU", subText3: "9.4-9.11"),
    ]
    
//    init(path: Binding<NavigationPath>) {
//            self._path = path
//        let appearance = UINavigationBarAppearance()
//                appearance.configureWithOpaqueBackground()
//        appearance.backgroundColor = .white
//                UINavigationBar.appearance().standardAppearance = appearance
//                UINavigationBar.appearance().scrollEdgeAppearance = appearance
//       
//        }
    
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
                                           HStack {
                                               Text(exhibit.subText1)
                                               Text("|")
                                               Text(exhibit.subText2)
                                               Text("|")
                                               Text(exhibit.subText3)
                                           }
                                           .font(.subheadline)
                                           .foregroundColor(.secondary)
                                       }
                                   }
                                   .padding(.vertical, 4)
                               }
                               
                           }
                       }
//                       .searchable(text: $searchText, placement: .navigationBarDrawer(displayMode: .always))
                       
                       Spacer()
                   }
               }
               
               .navigationBarTitle("전시관", displayMode: .large)
               .onAppear {
                   let result: () = locationpermissionManager.checkLocationPermission()
                   print(result)
               }
             
             
             
    
    
           
           .tint(.black)
        
}
}

#Preview {
    ExhibitsView()
}
