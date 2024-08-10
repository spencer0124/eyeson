//
//  ArtworkView.swift
//  eyeson
//
//  Created by 조승용 on 8/7/24.
//

import SwiftUI

struct ArtworkView: View {
    var body: some View {
        Text(/*@START_MENU_TOKEN@*/"Hello, World!"/*@END_MENU_TOKEN@*/)
        Image("artwork_example")
            .resizable()
            .scaledToFit()
            .padding(.horizontal, 40)
    
    }
}

#Preview {
    ArtworkView()
}
