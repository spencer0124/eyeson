//
//  ExhibitsDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI
import Glur

struct ExhibitsDetailView: View {
    

    
    var exhibit: ExhibitList
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        ZStack {
            VStack {
                Image("image_exhibition")
                    .resizable()
                    .scaledToFit()
                    .glur(radius: 10.0, // The total radius of the blur effect when fully applied.
                          offset: 0.3, // The distance from the view's edge to where the effect begins, relative to the view's size.
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
                CustomButtonsView()
                HStack{
                    Spacer()
                        .frame(width: 20)
                    Text("작품 목록 100개")
                        .font(.system(size: 16))
                        .fontWeight(.regular)
                    Spacer()
                }
                
                Spacer()
            }
            VStack {
                HStack {
                    Spacer()
                        .frame(width: 15)
                    Button(action: {
                        presentationMode.wrappedValue.dismiss()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18))
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    Text(exhibit.mainText)
                        .font(.system(size: 18))
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Button(action: {
                        // Empty action
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18))
                            .foregroundColor(.clear) // Invisible button
                    }
                    Spacer()
                        .frame(width: 15)
                }
            
                        .foregroundColor(.white)
                        .padding(.top, (UIApplication.shared.windows.first?.safeAreaInsets.top ?? 0) + 5) // Add safe area space
                    Spacer()
                }

                
            }
            .ignoresSafeArea()
            .navigationBarBackButtonHidden(true)
           
    }
   }

   #Preview {
       ExhibitsDetailView(exhibit: ExhibitList(image: "image_museum", mainText: "Every Moment of Mine", subText1: "서울", subText2: "노들갤러리", subText3: "9.4-9.11"))
   }

struct CustomButtonsView: View {
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        HStack(spacing: 0) {
            
            Button(action: {
                // Action for "전시정보"
            }) {
                VStack {
                    Image(systemName: "photo")
                        .font(.system(size: 24))
                        .foregroundColor(Color.gray.opacity(1.2))
                    Text("전시정보")
                        .font(.system(size: 14))
                }
                .padding(.vertical, 10)
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(width: 1, height: 40)
                .background(Color.gray)
            
            Button(action: {
                // Action for "장소정보"
            }) {
                VStack {
                    Image(systemName: "location.circle")
                        .font(.system(size: 24))
                    Text("장소정보")
                        .font(.system(size: 14))
                }
                .padding(.vertical, 10)
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(width: 1, height: 40)
                .background(Color.gray)
            
            Button(action: {
                // Action for "작가정보"
            }) {
                VStack {
                    Image(systemName: "pencil.line")
                        .font(.system(size: 24))
                    Text("작가정보")
                        .font(.system(size: 14))
                }
                .padding(.vertical, 10)
            }
            .frame(maxWidth: .infinity)
            
            Divider()
                .frame(width: 1, height: 40)
                .background(Color.gray)
            
            Button(action: {
                presentationMode.wrappedValue.dismiss()
            }) {
                VStack {
                    Image(systemName: "info.circle")
                        .font(.system(size: 24))
                    Text("저작권")
                        .font(.system(size: 14))
                }
                .padding(.vertical, 10)
            }
            .frame(maxWidth: .infinity)
        }

        .background(Color.white)
        .padding(.horizontal)
        
    }
        
}
