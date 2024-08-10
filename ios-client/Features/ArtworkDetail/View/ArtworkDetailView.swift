//
//  ArtworkDetailView.swift
//  eyeson
//
//  Created by 조승용 on 8/10/24.
//
import SwiftUI
import UIKit
import SwiftUIImageViewer


struct ArtworkDetailView: View {
    
    
    @State private var isImagePresented = false

    var body: some View {
        image
            .resizable()
            .scaledToFit()
            .cornerRadius(12)
            .frame(width: 260, height: 260)
            .onTapGesture {
                isImagePresented = true
            }
            .fullScreenCover(isPresented: $isImagePresented) {
                ZStack {
                    Color.black
                                    .edgesIgnoringSafeArea(.all)
                    SwiftUIImageViewer(image: image)
                        .overlay(alignment: .topTrailing) {
                            closeButton
                        }
                    VStack {
                        Spacer()
                        Button(action: {
                            print("Hello is HoonIOS")
                        }, label: {
                            Text("해설 요청하기")
                                .foregroundColor(.white) // 글씨를 흰색으로 설정
                                .padding() // 버튼 내부 여백 추가
                                .background(Color.blue) // 배경색을 파란색으로 설정
                                .cornerRadius(10) // 모서리를 둥글게
                        })
                        Spacer()
                            .frame(height: 100)
                    }
                    
                }
                
            }
    }

    private var image: Image {
        Image("artwork_example")
    }

    private var closeButton: some View {
        Button {
            isImagePresented = false
        } label: {
            Image(systemName: "xmark")
                .font(.headline)
        }
        .buttonStyle(.bordered)
        .clipShape(Circle())
        .tint(.purple)
        .padding()
    }

    
}



#Preview {
    ArtworkDetailView()
}
