//
//  ArtworkView.swift
//  eyeson
//
//  Created by 조승용 on 8/7/24.
//

import SwiftUI

struct ArtworkView: View {
    var eng_id: String
    
    @StateObject private var viewModel = DescriptionViewModel()

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
                        Image("artwork_example")
                            .resizable()
                            .scaledToFit()
                            .cornerRadius(12)
                            .frame(width: 260, height: 260)
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
        .navigationTitle("\(viewModel.meta["title"] ?? "Unknown Title")")
        .onAppear {
            viewModel.fetchDescription(for: eng_id)
        }
    }
}

#Preview {
    ArtworkView(eng_id: "ByeongyunLee_Bird.JPG")
}
