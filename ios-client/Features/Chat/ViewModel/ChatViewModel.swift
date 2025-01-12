//
//  ChatViewModel.swift
//  eyeson
//
//  Created by SeungYong on 1/5/25.
//

import Foundation
import Starscream
import SwiftUI

/// 서버에서 전송하는 메시지(JSON)을 매핑할 구조체
/// (type, content, username, museum, timestamp, active_users)
struct ChatMessage: Codable, Identifiable {
    /// List 등에 바인딩하기 위해 사용되는 임시 id
    let id = UUID()
    
    let type: String           // "system" 또는 "message"
    let content: String        // 메시지 내용
    let username: String       // 보낸 사용자명
    let museum: String         // 박물관 ID(또는 이름)
    let timestamp: String      // ISO8601 형식 시간
    let active_users: [String]? // 현재 활성 사용자 목록(옵션)
    
    enum CodingKeys: String, CodingKey {
        case type
        case content
        case username
        case museum
        case timestamp
        case active_users
    }
}

class ChatViewModel: ObservableObject {
    // 채팅에 표시될 메시지 리스트
    @Published var messages: [ChatMessage] = []
    // TextField 바인딩
    @Published var currentMessage: String = ""
    
    private var socket: WebSocket?
    private var isConnected = false
    
    // init 시 넘겨받는 정보
    private let museumID: String
    private let localUserName: String  // "익명 + 숫자 + (artworkName)" 형태
    
    // MARK: - 생성자
    init(museumID: String, artworkName: String) {
        self.museumID = museumID
        
        // "익명+랜덤숫자+(작품명)" 예: 익명1234(모나리자)
        let randomNum = Int.random(in: 1...9999)
        self.localUserName = "익명\(randomNum)(\(artworkName))"
        
        print("Local User Name (not sent to server): \(localUserName)")
    }
    
    // MARK: - WebSocket 연결
    func connect() {
        // 서버 API 문서에 따라: ws://43.201.93.53:8000/chat/ws/{museum}
        guard let url = URL(string: "ws://43.201.93.53:8000/chat/ws/\(museumID)") else {
            print("Invalid WebSocket URL")
            return
        }
        
        var request = URLRequest(url: url)
        // 필요시 request에 header 등 추가 설정 가능
        
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
    }
    
    // MARK: - WebSocket 해제
    func disconnect() {
        socket?.disconnect()
        socket = nil
    }
    
    // MARK: - 채팅 메시지 전송
    func sendMessage() {
        let trimmedMessage = currentMessage.trimmingCharacters(in: .whitespacesAndNewlines)
        
        // 비어있지 않고 연결된 상태에서만 전송
        guard !trimmedMessage.isEmpty, isConnected else { return }
        
        // API 문서에 따르면, 단순 텍스트 전송 -> 서버가 JSON으로 브로드캐스트
        socket?.write(string: trimmedMessage)
        
        // 전송 후 입력창 비우기
        currentMessage = ""
    }
}

// MARK: - Starscream WebSocketDelegate
extension ChatViewModel: WebSocketDelegate {
    func didReceive(event: Starscream.WebSocketEvent, client: any Starscream.WebSocketClient) {
        //
    }
    
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected(let headers):
            isConnected = true
            print("WebSocket connected: \(headers)")
            
        case .disconnected(let reason, let code):
            isConnected = false
            print("WebSocket disconnected: reason(\(reason)), code(\(code))")
            
        case .text(let text):
            // 서버에서 브로드캐스트된 JSON 문자열 수신
            guard let data = text.data(using: .utf8) else { return }
            do {
                let chatMessage = try JSONDecoder().decode(ChatMessage.self, from: data)
                DispatchQueue.main.async {
                    self.messages.append(chatMessage)
                }
            } catch {
                print("Decoding error: \(error.localizedDescription)")
            }
            
        case .binary(let data):
            print("Received binary data (unused): \(data)")
            
        case .ping(_), .pong(_):
            break
            
        case .viabilityChanged(_), .reconnectSuggested(_):
            break
            
        case .cancelled:
            isConnected = false
            print("WebSocket cancelled")
            
        case .error(let error):
            isConnected = false
            print("WebSocket error: \(String(describing: error))")
        case .peerClosed:
            print("peerclosed")
        }
    }
}
