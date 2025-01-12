//
//  ChatView.swift
//  eyeson
//
//  Created by SeungYong on 1/5/25.
//

import SwiftUI

struct ChatView: View {
    /// 어떤 채팅방(박물관)에 접속할지 결정하는 ID 또는 이름
    let museumID: String
    
    /// "익명+숫자+(작품명)" 형태 문자열을 생성할 때 쓰이는 작품명
    let artworkName: String
    
    @StateObject private var viewModel: ChatViewModel
    
    // MARK: - 초기화
    init(museumID: String, artworkName: String) {
        self.museumID = museumID
        self.artworkName = artworkName
        // View가 초기화될 때 ViewModel도 함께 생성
        _viewModel = StateObject(wrappedValue: ChatViewModel(museumID: museumID,
                                                             artworkName: artworkName))
    }
    
    var body: some View {
        VStack {
            // 채팅 메시지 리스트
            List(viewModel.messages, id: \.id) { msg in
                // system 메시지는 회색, 일반 메시지는 기본 색상
                HStack {
                    Text("[\(msg.timestamp)] \(msg.username): \(msg.content)")
                        .font(.body)
                        .foregroundColor(msg.type == "system" ? .gray : .primary)
                }
            }
            
            // 사용자 입력 & 전송 버튼
            HStack {
                TextField("Enter your message", text: $viewModel.currentMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                Button(action: {
                    viewModel.sendMessage()
                }) {
                    Text("Send")
                }
                .padding(.leading, 4)
            }
            .padding()
        }
        .onAppear {
            // View가 나타날 때 WebSocket 연결
            viewModel.connect()
        }
        .onDisappear {
            // View가 사라질 때 WebSocket 해제
            viewModel.disconnect()
        }
        .navigationBarTitle("Chat - \(museumID)", displayMode: .inline)
    }
}

#Preview {
    // 미리보기 시 임시 파라미터로 테스트
    ChatView(museumID: "1", artworkName: "테스트작품")
}
