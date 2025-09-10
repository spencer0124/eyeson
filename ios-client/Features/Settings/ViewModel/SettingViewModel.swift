

import Foundation
import SwiftUI
import UserNotifications
import CoreLocation

class AppSettings: ObservableObject {
    @AppStorage("selectedAIMode") var selectedAIMode: String = "promptmode1"
}
