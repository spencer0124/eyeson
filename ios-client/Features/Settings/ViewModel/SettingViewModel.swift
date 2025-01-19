//
//  SettingViewModel.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import Foundation
import SwiftUI
import UserNotifications
import CoreLocation

class AppSettings: ObservableObject {
    @AppStorage("selectedAIMode") var selectedAIMode: String = "promptmode1"
}
