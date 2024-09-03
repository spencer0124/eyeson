//
//  CameraInfoView.swift
//  eyeson
//
//  Created by 조승용 on 9/2/24.
//

import SwiftUI

struct CameraInfoView: View {
    
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading) {
                
                Text("자동 촬영 가이드")
                    .font(.title)
                    
                Spacer()
                    .frame(height: 20)
                Text("1. 화면 우측 상단 모드 [자동] 확인")
                    .font(.headline)
                    
                Text("텍스트를 클릭해 [자동]과 [수동] 전환 가능")
                
                Image("cguide1_1")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 화면 우측 상단 "자동" 글씨에 빨간박스로 강조되어 있음.
    
""")
                
                Spacer()
                    .frame(height: 20)
                Text("2. 모양을 인식해 자동으로 촬영 진행")
                    .font(.headline)
                    
                Text("모양을 인식해 자동으로 촬영됩니다")
                Text("버튼을 통해 직접 촬영도 가능합니다")
                Image("cguide1_2")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 모양이 자동으로 인식되어 촬영되는 모습.
""")
                
                Spacer()
                    .frame(height: 20)
                Text("3. 촬영 완료 후 [저장] 버튼 클릭")
                    .font(.headline)
                    
                Text("여러장의 사진을 촬영하면, \n마지막에 찍은 사진만 저장됩니다")
                Image("cguide1_3")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 사진 촬영 후 저장 버튼이 나오는 모습.
""")
                
                Spacer()
                    .frame(height: 20)
                
                Divider()
                
                Text("수동 촬영 가이드")
                    .font(.title)
                    
                Spacer()
                    .frame(height: 20)
                Text("1. 화면 우측 상단 모드 [수동] 확인")
                    .font(.headline)
                    
                Text("텍스트를 클릭해 [자동]과 [수동] 전환 가능")
                
                Image("cguide2_1")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 화면 우측 상단 "수동" 글씨에 빨간박스로 강조되어 있음.
    
""")
                
                Spacer()
                    .frame(height: 20)
                Text("2. 촬영 후 모양 조절")
                    .font(.headline)
                    
                Text("직접 사진을 촬영해주세요")
                Text("작품만 보이도록 사진을 편집해주세요")
                Image("cguide2_2")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 수동으로 사진을 촬영하는 모습.
""")
                
                Spacer()
                    .frame(height: 20)
                Text("3. 촬영 완료 후 [저장] 버튼 클릭")
                    .font(.headline)
                    
                Text("여러장의 사진을 촬영하면, \n마지막에 찍은 사진만 저장됩니다")
                Image("cguide2_3")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
사진. 사진 촬영 후 저장 버튼이 나오는 모습.
""")
                
                
                
                Spacer()
            }
            .padding()
            
            
        }
        .navigationTitle("촬영 가이드")
    }
}

#Preview {
    CameraInfoView()
}
