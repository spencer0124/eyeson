//
//  ArtworkDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/10/24.
//


import SwiftUI
import UIKit
import SwiftUIImageViewer
import Shimmer
import Lottie

struct ArtworkDetailView: View {
    var eng_id: String
    
    @Environment(\.presentationMode) var presentationMode
    @State private var isBottomSheetPresented = false

    var body: some View {
                ZStack {
                    Color.white

                    SwiftUIImageViewer(image: image)
//                        .overlay(alignment: .topTrailing) {
//                                                    closeButton
//                                                }

                    VStack {
                        Spacer()
                        Button(action: {
                            withAnimation {
                                isBottomSheetPresented = true
                            }
                        }, label: {
                            Text("해설 요청하기")
                                .font(.system(size: 15))
                                .foregroundColor(.white)
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .background(Color.gray)
                                .cornerRadius(10)
                        })
                        Spacer()
                            .frame(height: 100)
                    }
                }
                .overlay(
                    VStack {
                        Spacer()
                        if isBottomSheetPresented {
                            bottomSheet
                                .transition(.move(edge: .bottom))
                                .animation(.easeInOut)
                        }
                        
                    }
                )
    }
    

    private var image: Image {
        Image("artwork_example")
    }

    private var closeButton: some View {
        Button {
            // action
        } label: {
            Image(systemName: "xmark")
                .font(.headline)
        }
        .buttonStyle(.bordered)
        .clipShape(Circle())
        .tint(.purple)
        .padding()
    }

    private var bottomSheet: some View {
        VStack(alignment: .leading) {
            HStack {
                Spacer()
                Button(action: {
                    withAnimation {
                            isBottomSheetPresented = false
                        }
                                }) {
                                    Image(systemName: "xmark")
                                        .foregroundColor(.black)
                                        .padding()
                                        .background(Color.white)
                                        .cornerRadius(15)
                                }
            }
            
            
            HStack {
                Spacer()
                LottieView(animation: .named("lottie_scan2"))
                    .playbackMode(.playing(.fromProgress(0, toProgress: 1.0, loopMode: .loop)))
                    .resizable()
                    .scaledToFit()
                    .frame(width: 280)
                Spacer()
            }
            
            
            HStack {
                Spacer()
                Text("그림 분석중...")
                    .font(.system(size: 25))
                    .foregroundColor(.gray)
                    .shimmering(
                        active: true,
                        animation: .easeInOut(duration: 2).repeatForever(),
                        bandSize: 5.5
                    )
                    
                Spacer()
            }
            
                       

            
           
            Spacer()
                .frame(height: 60)
        }
        .frame(width: UIScreen.main.bounds.width, height: UIScreen.main.bounds.height / 3)
        .background(Color.white)
        .cornerRadius(20)
        .shadow(radius: 20)
//        .ignoresSafeArea(edges: .bottom)
        
    }
}

#Preview {
    ArtworkDetailView(eng_id: "photo/JeongyeonMoon_Golden.jpg")
}
