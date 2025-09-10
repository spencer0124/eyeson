

import SwiftUI

struct bluetoothScan: View {
    @Binding var path: NavigationPath
    @Environment(\.presentationMode) var presentationMode
    @Environment(\.dismiss) private var dismiss
    
    @StateObject var bleManager = BLEManager()
    
    var body: some View {
        VStack(spacing: 10) {
            Text("Bluetooth devices")
                .font(.largeTitle)
                .frame(maxWidth: .infinity, alignment: .center)
            
            List(bleManager.knownPeripherals) { peripheral in
                HStack {
                    Text(peripheral.name)
                    Spacer()
                    Text(String(peripheral.rssi))
                    Button(action: {
                        bleManager.connect(to: peripheral)
                    }) {
                        if bleManager.connectedPeripheralUUID == peripheral.id {
                            Text("Connected")
                                .foregroundColor(.green)
                        } else {
                            Text("Connect")
                        }
                    }
                }
            }
            .frame(height: UIScreen.main.bounds.height / 2)
            
            Spacer()
            
            Text("STATUS")
                .font(.headline)
            
            if bleManager.isSwitchedOn {
                Text("Bluetooth is switched on")
                    .foregroundColor(.green)
            } else {
                Text("Bluetooth is NOT switched on")
                    .foregroundColor(.red)
            }
            
            Spacer()
            
            VStack(spacing: 25) {
                Button(action: {
                    bleManager.startScanning()
                }) {
                    Text("Start Scanning")
                }.buttonStyle(BorderedProminentButtonStyle())
                
                Button(action: {
                    bleManager.stopScanning()
                }) {
                    Text("Stop Scanning")
                }.buttonStyle(BorderedProminentButtonStyle())
            }
            .padding()
            
            Spacer()
        }
        .onAppear {
            if bleManager.isSwitchedOn {
                bleManager.startScanning()
            }
        }
    }
}

#Preview {
    bluetoothScan(path: .constant(NavigationPath()))
}
