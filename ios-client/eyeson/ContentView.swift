//
//  ContentView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//
import SwiftUI

enum NavigationState {
    case Exhibits, Camera, Settings
}

struct ContentView: View {
    @State private var selectedTab: NavigationState = .Exhibits
    @State private var tabBarHeight: CGFloat = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            tabViewContent(for: .Exhibits, label: "전시관", systemImage: "photo")
            tabViewContent(for: .Camera, label: "작품 촬영", systemImage: "camera")
            tabViewContent(for: .Settings, label: "설정", systemImage: "gear")
        }
    }

    private func tabViewContent(for tab: NavigationState, label: String, systemImage: String) -> some View {
        NavigationStack {
            Group { // Group을 사용하여 뷰 계층 구조를 단순화
                switch tab {
                case .Exhibits: ExhibitsView()
                case .Camera: CamerascanView()
                case .Settings: SettingsView()
                }
            }
            .padding(.bottom, 0) // 탭 바 높이만큼 하단 패딩 추가 (중요!)
            .frame(maxWidth: .infinity, maxHeight: .infinity) // 화면 전체를 채우도록 설정
        }
        .navigationViewStyle(.stack)
        .tabItem {
            Label(label, systemImage: systemImage)
                .accessibilityLabel(label)
                .accessibilityHint("클릭하면 \(label) 화면으로 이동합니다")
        }
        .tag(tab)
    }
}
   

#Preview {
    ContentView()
}
