

import Foundation
import SwiftUI
import CoreLocation

func PermissionLocation() async {
       // 위치 사용 권한 설정 확인
       let locationManager = CLLocationManager()
       let authorizationStatus = locationManager.authorizationStatus
       
       // 위치 사용 권한 항상 허용되어 있음
       if authorizationStatus == .authorizedAlways {
       }
       // 위치 사용 권한 앱 사용 시 허용되어 있음
       else if authorizationStatus == .authorizedWhenInUse {
       }
       // 위치 사용 권한 거부되어 있음
       else if authorizationStatus == .denied {
           // 앱 설정화면으로 이동
           DispatchQueue.main.async {
               UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!)
           }
       }
       // 위치 사용 권한 대기 상태
       else if authorizationStatus == .restricted || authorizationStatus == .notDetermined {
           // 권한 요청 팝업창
           locationManager.requestWhenInUseAuthorization()
       }
   }
