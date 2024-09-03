//
//  ArtworkView.swift
//  eyeson
//
//  Created by 조승용 on 8/7/24.
//

import SwiftUI
import UIKit
import SwiftUIImageViewer
import Kingfisher

struct ArtworkView: View {
    var eng_id: String
    
    @StateObject private var viewModel = DescriptionViewModel()
    @Environment(\.presentationMode) var presentationMode
    @State private var isImagePresented = false
    @State private var isBottomSheetPresented = false

    var body: some View {
        
        ScrollView {
        VStack(alignment: .leading, spacing: 0) {
            if viewModel.isLoading {
                ProgressView("로딩중...")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
            } else {
                
                VStack (alignment: .leading, spacing: 5) {
                    HStack {
                        
                        Text("\(viewModel.meta["artist"] ?? "작가 정보 없음")")
                            .font(.headline)
                        
                        Text("\(viewModel.meta["emotion"] ?? "감정 정보 없음")")
                            .font(.subheadline)
                    }
                    
                    Text("\(viewModel.meta["style"] ?? "스타일 정보 없음")")
                        .font(.subheadline)
                    
                    Spacer()
                        .frame(height: 15)
                }
                
                
                VStack (alignment: .leading, spacing: 20) {
                    
                    Divider()
                
                    HStack {
                        Spacer()
                        KFImage(URL(string: viewModel.image_url))
                                .placeholder {
                                ProgressView()
                                    .frame(width: 65, height: 55)
                                }
                                .resizable()
                                .scaledToFit()
                                .cornerRadius(12)
                                .padding()
                                .onTapGesture {
                                            isImagePresented = true
                                        }
                                .fullScreenCover(isPresented: $isImagePresented) {
                                    ZStack {
                                            Color.white
                                        SwiftUIImageViewer(imageURLString: viewModel.image_url)
                                                .overlay(alignment: .topTrailing) {
                                                    closeButton
                                                }
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
                        Spacer()
                    }
                    
                    
                    Divider()
                    
                    Text("**한 줄 설명**")
                        .font(.headline)
                    Text(viewModel.explanationText)
                        .padding(.bottom, 10)
                    
                    Text("**작품 묘사**")
                        .font(.headline)
                    Text(viewModel.descriptionText)
                        .padding(.bottom, 10)
                    
                    
                    Text("**작품 해설**")
                        .font(.headline)
                    Text(viewModel.commentText)
                        .padding(.bottom, 10)
                }
                
                
            }
        }
        .padding()
    }
        .navigationTitle("\(viewModel.meta["title"] ?? " ")")
        .onAppear {
            viewModel.fetchDescription(for: eng_id)
        }
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
    
    
    private var image: Image {
        Image("artwork_example")
    }


    private var bottomSheet: some View {
            VStack(alignment: .leading) {
//                HStack {
//                    Spacer()
//                    Button(action: {
//                        withAnimation {
//                                isBottomSheetPresented = false
//                            }
//                                    }) {
//                                        Image(systemName: "xmark")
//                                            .foregroundColor(.black)
//                                            .padding()
//                                            .background(Color.white)
//                                            .cornerRadius(15)
//                                    }
//                }
//                
                
                
                HStack {
                    Spacer()
                    ProgressView("해설 불러오는 중")
                    Spacer()
                }
                
                           

                
               
                Spacer()
                    .frame(height: 60)
            }
            .frame(width: UIScreen.main.bounds.width, height: UIScreen.main.bounds.height / 3)
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 20)
            .ignoresSafeArea()
        }

}



#Preview {
    ArtworkView(eng_id: "ByeongyunLee_Bird.JPG")
}
