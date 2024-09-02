//
//  ArtworkView.swift
//  eyeson
//
//  Created by 조승용 on 8/7/24.
//

import SwiftUI

struct ArtworkView: View {
    @StateObject private var viewModel = DescriptionViewModel()
    let fileId: String
    
    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let errorMessage = viewModel.errorMessage {
                Text("Error: \(errorMessage)")
                    .foregroundColor(.red)
            } else if let response = viewModel.apiResponse {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Title: \(response.meta.title)")
                        .font(.headline)
                    Text("Artist: \(response.meta.artist)")
                    Text("Style: \(response.meta.style)")
                    Text("Emotion: \(response.meta.emotion)")
                    Text("Description: \(response.description)")
                    Text("Explanation: \(response.explanation)")
                    Text("Comment: \(response.comment)")
                    Text("Audio URL: \(response.음성url)")
                        .foregroundColor(.blue)
                        .onTapGesture {
                            if let url = URL(string: response.음성url) {
                                UIApplication.shared.open(url)
                            }
                        }
                }
                .padding()
            }
        }
        .onAppear {
            viewModel.fetchDescription(fileId: fileId)
        }
        .navigationTitle("작품명 어쩌구 모나리자")
    }
}

#Preview {
    ArtworkView(fileId: "sample_file_id")
}
