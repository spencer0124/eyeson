//
//  BLEManager.swift
//  eyeson
//
//  Created by 조승용 on 7/22/24.
//

import Foundation
import SwiftUI
import CoreBluetooth

class BLEManager: NSObject, ObservableObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var myCentral: CBCentralManager! // var for the central manager
    @Published var isSwitchedOn = false // check if bluetooth is turned on
    @Published var peripherals = [Peripheral]() // a published array to store discoverd
    @Published var connectedPeripheralUUID: UUID? // store the UUID of the connected peripheral
    
    override init() {
        super.init()
        myCentral = CBCentralManager(delegate: self, queue: nil) // init the central manger with self as delegate
    }
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        isSwitchedOn = central.state == .poweredOn // update isSwitchedOn based on the central's state
        if isSwitchedOn {
            startScanning()
        } else {
            stopScanning()
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        let peripheralName = advertisementData[CBAdvertisementDataLocalNameKey] as? String ?? peripheral.name ?? "Unknown"
        let newPeripheral = Peripheral(id: peripheral.identifier, name: peripheral.name ?? "Unknown", rssi: RSSI.intValue)
        if !peripherals.contains(where: { $0.id == newPeripheral.id }) { // check if the peripheral is already in the list
            DispatchQueue.main.async {
                self.peripherals.append(newPeripheral)
            }
        }
    }
    
    func startScanning() {
        print("start Scanning")
        myCentral.scanForPeripherals(withServices: nil, options: nil) // start scanning with no specific services
    }
    
    func stopScanning() {
        print("stop scanning")
        myCentral.stopScan()
    }
    
    func connect(to peripheral: Peripheral) {
        guard let cbPeripheral = myCentral.retrievePeripherals(withIdentifiers: [peripheral.id]).first
        else { // retrieve the peripheral by its identifier
            print("peripheral not found for connection")
            return // return if the peripheral is not found
        }
        
        connectedPeripheralUUID = cbPeripheral.identifier // Set the connected peripheral's UUID
        cbPeripheral.delegate = self // Set self as the delegate of the peripheral
        myCentral.connect(cbPeripheral, options: nil) // Connect to the peripheral
    }
    
    // Delegate method called when a peripheral is connected
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("Connected to \(peripheral.name ?? "Unknown")")
        peripheral.discoverServices(nil) // Discover services on the connected peripheral
    }
    
    // Delegate method called when the connection to a peripheral fails
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("Failed to connect to \(peripheral.name ?? "Unknown"): \(error?.localizedDescription ?? "No error information")")
        if peripheral.identifier == connectedPeripheralUUID {
            connectedPeripheralUUID = nil
        }
    }
    
    // Delegate method called when a peripheral is disconnected
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("disconnected from \(peripheral.name ?? "Unknown")")
        if peripheral.identifier == connectedPeripheralUUID {
            connectedPeripheralUUID = nil
        }
    }
    
    // Delegate method called when service are discoverd on a peripheral
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let services = peripheral.services { // check if services are discovered
            for service in services { // Iterate through the services
                print("Discovered service: \(service.uuid)")
                peripheral.discoverCharacteristics(nil, for: service) // discover characteristics for the service
            }
        }
        // Update peripheral name if it was "Unknown"
        if let index = peripherals.firstIndex(where: { $0.id == peripheral.identifier }) {
            DispatchQueue.main.async {
                self.peripherals[index].name = peripheral.name ?? "Unknown"
            }
        }
    }
    
    // Delegate method called when characteristics are discovered for a service
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let characteristics = service.characteristics { // Check if characteristics are discovered
            for characteristic in characteristics { // Iterate through the characteristics
                print("discovered characteristics: \(characteristic.uuid)") // Print the characteristic UUID
                // Interact with characteristics as needed
            }
        }
    }
    
    var knownPeripherals: [Peripheral] {
           return peripherals.filter { $0.name != "Unknown" }
       }
    
}
