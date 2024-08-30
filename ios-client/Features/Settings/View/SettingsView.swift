//
//  SettingsView.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import SwiftUI
import UserNotifications
import CoreLocation

struct SettingsView: View {
    @State private var pushNotificationsEnabled = false
    @State private var locationServicesEnabled = false
    @State private var selectedLanguage = "Korean"
    
    var body: some View {
        
                Form {
                    Section(header: Text("권한 설정")) {
//                        Button(action: {
//                                openSettings()
//                            }) {
//                                HStack {
//                                    Text("푸시 알림")
//                                    Spacer()
//                                    Text(pushNotificationsEnabled ? "허용됨" : "허용 안 됨")
//                                        .foregroundColor(pushNotificationsEnabled ? .blue : .gray)
//                                }
//                            }
//                            .foregroundColor(.primary)
                        Button(action: {
                                                openSettings()
                                            }) {
                                                HStack {
                                                    Text("위치 정보 (GPS)")
                                                    Spacer()
                                                    Text(locationServicesEnabled ? "허용됨" : "허용 안 됨")
                                                        .foregroundColor(locationServicesEnabled ? .blue : .gray)
                                                }
                                            }
                                            .foregroundColor(.primary) // To keep the default text color
                                        }
                    
                    Section(header: Text("언어 설정")) {
                       Picker(selection: $selectedLanguage, label: Text("")) {
                           Text("한국어 (Korean)").tag("Korean")
//                           Text("영어 (English)").tag("English")
//                           Text("중국어 (Chinese)").tag("Chinese")
                       }
                       .pickerStyle(.inline)
                       .labelsHidden()
                   }
               }
            
            .navigationBarTitle("설정", displayMode: .large)
            .onAppear {
                        checkPushNotificationPermission()
                        checkLocationServicesPermission()
                    }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                            checkPushNotificationPermission()
                            checkLocationServicesPermission()
                        }
        
    }
    
    
    private func checkPushNotificationPermission() {
            UNUserNotificationCenter.current().getNotificationSettings { settings in
                DispatchQueue.main.async {
                    pushNotificationsEnabled = settings.authorizationStatus == .authorized
                }
            }
        }
        
        private func checkLocationServicesPermission() {
            let authorizationStatus = CLLocationManager.authorizationStatus()
            DispatchQueue.main.async {
                locationServicesEnabled = authorizationStatus == .authorizedAlways || authorizationStatus == .authorizedWhenInUse
            }
        }
    
    private func openSettings() {
            if let url = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(url)
            }
        }
}

#Preview {
    SettingsView()
}
