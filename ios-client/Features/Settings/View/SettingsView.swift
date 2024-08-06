//
//  SettingsView.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import SwiftUI

struct SettingsView: View {
    @State private var pushNotificationsEnabled = true
    @State private var locationServicesEnabled = true
    @State private var selectedLanguage = "Korean"
    
    var body: some View {
        NavigationView {
                Form {
                    Section(header: Text("계정 설정")) {
                        Toggle(isOn: $pushNotificationsEnabled) {
                            Text("푸시 알림")
                        }
                        Toggle(isOn: $locationServicesEnabled) {
                            Text("위치 정보 (GPS)")
                        }
                    }
                    
                    Section(header: Text("언어 설정")) {
                       Picker(selection: $selectedLanguage, label: Text("")) {
                           Text("한국어 (Korean)").tag("Korean")
                           Text("영어 (English)").tag("English")
                           Text("중국어 (Chinese)").tag("Chinese")
                       }
                       .pickerStyle(.inline)
                       .labelsHidden()
                   }
               }
            .navigationBarTitle("환경설정", displayMode: .large)
        }
    }
}

#Preview {
    SettingsView()
}
