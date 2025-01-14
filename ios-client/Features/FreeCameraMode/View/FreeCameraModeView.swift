//
//  FreeCameraModeView.swift
//  eyeson
//
//  Created by SeungYong on 1/14/25.
//

import SwiftUI



struct FreeCameraModeView: View {
    var image: UIImage?

    var body: some View {
        if let image = image {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
        } else {
            Text("No image received")
        }
        Text("This is the custom camera mode view.")
    }
}

#Preview {
    FreeCameraModeView()
}
