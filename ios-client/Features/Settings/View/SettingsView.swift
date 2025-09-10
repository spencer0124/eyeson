import SwiftUI
import UserNotifications
import CoreLocation

struct SettingsView: View {
    @State private var pushNotificationsEnabled = false
    @State private var locationServicesEnabled = false
    @State private var selectedLanguage = "Korean"
    @AppStorage("selectedAIMode") var selectedAIMode:String = UserDefaults.standard.string(forKey: "selectedAIMode") ?? "promptmode1"
    
    var body: some View {
        
                Form {
                    Section(header: Text("권한 설정").foregroundColor(.black)) {
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
                    
                    Section(header: Text("언어 설정").foregroundColor(.black)) {
                       Picker(selection: $selectedLanguage, label: Text("")) {
                           Text("한국어 (Korean)").tag("Korean")
//                           Text("영어 (English)").tag("English")
//                           Text("중국어 (Chinese)").tag("Chinese")
                       }
                       .pickerStyle(.inline)
                       .labelsHidden()
                   }
                    
                    Section(header: Text("AI 해설 설정").foregroundColor(.black),
                            footer:
                                VStack(alignment: .leading) { // VStack으로 감싸줍니다.
                                    Spacer()
                                        .frame(height: 10)
                                    Text(selectedAIMode == "promptmode1" ?
                                         "[객관적인 사실 중심의 해설 예시]"
                                         : "[감성적인 사실 중심의 해설 예시]")
                                    Spacer()
                                        .frame(height: 3)
                                    Text(selectedAIMode == "promptmode1" ?
                                         "주황빛이 두드러지는 들판 정 가운데 빨간 지붕의 집이 돋보이는 작품입니다. 정면 모습을 보여주는 집은 하얀 벽면으로 이루어져 있으며, 창살 없는 작은 창문 두 개를 갖고 있습니다." :
                                         "가을빛으로 물든 주황색 들판 한가운데, 빨간 지붕의 집이 포근한 안식처처럼 자리하고 있습니다. 하얀 벽과 작은 창문은 소박하지만 아늑한 느낌을 주며, 고요한 가을날의 평화로움이 가득 담겨 있습니다.")
                                }
                    ) {
                       Picker(selection: $selectedAIMode, label: Text("")) {
                           Text("객관적인 사실 중심의 해설").tag("promptmode1")
                           Text("감성적인 묘사 중심의 해설").tag("promptmode2")
                       }
                       .pickerStyle(.inline)
                       .labelsHidden()
                       .onAppear { // 뷰가 나타날 때 UserDefaults에서 값을 불러옵니다.
                           selectedAIMode = UserDefaults.standard.string(forKey: "selectedAIMode") ?? "promptmode1"
                                       }
                       .onChange(of: selectedAIMode) { newValue, _ in // 값이 변경될 때 UserDefaults에 저장합니다.
                           UserDefaults.standard.set(newValue, forKey: "selectedAIMode")
                       }
                        
                        
                        
                        
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
