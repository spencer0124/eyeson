//
//  ContentView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//
import SwiftUI

enum NavigationState {
    case Exhibits, Camera, Nearby, Settings
}

struct ContentView: View {
    @State private var selectedTab: NavigationState = .Exhibits

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                ExhibitsView()
            }
            .navigationViewStyle(.stack)
            .tabItem {
                Label("전시관", systemImage: "photo")
            }
            .tag(NavigationState.Exhibits)

            NavigationStack {
                CamerascanView()
            }
            .navigationViewStyle(.stack)
            .tabItem {
                Label("작품 촬영", systemImage: "camera")
            }
            .tag(NavigationState.Camera)
            
            NavigationStack {
                SettingsView()
            }
            .navigationViewStyle(.stack)
            .tabItem {
                Label("설정", systemImage: "gear")
            }
            .tag(NavigationState.Settings)
        }
    }
}
   

#Preview {
    ContentView()
}
