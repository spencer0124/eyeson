
//
//import SwiftUI
//import UIKit
//import SwiftUIImageViewer
//import Kingfisher
//
//struct FullScreenImageView: View {
//    let imageURL: String
//    @Binding var isImagePresented: Bool
//    
//    var body: some View {
//        ZStack {
//            Color.white
//            SwiftUIImageViewer(imageURLString: imageURL)
//                .overlay(alignment: .topTrailing) {
//                    closeButton
//                }
//            VStack {
//                Spacer()
//                Button(action: {
//                    // Action to handle when the button is pressed
//                }, label: {
//                    Text("해설 요청하기")
//                        .font(.system(size: 15))
//                        .foregroundColor(.white)
//                        .padding(.horizontal, 20)
//                        .padding(.vertical, 10)
//                        .background(Color.gray)
//                        .cornerRadius(10)
//                })
//                Spacer()
//                    .frame(height: 100)
//            }
//        }
//    }
//    
//    private var closeButton: some View {
//        Button {
//            isImagePresented = false
//        } label: {
//            Image(systemName: "xmark")
//                .font(.headline)
//        }
//        .buttonStyle(.bordered)
//        .clipShape(Circle())
//        .tint(.purple)
//        .padding()
//    }
//}
