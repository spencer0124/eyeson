//
//  CamerascanView.swift
//  eyeson
//
//  Created by 조승용 on 8/5/24.
//

import SwiftUI

struct CamerascanView: View {
    @State private var scannedImages: [(id: UUID, image: UIImage, date: Date)] = []
    @State private var isShowingScanner = false
    @State private var isNavigatingToAnalyze = false

    var body: some View {
        
            ZStack {
                Color("backgroundColor")
                    .ignoresSafeArea()
                
                VStack {
                    Button(action: {
                        isShowingScanner = true
                    }) {
                        Text("카메라로 작품 촬영하기")
                            .font(.system(size: 15))
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
                    
                    Button(action: {
                        isShowingScanner = true
                    }) {
                        Text("촬영 가이드 보기")
                            .font(.system(size: 15))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 10)
                            .background(Color.white)
                            .foregroundColor(.black)
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

                    // Removed the List view as per your request
                }
                .padding()
                .navigationBarTitle("작품 촬영", displayMode: .large)
                .background(
                    NavigationLink(
                        destination: AnalyzeImage(image: scannedImages.last?.image),
                        isActive: $isNavigatingToAnalyze,
                        label: { EmptyView() }
                    )
                )
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
        
        // Remove all entries with the same date, then add the new entry
        for newEntry in newEntries {
            scannedImages.removeAll(where: { formattedDate($0.date) == formattedDate(newEntry.2) })
            scannedImages.append(newEntry)
        }
    }
}

struct AnalyzeImage: View {
    var image: UIImage?

    var body: some View {
        VStack {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 400)
            } else {
                Text("No image available")
            }
        }
        .navigationTitle("이미지 분석중..")
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
