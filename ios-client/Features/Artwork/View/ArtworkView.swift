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
        VStack(alignment: .leading, spacing: 20) {
            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
            } else {
                Text("**Title:** \(viewModel.meta["title"] ?? "Unknown Title")")
                    .font(.title)
                
                Text("**Artist:** \(viewModel.meta["artist"] ?? "Unknown Artist")")
                    .font(.headline)
                
                Text("**Style:** \(viewModel.meta["style"] ?? "Unknown Style")")
                    .font(.subheadline)
                
                Text("**Emotion:** \(viewModel.meta["emotion"] ?? "Unknown Emotion")")
                    .font(.subheadline)
                
                Divider()
                
                Text("**Description**")
                    .font(.headline)
                Text(viewModel.descriptionText)
                    .padding(.bottom, 10)
                
                Text("**Explanation**")
                    .font(.headline)
                Text(viewModel.explanationText)
                    .padding(.bottom, 10)
                
                Text("**Comment**")
                    .font(.headline)
                Text(viewModel.commentText)
                    .padding(.bottom, 10)
            }
        }
        .padding()
        .navigationTitle("Artwork Details")
        .onAppear {
            viewModel.fetchDescription(for: eng_id)
        }
    }
}

#Preview {
    ArtworkView(eng_id: "ByeongyunLee_Bird.JPG")
}
