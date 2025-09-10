
import SwiftUI
import Kingfisher
//import ImageViewer
import SwiftUIImageViewer2

struct FreeCameraModeView: View {
    var originalImage: UIImage? // 원본 전체 이미지만 파라미터로 전달받음
    
    @ObservedObject var viewModel = FreeCameraModeViewModel()
    @State var isBottomSheetPresented: Bool = false
    
    @State var showImageViewer: Bool = false
    
    private var bottomSheet: some View {
        VStack {
            ScrollView {
                VStack(alignment: .leading) {
                    if viewModel.isLoadingRequestDescription {
                        VStack {
                            Spacer()
                            ProgressView("해설 로딩중")
                                .padding()
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
            .accessibilityElement(children: .contain)
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
            
            let screenshot_image = renderer.image { context in
                window?.layer.render(in: context.cgContext)
            }
        
        let appSettings = AppSettings()
        
        print("promptmode - 2: \(appSettings.selectedAIMode)")
        
       
        viewModel.requestDescriptionWithScreenshot2(image1: originalImage!, image2:screenshot_image, promptmode: appSettings.selectedAIMode)
        }

    var body: some View {
        HStack {
                    ZStack {
                        Color.white
                        ZStack {
                            SwiftUIImageViewer2(uiImage: originalImage)
                                .accessibilityLabel("촬영된 이미지")
                                .accessibility(sortPriority: 3)
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
                            .accessibility(sortPriority: 2)
                            
                            Spacer()
                                .frame(height: 100)
                        }
                    }
                    .accessibilityElement(children: .contain)
                    .overlay(
                        VStack {
                            Spacer()
                            if isBottomSheetPresented {
                                bottomSheet
                                    .transition(.move(edge: .bottom))
                                    .animation(.easeInOut)
                                    .accessibility(sortPriority: 1)
                            }
                            
                            
                        }
                    )
                
                                
        }
//        .accessibilityLabel("작품 이미지")
        .accessibilityHint("해설을 원하는 부분을 확대한 뒤, 해설 요청하기 버튼을 클릭하세요")
        .onAppear {
            showImageViewer = true
        }
    }
        
}


