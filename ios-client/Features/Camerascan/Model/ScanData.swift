
import Foundation
import UIKit

struct ScanData: Identifiable {
    var id = UUID()
    let timestamp: Date
    let pictures: [UIImage]
    
    init(pictures: [UIImage]) {
        self.timestamp = Date()
        self.pictures = pictures
    }
}
