//
//  ContentView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//
import SwiftUI

struct ContentView: View {
    @State private var showScannerSheet = false
    @State private var images: [ScanData] = []
    @State private var showBluetoothView = false
    
    var body: some View {
        NavigationView {
            VStack {
                if images.count > 0 {
                    List {
                        ForEach(images) { image in
                            NavigationLink(
                                destination: ScrollView {
                                    VStack {
                                        ForEach(image.pictures, id: \.self) { picture in
                                            Image(uiImage: picture)
                                                .resizable()
                                                .aspectRatio(contentMode: .fit)
                                        }
                                    }
                                },
                                label: {
                                    VStack(alignment: .leading) {
                                        Text(image.timestamp, style: .time)
                                            .font(.headline)
                                        ScrollView(.horizontal, showsIndicators: false) {
                                            HStack {
                                                ForEach(image.pictures, id: \.self) { picture in
                                                    Image(uiImage: picture)
                                                        .resizable()
                                                        .aspectRatio(contentMode: .fit)
                                                        .frame(width: 100, height: 100)
                                                        .clipped()
                                                }
                                            }
                                        }
                                    }
                                }
                            )
                        }
                    }
                }
                else {
                    Text("No scan yet").font(.title)
                }
            }
            .navigationTitle("History")
            .navigationBarItems(trailing: HStack {
                Button(action: {
                    self.showBluetoothView = true
                }, label: {
                    Image(systemName: "dot.radiowaves.left.and.right")
                        .font(.title)
                })
                .background(
                    NavigationLink(destination: bluetoothScan(), isActive: $showBluetoothView) {
                        EmptyView()
                    }
                    .hidden()
                )
                Button(action: {
                    self.showScannerSheet = true
                }, label: {
                    Image(systemName: "camera")
                        .font(.title)
                })
                .sheet(isPresented: $showScannerSheet, content: {
                    makeScannerView()
                })
            })
        }
    }
    
    private func makeScannerView() -> ScannerView {
        ScannerView(completion: { imagesPerPage in
            if let newImages = imagesPerPage {
                let newScanData = ScanData(pictures: newImages)
                self.images.append(newScanData)
            }
            self.showScannerSheet = false
        })
    }
}


#Preview {
    ContentView()
}
