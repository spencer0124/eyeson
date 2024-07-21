//
//  ContentView.swift
//  eyeson
//
//  Created by 조승용 on 7/20/24.
//

import SwiftUI

struct ContentView: View {
    @State private var showCannerSheet = false
    @State private var texts: [ScanData] = []
    
    var body: some View {
        NavigationView {
            VStack {
                if texts.count > 0 {
                    List {
                        ForEach(texts) { text in
                            NavigationLink(
                                destination: ScrollView{Text(text.content)},
                                label: {
                                    Text(text.content).lineLimit(1)
                                }                            )
                        }
                    }
                }
                else {
                    Text("No scan yet").font(.title)
                }
            }
                .navigationTitle("Scan OCR")
                .navigationBarItems(trailing:
                        Button(action: {
                    self.showCannerSheet = true
                }, label: {
                    Image(systemName: "doc.text.viewfinder")
                        .font(.title)
                })
                            .sheet(isPresented: $showCannerSheet, content: {
                                makeSacnnerView()
                            })
                
                
                )
        }
    }
    private func makeSacnnerView() -> ScannerView {
        ScannerView(completion: {
            textPerPage in
            if let outputText = textPerPage?.joined(separator: "\n").trimmingCharacters(in: .whitespacesAndNewlines) {
                let newScanData = ScanData(content: outputText)
                self.texts.append(newScanData)
            }
            self.showCannerSheet = false
        })
    }
}

#Preview {
    ContentView()
}
