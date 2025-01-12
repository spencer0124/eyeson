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
    @State private var capturedImage: UIImage? = nil
   

    var body: some View {
        
        ScrollView {
        VStack(alignment: .leading, spacing: 0) {
            if viewModel.isLoadingFetchDescription {
                ProgressView("로딩중")
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
            } else {
                
                VStack (alignment: .leading, spacing: 5) {
                    HStack {
                        
                        Text("\(viewModel.meta["artist"] ?? "작가 정보 없음")")
                            .font(.headline)
                            .accessibilityLabel("작가: \(viewModel.meta["artist"] ?? "정보 없음")")
                        
                        Text("\(viewModel.meta["emotion"] ?? "감정 정보 없음")")
                            .font(.subheadline)
                            .accessibilityLabel("감정정보: \(viewModel.meta["emotion"] ?? "정보 없음")")
                    }
                    
                    Text("\(viewModel.meta["style"] ?? "스타일 정보 없음")")
                        .font(.subheadline)
                        .accessibilityLabel(generateAccessibilityText(for: viewModel.meta["style"] ?? "정보 없음"))
                    
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
                                        
                                        ZStack {
                                            SwiftUIImageViewer(imageURLString: viewModel.image_url)
                                                .accessibilityLabel("\(viewModel.meta["title"] ?? " ") 작품 이미지")
                                            
                                            VStack {
                                                Spacer()
                                                    .frame(height: 10)
                                                HStack {
                                                    Spacer()
                                                    closeButton
                                                        .accessibilityLabel("닫기 버튼")
                                                        .accessibilityHint("작품 상세정보 화면으로 돌아간다")
                                                    Spacer()
                                                        .frame(width: 10)
                                                }
                                                Spacer()
                                            }
                                            
                                        }
                                        
                                        
                                                
                                                
                                            VStack {
                                                Spacer()
                                                Button(action: {
                                                    withAnimation {
                                                        captureScreenshotAndRequestDescription()
                                                        
                                                            isBottomSheetPresented = true
                                                    }
                                                }, label: {
                                                    Text("해설 요청하기")
//                                                        .font(.system(size: 15))
                                                        .foregroundColor(.white)
                                                        .padding(.horizontal, 30)
                                                        .padding(.vertical, 20)
                                                        .background(
                                                                            RoundedRectangle(cornerRadius: 10) // 배경 모양
                                                                                .stroke(
                                                                                    AngularGradient( // 각진 그라데이션
                                                                                        gradient: Gradient(colors: [.red, .yellow]), // 색상
                                                                                        center: .center, // 중심
                                                                                        startAngle: .degrees(0), // 시작 각도
                                                                                        endAngle: .degrees(360) // 끝 각도
                                                                                    ),
                                                                                    lineWidth: 10 // 테두리 두께
                                                                                )
                                                                                .background(Color(hex: "404293")) // 내부 배경색
                                                                        )
                                                        .cornerRadius(10)
                                                })
                                                .accessibilityHidden(isBottomSheetPresented)
                                                .accessibilityLabel("해설 요청") // 버튼 역할 설명
                                                .accessibilityHint("현재 화면에서 확대한 부분에 대해 자세하게 설명해줍니다") // 동작에 대한 힌트 추가
                                                .accessibilityAddTraits(.isButton) // 접근성 요소에 버튼 특성 추가
                                                .contentShape(Rectangle()) // 더 큰 터치 영역 제공
                                                
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
                                    
                                    // ✅ alert modifier 추가
//                                           .alert(isPresented: $viewModel.isDescriptionLoaded) {
////                                               $viewModel.isDescriptionLoaded = false
//                                               if let error = viewModel.descriptionRequestError {
//                                                   return Alert(title: Text("오류"), message: Text(error), dismissButton: .default(Text("확인")))
//                                               } else {
//                                                   return Alert(title: Text("해설 완료"), message: Text("해설 생성이 완료되었습니다."), dismissButton: .default(Text("확인")))
//                                               }
//
//                                           }
                                    }
                                
                    }
                    .accessibilityLabel("작품 이미지")
                    .accessibilityHint("해설을 원하는 부분을 확대한 뒤, 해설 요청하기 버튼을 클릭하세요")
                    
             
                    Button(action: {
                        isImagePresented = true
//                        print("clicked")
                    }) {
                        Text("작품 확대하여 해설 요청하기")
//                            .font(.system(size: 15))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(Color(hex: "404293"))
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 20)
                    .accessibilityLabel("작품 확대하여 해설보기") // 버튼 역할 설명
                    .accessibilityHint("그림을 누르면 확대/축소나 자세한 설명 듣기가 가능합니다") // 동작에 대한 힌트 추가
                    .accessibilityAddTraits(.isButton) // 접근성 요소에 버튼 특성 추가
                    
                    
                    
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
        .padding(.bottom, 10)
        
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
        VStack {
            ScrollView {
                VStack(alignment: .leading) {
                    if viewModel.isLoadingRequestDescription {
                        VStack {
                            Spacer()
                            ProgressView("해설 로딩중")
                                .padding()
//                            Spacer()
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else if !viewModel.descriptionText.isEmpty {
                        Text(viewModel.descriptionText)
                            .padding()
                    } else {
                        Text("설명 텍스트가 없습니다.")
                            .padding()
                    }
                    
                    Spacer()
                        .frame(height: 60)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            
            Divider()
            
            Button(action: {
                isBottomSheetPresented = false
            }) {
                Text("해설 닫기")
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .accessibilityLabel("해설 닫기") // 버튼 역할 설명
            .accessibilityHint("하단 해설이 닫힙니다") // 동작에 대한 힌트 추가
            .accessibilityAddTraits(.isButton) // 접근성 요소에 버튼 특성 추가
            
            .padding()
        }
            .frame(width: UIScreen.main.bounds.width, height: UIScreen.main.bounds.height / 3)
            .background(Color.white)
            .cornerRadius(20)
            .shadow(radius: 20)
            .ignoresSafeArea()
            .onAppear() {
                captureScreenshotAndRequestDescription()
            }
        }
    
    private func captureScreenshotAndRequestDescription() {
            let window = UIApplication.shared.windows.first { $0.isKeyWindow }
            let renderer = UIGraphicsImageRenderer(size: window?.bounds.size ?? CGSize.zero)
            
            let image = renderer.image { context in
                window?.layer.render(in: context.cgContext)
            }
        
            capturedImage = image
       
            viewModel.requestDescriptionWithScreenshot(image: image, file: "photo/" + eng_id)
        }
    
    
    func generateAccessibilityText(for text: String) -> String {
        return text.replacingOccurrences(of: " /", with: ",") // '/' 제거
                    .replacingOccurrences(of: "*", with: " 곱하기 ") // '*' 변환
                    .replacingOccurrences(of: "cm", with: "센치미터")
    }

}



#Preview {
    ArtworkView(eng_id: "JeongyeonMoon_Golden.jpg")
}
