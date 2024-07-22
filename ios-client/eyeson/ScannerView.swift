//
//  ScannerView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//

import VisionKit
import SwiftUI

struct ScannerView: UIViewControllerRepresentable {
    func makeCoordinator() -> Coordinator {
        return Coordinator(completion: completionHandler)
    }
    
    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        private let completionHandler: ([UIImage]?) -> Void
        
        init(completion: @escaping ([UIImage]?) -> Void) {
            self.completionHandler = completion
        }
        
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            let images = (0..<scan.pageCount).map { scan.imageOfPage(at: $0) }
            completionHandler(images)
        }
        
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFailWithError error: Error) {
            completionHandler(nil)
        }
        
        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
            completionHandler(nil)
        }
    }
    
    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let viewController = VNDocumentCameraViewController()
        viewController.delegate = context.coordinator
        return viewController
    }
    
    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {}
    
    typealias UIViewControllerType = VNDocumentCameraViewController
    
    private let completionHandler: ([UIImage]?) -> Void
    
    init(completion: @escaping([UIImage]?) -> Void) {
        self.completionHandler = completion
    }
}
