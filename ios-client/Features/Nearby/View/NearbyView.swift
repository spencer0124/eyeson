//
//  NearbyView.swift
//  eyeson
//
//  Created by 조승용 on 8/6/24.
//

import SwiftUI
import Lottie

struct NearbyView: View {
    var body: some View {
        NavigationView {
            ZStack {
                Color("backgroundColor")
                    .ignoresSafeArea()
                VStack {
                    LottieView(animation: .named("lottie_splash"))
                        .looping()
//                        .playing()
                    Image(systemName: "shareplay")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 30)
                    
                    Text("노들갤러리")
                        .font(.system(size: 18))
                        .fontWeight(.medium)
                        .foregroundColor(.gray)
                    
                    Spacer()
                        .frame(height: 15)
                    
                    Text("주변에 약 5명의 사람이 있습니다")
                        .font(.system(size: 20))
                        .fontWeight(.regular)
                        .foregroundColor(.black)
                }
            }
            
            .navigationBarTitle("주변인원")
            
            
        }
        
    }
}

#Preview {
    NearbyView()
}
