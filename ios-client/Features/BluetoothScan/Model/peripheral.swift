

import Foundation

struct Peripheral: Identifiable {
    let id: UUID
    var name: String
    let rssi: Int
    // Declare a constant property 'rssi' of type Int, used for the signal strength of the peripheral
}
