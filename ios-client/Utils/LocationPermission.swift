

import Foundation
import SwiftUI
import CoreLocation

class LocationPermissionManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()

    override init() {
        super.init()
        locationManager.delegate = self
    }

    func checkLocationPermission() {
        let authorizationStatus = locationManager.authorizationStatus

        if authorizationStatus == .authorizedAlways || authorizationStatus == .authorizedWhenInUse {
            // Permission is already granted
        } else if authorizationStatus == .denied {
            // Permission is denied, trigger the alert to ask if user wants to go to settings
            DispatchQueue.main.async {
                
            }
        } else if authorizationStatus == .restricted || authorizationStatus == .notDetermined {
            // Request permission
            locationManager.requestWhenInUseAuthorization()
        }
    }

    
    
}
