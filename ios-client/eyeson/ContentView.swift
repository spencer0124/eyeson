//
//  ContentView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//
import SwiftUI

enum NavigationState {
    case Exhibits, Nearby, Settings
}

struct ContentView: View {
    @State private var selectedTab: NavigationState = .Exhibits

    var body: some View {

            TabView(selection: $selectedTab) {
                ExhibitsView()
                    .tabItem {
                        Label("전시관", systemImage: "photo")
                    }
                    .tag(NavigationState.Exhibits)
                
                NearbyView()
                    .tabItem {
                        Label("주변 인원", systemImage: "person")
                    }
                    .tag(NavigationState.Nearby)
                
                SettingsView()
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
