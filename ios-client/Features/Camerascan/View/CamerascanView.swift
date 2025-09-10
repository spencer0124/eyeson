

import SwiftUI

struct CamerascanView: View {
    @State private var scannedImages: [(id: UUID, image: UIImage, date: Date)] = []
    @State private var isShowingScanner = false
    @State private var isShowingProgress = false
    @State private var isNavigatingToAnalyze = false
    
    @State private var navigateToCameraInfo = false
    @State private var navigateToCustomCameraMode = false // 자유촬영 모드
    
    @StateObject private var viewModel = ImageSearchViewModel()
    
    // 첫 번째 Picker (모드 선택)
    @State private var SelectedCameraOption = 0
    var CameraOptions = ["전시관 모드", "자유촬영 모드"]
    
    // 두 번째 Picker (전시관 선택)
    @State private var selectedExhibitId: String = "" // 선택된 전시관의 인덱스 (viewModel.exhibitInfo 배열에서)


    var body: some View {
            ZStack {
                Color("backgroundColor")
                    .ignoresSafeArea()
                
                VStack {
                    
                    Button(action: {
                        isShowingScanner = true
                    }) {
                        Text("카메라로 작품 촬영하기")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(Color(hex: "404293"))
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 41)
                    .sheet(isPresented: $isShowingScanner) {
                        ScannerView { images in
                            if let images = images {
                                let currentDate = Date()
                                addScannedImages(images: images, date: currentDate)
                                if let lastImage = scannedImages.last {
                                    if(SelectedCameraOption == 0) {
                                        isNavigatingToAnalyze = true
                                    }
                                    else if(SelectedCameraOption == 1) {
                                        navigateToCustomCameraMode = true
                                    }
                                    
                                }
                            }
                            isShowingScanner = false
                        }
                    }
                    
                    Spacer()
                        .frame(height: 20)
                    
                    Button(action: {
                        navigateToCameraInfo = true
                    }) {
                        Text("촬영 가이드 보기")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(Color(hex: "404293"))
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 41)
                    .sheet(isPresented: $isShowingScanner) {
                        ScannerView { images in
                            if let images = images {
                                let currentDate = Date()
                                addScannedImages(images: images, date: currentDate)
                                if let lastImage = scannedImages.last {
                                    isNavigatingToAnalyze = true
                                }
                            }
                            isShowingScanner = false
                        }
                    }
                    
                    VStack {
                        Spacer()
                            .frame(height: 30)
                            Picker("촬영 모드", selection: $SelectedCameraOption) {
                                ForEach(0 ..< CameraOptions.count) {
                                    Text(CameraOptions[$0])
                                    
                                  }
                            }.pickerStyle(.segmented)

                        Spacer()
                            .frame(height: 25)
                    
                        VStack {
//                            Spacer()
                            HStack(alignment: .top) {
                                    Image(systemName: "info.circle")

                                    Spacer()
                                        .frame(width: 10)
                                    
                                    if(SelectedCameraOption == 0) {
                                        VStack(alignment: .leading) {
                                            if viewModel.isLoading2 {
                                                        ProgressView() // Show a progress indicator while loading
                                                    }
                                            else {
                                            Picker("전시관 선택", selection: $selectedExhibitId) {
                                                // ViewModel에서 가져온 전시관 목록으로 Picker 구성
                                                ForEach(viewModel.exhibitInfo, id: \.id) { exhibit in // 여기를 수정했습니다.
                                                    Text(exhibit.name).tag(exhibit.id)
                                                }
                                            }
                                            .onAppear {
                                                    if selectedExhibitId.isEmpty && !viewModel.exhibitInfo.isEmpty {
                                                        selectedExhibitId = viewModel.exhibitInfo[0].id // 데이터 로드 후 selectedExhibitId 설정
                                                    }
                                                }
                                            .padding(.horizontal, -10)
                                            .padding(.vertical, -9)
                                        }
                                                                            
                                            
                                            
//                                            Text("현재 선택된 ID: \(selectedExhibitId)")
                                            
                                            Text("선택된 전시에 등록된 작품 중에서\n일치하는 작품을 검색합니다")
                                            Spacer()
                                        }
    //
                                        
                                    } else {
                                        VStack(alignment: .leading){
                                            Text("자유롭게 작품을 촬영하여\nAI 해설을 제공받습니다")
                                            Spacer()
                                        }
                                        
                                    }
                                
                                    Spacer()
                                }
                                .frame(height: 100)
                            Spacer()
                        }
                        .frame(maxHeight: 100)
                        
                        
                    }.padding(.horizontal, 41)

                    NavigationLink(destination: CameraInfoView(), isActive: $navigateToCameraInfo) {
                                        EmptyView()
                    }
                    .accessibilityHidden(true)
                    
                    NavigationLink(
                        destination: AnalyzeImage(image: scannedImages.last?.image, SelectedCameraOption: $SelectedCameraOption, selectedExhibitId: selectedExhibitId),
                        isActive: $isNavigatingToAnalyze,
                        label: { EmptyView() }
                    )
                    .accessibilityHidden(true)
                    
                    NavigationLink(
                        destination: FreeCameraModeView(originalImage: scannedImages.last?.image), isActive: $navigateToCustomCameraMode,
                        label: { EmptyView() }
                    
                    )
                    .accessibilityHidden(true)
                    
                    
                    
                  
                }
                .padding()
                .navigationBarTitle("작품 촬영", displayMode: .large)
                .onAppear() {
                    viewModel.fetchExhibitInfo()
//                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { // 약간의 지연을 추가
//                        if selectedExhibitId.isEmpty && !viewModel.exhibitInfo.isEmpty {
//                            selectedExhibitId = viewModel.exhibitInfo[0].id
//                        }
//                    }
                }
            }
        
    }

    // Helper function to format the date
    private func formattedDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss.SSS"
        return formatter.string(from: date)
    }

    // Function to add scanned images and keep only the last duplicate
    private func addScannedImages(images: [UIImage], date: Date) {
        let newEntries = images.map { (UUID(), $0, date) }
        
        // 새로운 이미지가 잘 들어오는지 확인
            print("새로 추가된 이미지 개수: \(newEntries.count)")
        
        // Remove all entries with the same date, then add the new entry
        for newEntry in newEntries {
            print("새 이미지 ID: \(newEntry), 날짜: \(formattedDate(newEntry.2))")
            scannedImages.removeAll(where: { formattedDate($0.date) == formattedDate(newEntry.2) })
            scannedImages.append(newEntry)
            
            // 현재 scannedImages 배열의 상태 출력
                    print("현재 scannedImages 배열:")
                    for entry in scannedImages {
                        print("ID: \(entry.id), 날짜: \(formattedDate(entry.date))")
                    }
        }
    }
}


struct AnalyzeImage: View {
    var image: UIImage?
    
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = ImageSearchViewModel()
    @State private var navigateToDescription = false // 전시관 모드
    @State private var navigateToCustomCameraMode = false // 자유촬영 모드
    @State private var hasLoadedData = false
    @State private var showContent = false
    
    @Binding var SelectedCameraOption: Int
    var selectedExhibitId: String

    var body: some View {
        VStack {
            if let image = image {
                if viewModel.isLoading {
                    ProgressView("이미지 분석중")
                } else if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                } else if !viewModel.searchResults.isEmpty {
                    ZStack {
                        Color("backgroundColor")
                            .ignoresSafeArea()
                        if showContent {
                        VStack {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                                .frame(maxHeight: 400)
                            Text("일치하는 작품을 찾았어요!")
                                .font(.title2)
                            //                        Text(viewModel.searchResults)
                            //                            .font(.subheadline)
                            Button(action: {
                                navigateToDescription = true
                            }) {
                                Text("작품 보기")
                                    .font(.system(size: 15))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 10)
                                    .background(Color(hex: "404293"))
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                            }
                            .padding(.horizontal, 41)
                            Button(action: {
                                dismiss()
                            }) {
                                Text("취소")
                                    .font(.system(size: 15))
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 10)
                                    .background(Color.white)
                                    .foregroundColor(.black)
                                    .cornerRadius(10)
                            }
                            .padding(.horizontal, 41)
                            
                            
                        }
                    }
                }
                .onAppear {
                    hasLoadedData = true
                   navigateToDescription = true
                        
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                            showContent = true
                            navigateToDescription = true
                                                }

                            }
                } else {
                    Text("No results found.")
                        .padding()
                }
            } else {
                Text("No image available")
            }
        }
    
        .onChange(of: image) { newImage in
            
            if let image = newImage {
                // trash value
                viewModel.searchImage(image: image, uniqueId: selectedExhibitId)
            }
        }
        .onAppear() {
            if let image = image {
                print("called here #1")
                // trash value
                viewModel.searchImage(image: image, uniqueId: selectedExhibitId)
                }
            if(hasLoadedData) {
                dismiss()
            }
        }
        // trash value
        .background() {
            NavigationLink(destination: ArtworkView(eng_id: viewModel.searchResults, paramUniqueId: selectedExhibitId
                                                   ), isActive: $navigateToDescription) {
                                EmptyView()
            }
           
        }
    }
}

#Preview {
    CamerascanView()
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
