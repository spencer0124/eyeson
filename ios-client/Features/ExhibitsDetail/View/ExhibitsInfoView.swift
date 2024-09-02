//
//  ExhibitsInfoView.swift
//  eyeson
//
//  Created by 조승용 on 9/2/24.
//

import SwiftUI


struct ExhibitInfoView: View {
    
    var body: some View {
        ScrollView {
            VStack {
//                Text("제 4회 에이블라인드 장애 예술인 전시회〈나의 모든 순간〉")
//                    .font(.largeTitle)
//                    .padding()
//                
                Image("ExhibitInfo1")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
    제 4회 에이블라인드 장애 예술인 전시회〈나의 모든 순간〉every moment of mine
    2024. 9. 4.~ 11. 노들갤러리 2관
    주최 에이블라인드와 후원 문화체육관광부, 한국장애인문화예술원

    에이블라인드
    시각장애 예술 크리에이터 에이전시 에이블라인드(ABLIND)는
    시각장애인(blind)의 도전과 희망의 가능성(able)을 세상에 보여줍니다.
    에이블라인드는 시각적 예술에 도전하는 시각장애 예술 크리에이터를 포함해
    다양한 장애 예술인을 서포트 하며 장애인과 비장애인이 함께하는 세상을 꿈꿉니다.

    당신의 기억 조각 속 가장 행복했던 순간은 언제인가요? 반대로 힘들었던 순간은 언제인가요?
    ‘나’는 나의 모든 순간들로 이루어집니다.
    몇 달을 몰두하던 일을 성공적으로 해낸 날도, 반복되는 일상에 지쳐 침대에 쓰러진 날도,
    뜻하지 않은 소소한 행운을 마주한 날도, 예상 못 한 참혹한 불행이 드리운 날도 그 모든 순간은 나를 만들었습니다.

    뾰족하게 느껴졌던 어떤 조각들은 따듯한 조각들과 함께 부딪히고 깎이며 어느새 내 안에 자리를 잡았습니다.
    어떤 조각도 내 것이 아닌 게 없습니다. 나는, 나의 모든 순간들로 ‘나’입니다.
""")
                
                Image("ExhibitInfo2")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
참여 작가
강금영, 구희원, 김단영, 김서영, 김종훈, 김차연, 김하윤, 다온, 문정연, 문진서,
박서연, 박은경, 박환, 신성원, 유진, 이병륜, 장원호, 장지음, 정은교, 정희정,
조형진(별하작가), 최경은, 최원우, 토우, 표거연, 한희주, 허은빈, 홍준호 총 28명 입니다.

나의 모든 순간에는 9가지 유형의 장애 예술가 28명이 감정이 담긴 기억, 순간, 추억에 대한 작품을 그렸습니다.
작품을 보며 지금의 나를 만든 기억들을 떠올려 보세요.

1.   Pieces of Moment / 순간의 조각
순간의 조각을 간직하고 감정이 담긴 작품과 추천 음악을 감상해보세요.

2.   Artist’s room / 작가의 방
감정 카드를 보고 그 감정을 느낀 순간을 캔버스에 그려주세요. 우리의 순간이 모여 하나의 작품이 완성됩니다.

본 전시회는 배리어프리를 지향합니다.

1.   입체 가이드라인: 시각장애인을 위해 전시회장 바닥에 설치한 가이드라인을 발로 밟아 느끼며 전시를 즐겨보세요.
2.   작품 해설 영상과 QR 코드: 모든 작품 캡션에 있는 QR 코드를 스마트폰 카메라로 스캔해 배리어프리 작품 해설 영상을 보실 수 있습니다.
3.   터치 투어: 터치 투어 존 작품들은 조심스럽게 만지며 관람할 수 있습니다. 터치 투어 관람은 주변 스태프에게 문의해주세요.
4.   시각장애인 접근성 향상 앱 체험: 성균관대 Seeterature 팀에서 준비한 전시 보조 앱을 체험하며 색다른 관람을 시도해 보세요.
""")
                
                Image("ExhibitInfo3")
                    .resizable()
                    .scaledToFit()
                    .padding(.bottom)
                    .accessibilityLabel("""
청소년 작가 Zone, 디지털 작품 Zone, 입체 작품 Zone, 터치 투어 Zone, 굿즈 Shop, 인터뷰 영상,
프로필 사진, 순간의 조각, 작가의 방, Seeterature, 영수증 사진기, 글자 퍼즐이
전시장에 위치한 장소를 도면 내에 아이콘으로 표현하고 있습니다.

즉석 사진을 촬영하고, 방명록을 남길 수 있는 영수증 사진기 공간과 숨겨진 감정 단어를 찾아
퍼즐을 풀어볼 수 있는 글자 퍼즐 공간에 대한 설명도 기재되어 있습니다.

전시회 정보 소개
에이블라인드(ABLIND)에서 기획한 네 번째 전시
나의 모든 순간에는 시각, 지체, 지적, 정신, 자폐, 발달, 뇌병변, 청각, 신장 장애를 가진 예술가 28명이 참여하였습니다.

 

전시명: ablind 4th exhibition, 나의 모든 순간 Every moment of mine
전시장소: 서울특별시 용산구 양녕로 445 노들갤러리 2관
전시장은 배리어프리 접근에 용이하며 장애인 화장실이 구비되어 있습니다.

찾아 오시는 길은 노들역 2번 출구 또는 노들섬 버스 정류장입니다.

전시기간: 2024.09.04-2024.09.11 / 월요일 휴관
관람시간: 평일 11:00-19:00 / 주말 10:00-19:00 / 전시 마지막 날(11일)은 15시 마감
전시 셀러브레이션 파티: 9월 7일(토) 16시 / 아카펠라 그룹 ‘나린’ 축하 공연 및 작가와의 대화, 러키 드로우 등이 준비되어 있습니다.
전시문의: ablind@ablind.co.kr / 070-7954-2574 / @ablind_art


문화체육관광부, 한국장애인문화예술원, 낭독마을 책읽는 사람들, 나린, Seeterature, 왓어브레드, 봉스디
 

유의사항 안내
노들섬 내 주차장은 협소하여 상시 만차되며, 주차장 진입로 및 주변 교통이 매우 혼잡하여 주차에 많은 시간이 소요됩니다.
대중교통을 적극 이용해 주시기 바랍니다.
주차 및 교통난으로 인해 당일 관람이 불가하거나 관람을 포기한 경우, 예매 취소 및 환불, 변경을 불가합니다.
""")
                
                Spacer()
            }
            .padding()
        }
        .navigationTitle("전시정보")
    }
}

#Preview {
    ExhibitInfoView()
}
