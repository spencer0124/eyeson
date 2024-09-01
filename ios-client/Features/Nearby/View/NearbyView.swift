//
//  NearbyView.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import SwiftUI
import Lottie

//                                  Image(systemName: "shareplay")
//                                      .resizable()
//                                      .scaledToFit()
//                                      .frame(width: 30)

struct NearbyView: View {
    @State private var playbackMode: LottiePlaybackMode = .paused
    
    var body: some View {
        
            ZStack {
                Color("backgroundColor")
                    .ignoresSafeArea()
                VStack {
                    
                    Spacer()
                        .frame(height: 2)
                    
                    
                    HStack {
                        Spacer()
                            .frame(width: 20)
                       
                        Text("서울특별시 동작구 노들갤러리")
                            .font(.system(size: 17))
                            .foregroundColor(.gray)
                     
                       Spacer()
                    }
                   
                    
                      
                
            
                    
                    LottieView(animation: .named("lottie_splash"))
                        .playbackMode(.playing(.fromProgress(0, toProgress: 0.96, loopMode: .loop)))
                    
                    
                    
                    Spacer()
                        .frame(height: 15)
                    
//                    Gauge(value: 12, in: 0...100) {
//                        Text("Battery Level")
//                    }
//                    .gaugeStyle(.accessoryLinear)
//                    
                    
                 
                    
                    Spacer()
                }
            }
            
            .navigationBarTitle("주변인원")
            
            
            
        
        
    }
}

#Preview {
    NearbyView()
}
