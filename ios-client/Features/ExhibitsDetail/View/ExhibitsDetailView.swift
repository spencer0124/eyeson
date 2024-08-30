//
//  ExhibitsDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI
import Glur

struct ExhibitsDetailView: View {
    @State private var isNavigatingToExhibitInfo = false
    var exhibit: ExhibitList

    var body: some View {
        ZStack {
            VStack {
                Image("image_exhibition")
                    .resizable()
                    .scaledToFit()
                    .glur(radius: 10.0,
                          offset: 0.1,
                          interpolation: 0.5,
                          direction: .up
                    )
                    .overlay(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.black.opacity(0.5), Color.clear]),
                            startPoint: .top,
                            endPoint: .center
                        )
                    )
                
                Spacer()
                    .frame(height: 20)
   
                HStack {
                    Spacer()
                        .frame(width: 18)
                    Rectangle()
                        .frame(width: 4, height: 26)
                        .foregroundColor(.gray)
                    Text(exhibit.mainText)
                        .font(.system(size: 20))
                        .fontWeight(.bold)
                    Spacer()
                    CustomButtonsView(isNavigatingToExhibitInfo: $isNavigatingToExhibitInfo)
                    Spacer()
                        .frame(width: 18)
                }
                
                List {
                    ForEach(exhibitDetails) { exhibitDetail in
                        NavigationLink(destination: ArtworkDetailView()) {
                            HStack {
                                Image(exhibitDetail.id)
                                    .resizable()
                                    .scaledToFit()
                                    .frame(width: 65, height: 55)
                                Spacer()
                                    .frame(width: 20)
                                VStack(alignment: .leading) {
                                    Text(exhibitDetail.meta.title)
                                        .font(.headline)
                                    HStack {
                                        Text(exhibitDetail.meta.artist)
                                    }
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
                .listStyle(PlainListStyle())
                
                Spacer()
            }
            
            .background(
                NavigationLink(
                    destination: ExhibitInfoView(exhibit: exhibit),
                    isActive: $isNavigatingToExhibitInfo,
                    label: { EmptyView() }
                )
            )
            
        }
        .navigationTitle("작품 목록")
        .navigationBarTitleDisplayMode(.inline)
        
        .ignoresSafeArea()
    }
    
    struct CustomButtonsView: View {
        @Binding var isNavigatingToExhibitInfo: Bool
        
        var body: some View {
            Button(action: {
                isNavigatingToExhibitInfo = true
            }) {
                HStack(spacing: 2) {
                    Image(systemName: "info.circle")
                        .foregroundColor(Color.customGray1)
                    Text("전시정보")
                        .font(.system(size: 14))
                        .foregroundColor(Color.customGray1)
                }
            }
        }
    }
}

struct ExhibitInfoView: View {
    var exhibit: ExhibitList
    
    var body: some View {
        VStack {
           
            Text(exhibit.mainText)
                .font(.largeTitle)
                .padding()
            
            // Insert additional exhibit information here
            Text("Details about the exhibit will be shown here.")
                .padding()
            
            Spacer()
        }
        .navigationTitle("전시정보")
    }
}

#Preview {
    ExhibitsDetailView(exhibit: ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"))
}

