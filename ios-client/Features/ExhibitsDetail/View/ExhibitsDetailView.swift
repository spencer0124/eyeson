//
//  ExhibitsDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI
import Glur

struct ExhibitsDetailView: View {
    
    @State private var searchText = ""
    @State private var isExhibitInfoSheetPresented = false
    
   
    
    
    
    var exhibit: ExhibitList
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            
            ZStack {
                VStack {
                    Image("image_exhibition")
                        .resizable()
                        .scaledToFit()
                        .glur(radius: 10.0, // The total radius of the blur effect when fully applied.
                              offset: 0.1, // The distance from the view's edge to where the effect begins, relative to the view's size.
                              interpolation: 0.5, // The distance from the offset to where the effect is fully applied, relative to the view's size.
                              direction: .up // The direction in which the effect is applied.
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
                        CustomButtonsView(isExhibitInfoSheetPresented: $isExhibitInfoSheetPresented)
                        Spacer()
                            .frame(width: 18)
                    }
                    
                    
                    List {
                        ForEach(exhibitDetails) { exhibitDetail in  // 여기서 exhibitDetails 배열을 사용합니다.
                            NavigationLink(destination: ArtworkDetailView()) {
                                HStack {
                                    Image(exhibitDetail.id)  // 이미지 파일명을 id로 사용
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
                            .navigationBarBackButtonHidden(true)
                        }
                    }
                    .listStyle(PlainListStyle())
                    //                .searchable(text: $searchText, placement: .navigationBarDrawer(displayMode: .always))
                    
                    Spacer()
                }
                //            VStack {
                //                HStack {
                //                    Spacer()
                //                        .frame(width: 15)
                //                    Button(action: {
                //                        presentationMode.wrappedValue.dismiss()
                //                    }) {
                //                        Image(systemName: "chevron.left")
                //                            .font(.system(size: 18))
                //                            .foregroundColor(.clear)
                //                    }
                //
                //                    Spacer()
                //
                //                    Text(exhibit.mainText)
                //                        .font(.system(size: 18))
                //                        .fontWeight(.bold)
                ////                        .foregroundColor(.black)
                //
                //                    Spacer()
                //
                //                    Button(action: {
                //                        // Empty action
                //                    }) {
                //                        Image(systemName: "chevron.left")
                //                            .font(.system(size: 18))
                //                            .foregroundColor(.clear) // Invisible button
                //                    }
                //                    Spacer()
                //                        .frame(width: 15)
                //                }
                //
                //                .foregroundColor(.white)
                //                .padding(.top, (UIApplication.shared.windows.first?.safeAreaInsets.top ?? 0) + 5) // Add safe area space
                //                Spacer()
                //            }
                
                
            }
            .toolbar(.hidden)
            .ignoresSafeArea()
            .navigationBarBackButtonHidden(true)
        }
        .sheet(isPresented: $isExhibitInfoSheetPresented) {
            ExhibitInfoSheet()
        }
    }
    
   
    
    struct CustomButtonsView: View {
        @Environment(\.presentationMode) var presentationMode
        @Binding var isExhibitInfoSheetPresented: Bool
        
        var body: some View {
            HStack(spacing: 0) {
                
                Button(action: {
                    isExhibitInfoSheetPresented = true
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
    
    struct ExhibitInfoSheet: View {
        @Environment(\.presentationMode) var presentationMode
        
        var body: some View {
            VStack {
                HStack {
                    Spacer()
                    Button(action: {
                        presentationMode.wrappedValue.dismiss()
                    }) {
                        Text("취소")
                            .foregroundColor(.blue)
                    }
                    .padding()
                }
                
                Text("전시정보")
                    .font(.largeTitle)
                    .padding()
                
                // 전시 정보 내용
                Spacer()
            }
        }
    }
}

#Preview {
    ExhibitsDetailView(exhibit: ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"))
}
