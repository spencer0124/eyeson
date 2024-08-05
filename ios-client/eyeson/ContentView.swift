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
    @State private var path = NavigationPath()
    @State private var selectedTab: NavigationState = .Exhibits

    var body: some View {
        
        NavigationStack {
            
            
            ZStack(alignment: .bottom) {
                TabView(selection: $selectedTab) {
                    ExhibitsView(path: $path)
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
                
                HStack {
                    if selectedTab == .Exhibits {
                        Indicator()
                            .frame(maxWidth: .infinity)
                    } else {
                        Spacer()
                            .frame(maxWidth: .infinity)
                    }
                    if selectedTab == .Nearby {
                        Indicator()
                            .frame(maxWidth: .infinity)
                    } else {
                        Spacer()
                            .frame(maxWidth: .infinity)
                    }
                    if selectedTab == .Settings {
                        Indicator()
                            .frame(maxWidth: .infinity)
                    } else {
                        Spacer()
                            .frame(maxWidth: .infinity)
                    }
                }
                .frame(height: 2)
                .background(Color.clear)
            }
            
        }
   
        .navigationDestination(for: NavigationState.self) { route in
                        switch route {
                        case .Exhibits:
                            bluetoothScan(path: $path)
                        case .Nearby:
                            bluetoothScan(path: $path)
                        case .Settings:
                            bluetoothScan(path: $path)
                            
                        }
                    }
    }
    
    
    
    private func NearbyView() -> some View {
        VStack {
            Text("Nearby View")
           
        }
    }
    
    private func SettingsView() -> some View {
        VStack {
            Text("Settings View")
           
        }
    }
}

struct Indicator: View {
    var body: some View {
        Rectangle()
            .fill(Color.blue)
            .frame(width: 60, height: 2)
            .padding(.bottom, 100) // Adjust this value to position the bar correctly above the icons
    }
}

#Preview {
    ContentView()
}
